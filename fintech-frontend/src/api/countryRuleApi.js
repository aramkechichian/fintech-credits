/**
 * API client for country rules endpoints
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const countryRuleApi = {
  /**
   * Get all country rules with pagination
   */
  async getAll(skip = 0, limit = 100, isActive = null) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    let url = `${API_BASE_URL}/country-rules?skip=${skip}&limit=${limit}`;
    if (isActive !== null) {
      url += `&is_active=${isActive}`;
    }

    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      const error = await response.json().catch(() => ({ detail: "Error al obtener las reglas de países" }));
      throw new Error(error.detail || "Error al obtener las reglas de países");
    }

    return await response.json();
  },

  /**
   * Get a country rule by ID
   */
  async getById(ruleId) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/country-rules/${ruleId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      const error = await response.json().catch(() => ({ detail: "Error al obtener la regla de país" }));
      throw new Error(error.detail || "Error al obtener la regla de país");
    }

    return await response.json();
  },

  /**
   * Get country rule by country code
   */
  async getByCountry(country) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/country-rules/country/${country}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      const error = await response.json().catch(() => ({ detail: "Error al obtener la regla de país" }));
      throw new Error(error.detail || "Error al obtener la regla de país");
    }

    return await response.json();
  },

  /**
   * Create a new country rule
   */
  async create(ruleData) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/country-rules`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(ruleData),
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      const error = await response.json().catch(() => ({ detail: "Error al crear la regla de país" }));
      throw new Error(error.detail || "Error al crear la regla de país");
    }

    return await response.json();
  },

  /**
   * Update a country rule
   */
  async update(ruleId, updateData) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/country-rules/${ruleId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify(updateData),
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      const error = await response.json().catch(() => ({ detail: "Error al actualizar la regla de país" }));
      throw new Error(error.detail || "Error al actualizar la regla de país");
    }

    return await response.json();
  },

  /**
   * Delete a country rule (soft delete)
   */
  async delete(ruleId) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/country-rules/${ruleId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      const error = await response.json().catch(() => ({ detail: "Error al eliminar la regla de país" }));
      throw new Error(error.detail || "Error al eliminar la regla de país");
    }

    return true;
  },
};
