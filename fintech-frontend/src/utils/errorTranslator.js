/**
 * Translates error messages to the current language
 * Maps common error messages to translation keys
 */
export function translateError(errorMessage, t) {
  if (!errorMessage || !t) return errorMessage;

  // Map common error messages to translation keys
  const errorMap = {
    "You must be logged in": "errors.mustBeLoggedIn",
    "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.": "errors.sessionExpired",
    "Error al crear la solicitud de crédito": "creditRequest.errors.createFailed",
    "Error al obtener solicitudes de crédito": "creditRequest.errors.getAllFailed",
    "Error al obtener la solicitud de crédito": "creditRequest.errors.getByIdFailed",
    "Error al buscar solicitudes de crédito": "creditRequest.errors.searchFailed",
    "Error retrieving credit request": "creditRequest.errors.getByIdFailed",
    "Error getting credit requests": "creditRequest.errors.getAllFailed",
    "Error searching credit requests": "creditRequest.errors.searchFailed",
    "Error creating credit request": "creditRequest.errors.createFailed",
    "Could not validate credentials": "errors.sessionExpired",
    "User not found": "errors.userNotFound",
    "Incorrect email or password": "login.error",
    "Error registering user": "register.error",
    "Error getting user": "errors.getUserFailed",
    "Error al obtener información del usuario": "errors.getUserFailed",
  };

  // Check if error message matches a key in the map
  const translationKey = errorMap[errorMessage];
  if (translationKey) {
    const translated = t(translationKey);
    // If translation exists and is different from the key, return it
    if (translated && translated !== translationKey) {
      return translated;
    }
  }

  // Check if error message contains any of the mapped strings
  for (const [key, value] of Object.entries(errorMap)) {
    if (errorMessage.includes(key)) {
      const translated = t(value);
      if (translated && translated !== value) {
        return translated;
      }
    }
  }

  // Return original message if no translation found
  return errorMessage;
}
