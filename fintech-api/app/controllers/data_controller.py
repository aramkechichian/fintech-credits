"""
Data export controller
Handles Excel export endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging
from datetime import datetime

from app.models.user import UserInDB
from app.services.data_service import export_credit_requests_to_excel, get_available_fields
from app.controllers.auth_controller import get_current_user_dependency

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["data"])


@router.get(
    "/export/fields",
    summary="Get available fields for export",
    description="Returns a list of all available fields that can be exported in the Excel file, along with their display labels.",
    responses={
        200: {"description": "List of available fields retrieved successfully"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        500: {"description": "Internal server error"}
    }
)
async def get_export_fields(
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get available fields for export"""
    try:
        fields = get_available_fields()
        return {
            "fields": fields,
            "field_names": list(fields.keys())
        }
    except Exception as e:
        logger.error(f"Error getting export fields: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving export fields"
        )


@router.get(
    "/export/excel",
    summary="Export credit requests to Excel",
    description="Exports credit requests to an Excel file based on filters and selected fields. The file can be downloaded with all matching requests based on the provided filters.",
    responses={
        200: {
            "description": "Excel file generated successfully",
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            }
        },
        400: {"description": "Invalid request - no valid fields selected or invalid filters"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        500: {"description": "Internal server error"}
    }
)
async def export_to_excel(
    current_user: UserInDB = Depends(get_current_user_dependency),
    countries: Optional[List[str]] = Query(None, description="Filter by countries"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    request_date_from: Optional[str] = Query(None, description="Filter by request date from (YYYY-MM-DD)"),
    request_date_to: Optional[str] = Query(None, description="Filter by request date to (YYYY-MM-DD)"),
    fields: Optional[List[str]] = Query(None, description="Fields to include in export (comma-separated or multiple query params)")
):
    """
    Export credit requests to Excel
    
    Query parameters:
    - countries: Filter by countries (can be multiple)
    - status: Filter by status
    - request_date_from: Filter by request date from (YYYY-MM-DD)
    - request_date_to: Filter by request date to (YYYY-MM-DD)
    - fields: Fields to include (can be multiple query params or comma-separated)
    """
    try:
        # Parse fields - handle both comma-separated and multiple params
        selected_fields = []
        if fields:
            for field_param in fields:
                # Split by comma if comma-separated
                if ',' in field_param:
                    selected_fields.extend([f.strip() for f in field_param.split(',')])
                else:
                    selected_fields.append(field_param.strip())
        
        # Remove duplicates and empty strings
        selected_fields = list(set([f for f in selected_fields if f]))
        
        # Parse date filters
        parsed_date_from = None
        parsed_date_to = None
        if request_date_from:
            try:
                parsed_date_from = datetime.strptime(request_date_from, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request_date_from format. Use YYYY-MM-DD"
                )
        if request_date_to:
            try:
                parsed_date_to = datetime.strptime(request_date_to, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request_date_to format. Use YYYY-MM-DD"
                )
        
        logger.info(f"Exporting data with filters: countries={countries}, status={status_filter}, request_date_from={request_date_from}, request_date_to={request_date_to}, fields={selected_fields}")
        
        # Generate Excel file
        excel_file = await export_credit_requests_to_excel(
            countries=countries,
            status=status_filter,
            request_date_from=parsed_date_from,
            request_date_to=parsed_date_to,
            selected_fields=selected_fields if selected_fields else None
        )
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"solicitudes_credito_{timestamp}.xlsx"
        
        # Return as streaming response
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except ValueError as e:
        error_message = str(e)
        logger.warning(f"Validation error exporting data: {error_message}")
        # Check if it's a "no data" error
        if "No data found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except Exception as e:
        logger.error(f"Error exporting data to Excel: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting data to Excel"
        )
