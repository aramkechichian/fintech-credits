// ==============================
// API Client for Data Export
// Backend: localhost:8000
// =============================

const API_BASE_URL = "http://localhost:8000";

export const dataApi = {
  /**
   * Get available fields for export
   */
  async getAvailableFields() {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/data/export/fields`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        throw new Error("Session expired. Please log in again.");
      }
      const error = await response.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  /**
   * Export credit requests to Excel
   */
  async exportToExcel(filters = {}, selectedFields = []) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    // Build query params
    const params = new URLSearchParams();
    
    if (filters.countries && filters.countries.length > 0) {
      filters.countries.forEach((country) => {
        params.append("countries", country);
      });
    }
    
    if (filters.request_date_from) {
      params.append("request_date_from", filters.request_date_from);
    }
    
    if (filters.request_date_to) {
      params.append("request_date_to", filters.request_date_to);
    }
    
    if (filters.status) {
      params.append("status", filters.status);
    }
    
    // Add fields as multiple query params
    if (selectedFields && selectedFields.length > 0) {
      selectedFields.forEach((field) => {
        params.append("fields", field);
      });
    }

    const url = `${API_BASE_URL}/data/export/excel?${params.toString()}`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        throw new Error("Session expired. Please log in again.");
      }
      // Handle 404 (no data found) specially
      if (response.status === 404) {
        const error = await response.json().catch(() => ({ detail: "No data found" }));
        throw new Error(error.detail || "No data found matching the selected filters");
      }
      const error = await response.text();
      throw new Error(error || `HTTP error! status: ${response.status}`);
    }

    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get("Content-Disposition");
    let filename = "solicitudes_credito.xlsx";
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
      if (filenameMatch) {
        filename = filenameMatch[1];
      }
    }

    // Convert response to blob and download
    const blob = await response.blob();
    const url_blob = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url_blob;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url_blob);
    document.body.removeChild(a);

    return { success: true, filename };
  },
};
