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
      // Handle 401 (unauthorized) - token expired or invalid
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      
      const errorText = await response.text();
      let error;
      try {
        error = JSON.parse(errorText);
      } catch {
        error = { detail: errorText || "Error al crear la solicitud de crédito" };
      }
      
      // Handle validation errors
      if (response.status === 422 && error.detail) {
        let errorMessage = "Error de validación: ";
        if (Array.isArray(error.detail)) {
          const errors = error.detail.map((e) => {
            const field = e.loc ? e.loc.join(".") : "campo";
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
      
      // Return generic error message instead of technical details
      throw new Error(error.detail && !error.detail.includes("Could not validate") 
        ? error.detail 
        : "Error al crear la solicitud de crédito");
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
      // Handle 401 (unauthorized) - token expired or invalid
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      
      const error = await response.json().catch(() => ({ detail: "Error al obtener solicitudes de crédito" }));
      throw new Error(error.detail && !error.detail.includes("Could not validate")
        ? error.detail 
        : "Error al obtener solicitudes de crédito");
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
      // Handle 401 (unauthorized) - token expired or invalid
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      
      const error = await response.json().catch(() => ({ detail: "Error al obtener la solicitud de crédito" }));
      throw new Error(error.detail && !error.detail.includes("Could not validate")
        ? error.detail 
        : "Error al obtener la solicitud de crédito");
    }

    return await response.json();
  },

  /**
   * Search credit requests with filters and pagination
   */
  async search(searchParams) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const queryString = searchParams.toString();
    const response = await fetch(
      `${API_BASE_URL}/credit-requests/search?${queryString}`,
      {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      // Handle 401 (unauthorized) - token expired or invalid
      if (response.status === 401) {
        // Clear token and redirect to login
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      
      const error = await response.json().catch(() => ({
        detail: "Error al buscar solicitudes de crédito",
      }));
      
      // Return generic error message instead of technical details
      throw new Error(error.detail && !error.detail.includes("Could not validate") 
        ? error.detail 
        : "Error al buscar solicitudes de crédito");
    }

    return await response.json();
  },

  /**
   * Update a credit request (status and/or bank information)
   */
  async update(requestId, updateData) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/credit-requests/${requestId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(updateData),
    });

    if (!response.ok) {
      // Handle 401 (unauthorized) - token expired or invalid
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      
      const error = await response.json().catch(() => ({ detail: "Error al actualizar la solicitud de crédito" }));
      throw new Error(error.detail && !error.detail.includes("Could not validate")
        ? error.detail 
        : "Error al actualizar la solicitud de crédito");
    }

    const data = await response.json();
    return data;
  },
};
