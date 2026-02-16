// ==============================
// API Client for Test Data
// Backend: localhost:8000
// =============================

const API_BASE_URL = "http://localhost:8000";

export const testDataApi = {
  /**
   * Generate random credit requests for testing
   * @param {number} count - Number of requests to generate (default: 50)
   * @returns {Promise<Object>} Response with message and count
   */
  async generateCreditRequests(count = 50) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const params = new URLSearchParams();
    params.append("count", count.toString());

    const response = await fetch(`${API_BASE_URL}/test-data/credit-requests/generate?${params.toString()}`, {
      method: "POST",
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
      const error = await response.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  /**
   * Clear all credit requests from the database
   * @returns {Promise<Object>} Response with message and deleted_count
   */
  async clearCreditRequests() {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const response = await fetch(`${API_BASE_URL}/test-data/credit-requests/clear`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      const error = await response.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },
};

export default testDataApi;
