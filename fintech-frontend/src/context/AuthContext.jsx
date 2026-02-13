import { createContext, useContext, useState, useEffect } from "react";
import { authApi } from "../api/authApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);

  const loadUser = async () => {
    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error("Error loading user:", error);
      setUser(null);
    }
  };

  useEffect(() => {
    // Check if user is authenticated on mount
    const authenticated = authApi.isAuthenticated();
    setIsAuthenticated(authenticated);
    
    // Load user data if authenticated
    if (authenticated) {
      loadUser();
    }
    
    setIsLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      await authApi.login(email, password);
      setIsAuthenticated(true);
      // Load user data after login
      await loadUser();
      return true;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    authApi.logout();
    setIsAuthenticated(false);
    setUser(null);
    // Redirect to login page
    window.location.reload();
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
