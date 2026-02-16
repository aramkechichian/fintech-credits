// ==============================
// API Client for Bank Provider
// Backend: localhost:8000
// =============================

const API_BASE_URL = "http://localhost:8000";

export const bankProviderApi = {
  /**
   * Get bank information from provider
   * @param {string} country - Country code
   * @param {string} fullName - Full name of the person
   * @param {string} identityDocument - Identity document number
   * @returns {Promise<Object>} Bank information response
   */
  async getBankInformation(country, fullName, identityDocument) {
    const token = localStorage.getItem("access_token");
    if (!token) {
      throw new Error("You must be logged in");
    }

    const params = new URLSearchParams({
      country: country,
      full_name: fullName,
      identity_document: identityDocument,
    });

    const response = await fetch(
      `${API_BASE_URL}/bank-provider/information?${params.toString()}`,
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
        localStorage.removeItem("access_token");
        throw new Error("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.");
      }
      
      const error = await response.json().catch(() => ({ 
        detail: "Error al obtener información bancaria" 
      }));
      throw new Error(error.detail || "Error al obtener información bancaria");
    }

    return await response.json();
  },
};
