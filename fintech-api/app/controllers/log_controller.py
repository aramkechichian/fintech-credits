"""
Log controller
Handles log querying and export endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging
from datetime import datetime

from app.models.user import UserInDB
from app.models.log_data import LogDataInDB
from app.services.log_service import search_logs
from app.services.log_export_service import export_logs_to_excel, get_available_fields
from app.controllers.auth_controller import get_current_user_dependency
from app.utils.endpoint_mapper import get_module_name_for_endpoint, LOGGED_MODULES, get_endpoints_for_module

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get(
    "/modules",
    summary="Get available modules for filtering",
    description="Returns a list of all modules that are logged in the system. These can be used to filter logs by module.",
    responses={
        200: {"description": "List of modules retrieved successfully"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        500: {"description": "Internal server error"}
    }
)
async def get_available_modules(
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get available modules for filtering logs"""
    try:
        return {
            "modules": LOGGED_MODULES
        }
    except Exception as e:
        logger.error(f"Error getting available modules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving available modules"
        )


@router.get(
    "/search",
    summary="Search logs with filters",
    description="Searches logs with optional filters (method, endpoint, date range) and pagination. Returns a paginated response with items, total count, page number, and total pages.",
    responses={
        200: {"description": "Search results retrieved successfully"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        500: {"description": "Internal server error"}
    }
)
async def search_logs_endpoint(
    current_user: UserInDB = Depends(get_current_user_dependency),
    method: Optional[str] = Query(None, description="Filter by HTTP method (GET, POST, PUT, DELETE, etc.)"),
    module: Optional[str] = Query(None, description="Filter by module (e.g., creditRequests, countryRules)"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint (partial match)"),
    date_from: Optional[str] = Query(None, description="Filter by date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Search logs with filters and pagination"""
    try:
        skip = (page - 1) * limit
        
        # If module is provided, convert it to endpoint filter
        # We'll search for any endpoint that starts with the module's endpoints
        endpoint_filter = endpoint
        if module:
            module_endpoints = get_endpoints_for_module(module)
            if module_endpoints:
                # Use all module endpoints for filtering (will match any endpoint starting with these)
                endpoint_filter = module_endpoints if not endpoint else endpoint
            else:
                # Invalid module, return empty results
                return {
                    "items": [],
                    "total": 0,
                    "page": page,
                    "limit": limit,
                    "total_pages": 0
                }
        
        # Parse date filters
        parsed_date_from = None
        parsed_date_to = None
        if date_from:
            try:
                parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use YYYY-MM-DD"
                )
        if date_to:
            try:
                parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use YYYY-MM-DD"
                )
        
        logs, total_count = await search_logs(
            method=method,
            endpoint=endpoint_filter,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            skip=skip,
            limit=limit
        )
        
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return {
            "items": [
                {
                    "id": str(log.id),
                    "endpoint": log.endpoint,
                    "module": get_module_name_for_endpoint(log.endpoint),
                    "method": log.method,
                    "user_id": str(log.user_id) if log.user_id else None,
                    "response_status": log.response_status,
                    "is_success": log.is_success,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat() if log.created_at else None
                }
                for log in logs
            ],
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching logs"
        )


@router.get(
    "/export/fields",
    summary="Get available fields for log export",
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
    """Get available fields for log export"""
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
    summary="Export logs to Excel",
    description="Exports logs to an Excel file based on filters and selected fields. The file can be downloaded with all matching logs based on the provided filters.",
    responses={
        200: {
            "description": "Excel file generated successfully",
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}
            }
        },
        400: {"description": "Invalid request - no valid fields selected or invalid filters"},
        401: {"description": "Unauthorized - invalid or missing authentication token"},
        404: {"description": "No data found matching the selected filters"},
        500: {"description": "Internal server error"}
    }
)
async def export_to_excel(
    current_user: UserInDB = Depends(get_current_user_dependency),
    method: Optional[str] = Query(None, description="Filter by HTTP method"),
    module: Optional[str] = Query(None, description="Filter by module (e.g., creditRequests, countryRules)"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint (partial match)"),
    date_from: Optional[str] = Query(None, description="Filter by date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    fields: Optional[List[str]] = Query(None, description="Fields to include in export (comma-separated or multiple query params)")
):
    """
    Export logs to Excel
    
    Query parameters:
    - method: Filter by HTTP method
    - module: Filter by module (e.g., creditRequests, countryRules)
    - endpoint: Filter by endpoint (partial match)
    - date_from: Filter by date from (YYYY-MM-DD)
    - date_to: Filter by date to (YYYY-MM-DD)
    - fields: Fields to include (can be multiple query params or comma-separated)
    """
    try:
        # If module is provided, convert it to endpoint filter
        endpoint_filter = endpoint
        if module:
            module_endpoints = get_endpoints_for_module(module)
            if module_endpoints:
                endpoint_filter = module_endpoints[0] if not endpoint else endpoint
            else:
                # Invalid module, return 404
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No data found matching the selected filters"
                )
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
        if date_from:
            try:
                parsed_date_from = datetime.strptime(date_from, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_from format. Use YYYY-MM-DD"
                )
        if date_to:
            try:
                parsed_date_to = datetime.strptime(date_to, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date_to format. Use YYYY-MM-DD"
                )
        
        logger.info(f"Exporting logs with filters: method={method}, module={module}, endpoint={endpoint_filter}, date_from={date_from}, date_to={date_to}, fields={selected_fields}")
        
        # Generate Excel file
        excel_file = await export_logs_to_excel(
            method=method,
            endpoint=endpoint_filter,
            date_from=parsed_date_from,
            date_to=parsed_date_to,
            selected_fields=selected_fields if selected_fields else None
        )
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"logs_{timestamp}.xlsx"
        
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
        logger.warning(f"Validation error exporting logs: {error_message}")
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
        logger.error(f"Error exporting logs to Excel: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting logs to Excel"
        )
