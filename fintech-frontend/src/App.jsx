import { useMemo, useState, useEffect } from "react";
import { I18nProvider, useTranslation } from "./i18n/I18nContext";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import HomePage from "./pages/HomePage";
import CreditRequestsListPage from "./pages/CreditRequestsListPage";
import CountryRulesPage from "./pages/CountryRulesPage";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  const { t } = useTranslation();
  const [route, setRoute] = useState(() => {
    if (typeof window !== "undefined") {
      const path = window.location.pathname;
      if (path.startsWith("/credit-requests/search")) return "search";
      if (path === "/country-rules") return "country-rules";
      if (path === "/" || path === "/home") return "home";
    }
    return isAuthenticated ? "home" : "login";
  });

  const handleNavigate = (nextRoute) => {
    // Update browser URL first
    if (nextRoute === "home") {
      window.history.pushState({ route: nextRoute }, "", "/");
    } else if (nextRoute === "country-rules") {
      window.history.pushState({ route: nextRoute }, "", "/country-rules");
    } else if (nextRoute === "search") {
      window.history.pushState({ route: nextRoute }, "", "/credit-requests/search");
    }
    
    // Update route state
    setRoute(nextRoute);
  };

  // Update route when authentication state changes
  useEffect(() => {
    if (isAuthenticated && (route === "login" || route === "register")) {
      setRoute("home");
    } else if (!isAuthenticated && route !== "login" && route !== "register") {
      setRoute("login");
    }
  }, [isAuthenticated, route]);

  // Handle browser navigation (back/forward buttons)
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path.startsWith("/credit-requests/search")) {
        setRoute("search");
      } else if (path === "/country-rules") {
        setRoute("country-rules");
      } else if (path === "/" || path === "/home") {
        setRoute("home");
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  // Sync route with URL changes (for programmatic navigation)
  useEffect(() => {
    const updateRouteFromUrl = () => {
      const path = window.location.pathname;
      let newRoute = null;
      
      if (path.startsWith("/credit-requests/search")) {
        newRoute = "search";
      } else if (path === "/country-rules") {
        newRoute = "country-rules";
      } else if (path === "/" || path === "/home") {
        newRoute = "home";
      }
      
      // Update route if we determined a new route from URL
      if (newRoute) {
        setRoute((currentRoute) => {
          // Only update if actually different
          return currentRoute !== newRoute ? newRoute : currentRoute;
        });
      }
    };

    // Listen for custom locationchange event
    window.addEventListener("locationchange", updateRouteFromUrl);
    
    // Also check on mount
    updateRouteFromUrl();
    
    return () => {
      window.removeEventListener("locationchange", updateRouteFromUrl);
    };
  }, []); // Empty deps - only run on mount and when locationchange event fires

  const Page = useMemo(() => {
    if (!isAuthenticated) {
      if (route === "register") {
        return <RegisterPage onNavigate={handleNavigate} />;
      }
      return <LoginPage onNavigate={handleNavigate} />;
    }

    if (route === "search") {
      return <CreditRequestsListPage />;
    }

    if (route === "country-rules") {
      return <CountryRulesPage />;
    }

    if (route === "home") return <HomePage />;
    
    return <HomePage />;
  }, [route, isAuthenticated]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-zinc-100 dark:bg-zinc-950 flex items-center justify-center">
        <div className="text-zinc-600 dark:text-zinc-400">{t("common.loading")}</div>
      </div>
    );
  }

  // Show login page without layout
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-zinc-100 dark:bg-zinc-950">
        {Page}
      </div>
    );
  }

  // Show main app
  return (
    <div className="min-h-screen bg-zinc-100 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-50">
      <Header />
      <div className="flex">
        <Sidebar currentRoute={route} onNavigate={handleNavigate} />
        <main className="flex-1 ml-64 px-8 py-8 max-w-full">
          {Page}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </I18nProvider>
  );
}
