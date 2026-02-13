// ==============================
// API Client for Credit Requests
// Backend: localhost:8000
// =============================

const API_BASE_URL = "http://localhost:8000";

export const creditRequestApi = {
  /**
   * Create a new credit request
   */
  async create(creditRequestData) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/credit-requests`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(creditRequestData),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let error;
      try {
        error = JSON.parse(errorText);
      } catch {
        error = { detail: errorText || "Error creating credit request" };
      }
      
      // Handle validation errors
      if (response.status === 422 && error.detail) {
        let errorMessage = "Validation error: ";
        if (Array.isArray(error.detail)) {
          const errors = error.detail.map((e) => {
            const field = e.loc ? e.loc.join(".") : "field";
            return `${field}: ${e.msg}`;
          }).join(", ");
          errorMessage += errors;
        } else if (typeof error.detail === "string") {
          errorMessage += error.detail;
        } else {
          errorMessage += JSON.stringify(error.detail);
        }
        throw new Error(errorMessage);
      }
      
      throw new Error(error.detail || "Error creating credit request");
    }

    return await response.json();
  },

  /**
   * Get all credit requests for the current user
   */
  async getAll() {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/credit-requests`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Error getting credit requests" }));
      throw new Error(error.detail || "Error getting credit requests");
    }

    return await response.json();
  },

  /**
   * Get a specific credit request by ID
   */
  async getById(requestId) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/credit-requests/${requestId}`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Error getting credit request" }));
      throw new Error(error.detail || "Error getting credit request");
    }

    return await response.json();
  },
};
