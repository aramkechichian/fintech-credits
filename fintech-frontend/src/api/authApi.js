// ==============================
// API Client for Authentication
// Backend: localhost:8000
// =============================

const API_BASE_URL = "http://localhost:8000";

export const authApi = {
  /**
   * Register a new user
   */
  async register(fullName, email, password) {
    const url = `${API_BASE_URL}/auth/register`;
    const requestBody = { full_name: fullName, email, password };
    
    console.log("[authApi] Register request:", {
      url,
      method: "POST",
      body: { ...requestBody, password: "***" }, // Don't log password
    });

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      console.log("[authApi] Register response:", {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries()),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("[authApi] Register error response:", errorText);
        let error;
        try {
          error = JSON.parse(errorText);
        } catch {
          error = { detail: errorText || "Error registering user" };
        }
        
        // Handle validation errors (422)
        if (response.status === 422 && error.detail) {
          let errorMessage = "Error de validación: ";
          if (Array.isArray(error.detail)) {
            const errors = error.detail.map(e => {
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
        
        throw new Error(error.detail || "Error registering user");
      }

      const data = await response.json();
      console.log("[authApi] Register success:", { email: data.email, id: data.id });
      return data;
    } catch (error) {
      console.error("[authApi] Register exception:", {
        name: error.name,
        message: error.message,
        stack: error.stack,
      });
      
      // Handle network errors
      if (error instanceof TypeError && error.message === "Failed to fetch") {
        console.error("[authApi] Network error - server may not be running at:", API_BASE_URL);
        throw new Error("No se pudo conectar con el servidor. Por favor, verifica que el servidor esté corriendo.");
      }
      throw error;
    }
  },

  /**
   * Login user
   */
  async login(email, password) {
    const url = `${API_BASE_URL}/auth/login`;
    console.log("[authApi] Login request:", { url, method: "POST", email });

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      console.log("[authApi] Login response:", {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Error logging in" }));
        console.error("[authApi] Login error:", error);
        throw new Error(error.detail || "Error logging in");
      }

      const data = await response.json();
      console.log("[authApi] Login success");
      // Store token in localStorage
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
        if (data.refresh_token) {
          localStorage.setItem("refresh_token", data.refresh_token);
        }
      }
      return data;
    } catch (error) {
      console.error("[authApi] Login exception:", {
        name: error.name,
        message: error.message,
      });
      // Handle network errors
      if (error instanceof TypeError && error.message === "Failed to fetch") {
        throw new Error("No se pudo conectar con el servidor. Por favor, verifica que el servidor esté corriendo.");
      }
      throw error;
    }
  },

  /**
   * Get stored access token (synchronous)
   */
  getToken() {
    return localStorage.getItem("access_token");
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!localStorage.getItem("access_token");
  },

  /**
   * Logout user
   */
  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  /**
   * Get current user information
   */
  async getCurrentUser() {
    const token = this.getToken();
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Error getting user" }));
      throw new Error(error.detail || error.message || "Error getting user");
    }

    return await response.json();
  },
};
