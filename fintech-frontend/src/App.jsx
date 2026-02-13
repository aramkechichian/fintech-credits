import { useMemo, useState, useEffect } from "react";
import { I18nProvider, useTranslation } from "./i18n/I18nContext";
import { AuthProvider, useAuth } from "./context/AuthContext";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import HomePage from "./pages/HomePage";
import CreditRequestsListPage from "./pages/CreditRequestsListPage";
import Header from "./components/Header";

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  const { t } = useTranslation();
  const [route, setRoute] = useState(() => {
    if (typeof window !== "undefined") {
      const path = window.location.pathname;
      if (path.startsWith("/credit-requests/search")) return "search";
      if (path === "/" || path === "/home") return "home";
    }
    return isAuthenticated ? "home" : "login";
  });

  const handleNavigate = (nextRoute) => {
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

  // Handle browser navigation
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path.startsWith("/credit-requests/search")) {
        setRoute("search");
      } else if (path === "/" || path === "/home") {
        setRoute("home");
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const Page = useMemo(() => {
    if (!isAuthenticated) {
      if (route === "register") {
        return <RegisterPage onNavigate={handleNavigate} />;
      }
      return <LoginPage onNavigate={handleNavigate} />;
    }

    if (route === "search" || window.location.pathname.startsWith("/credit-requests/search")) {
      return <CreditRequestsListPage />;
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
      <main className="mx-auto w-full max-w-6xl px-6 py-6">
        {Page}
      </main>
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
