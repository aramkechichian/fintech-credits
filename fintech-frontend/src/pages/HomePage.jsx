import { useState } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { useAuth } from "../context/AuthContext";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import CreateCreditRequestModal from "../components/CreateCreditRequestModal";
import SearchCreditRequestsModal from "../components/SearchCreditRequestsModal";
import LogsModal from "../components/LogsModal";
import Toast from "../components/ui/Toast";

export default function HomePage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [isLogsModalOpen, setIsLogsModalOpen] = useState(false);
  const [toast, setToast] = useState({ isVisible: false, message: "", type: "success" });

  const handleCreateCreditRequest = () => {
    setIsCreateModalOpen(true);
  };

  const handleSearchCreditRequests = () => {
    setIsSearchModalOpen(true);
  };

  const handleCreateModalClose = () => {
    setIsCreateModalOpen(false);
  };

  const handleSearchModalClose = () => {
    setIsSearchModalOpen(false);
  };

  const handleSuccess = () => {
    setIsCreateModalOpen(false);
    setToast({
      isVisible: true,
      message: t("creditRequest.successMessage"),
      type: "success",
    });
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 text-zinc-900 dark:text-zinc-50">
          {t("home.welcome")}, {user?.full_name || ""}
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          {t("home.description")}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-blue-600 dark:text-blue-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-zinc-50">
              {t("home.createCreditRequest")}
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
              {t("home.startNewRequest")}
            </p>
            <Button 
              className="w-full"
              onClick={handleCreateCreditRequest}
            >
              {t("home.createCreditRequest")}
            </Button>
          </div>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-green-600 dark:text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-zinc-50">
              {t("home.searchCreditRequests")}
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
              {t("home.searchDescription")}
            </p>
            <Button 
              className="w-full"
              onClick={handleSearchCreditRequests}
            >
              {t("home.searchCreditRequests")}
            </Button>
          </div>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-purple-600 dark:text-purple-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-zinc-50">
              {t("home.audits")}
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
              {t("home.auditsDescription")}
            </p>
            <Button 
              className="w-full"
              onClick={() => {
                window.history.pushState({ route: "audits" }, "", "/audits");
                window.dispatchEvent(new Event("locationchange"));
              }}
            >
              {t("home.audits")}
            </Button>
          </div>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-orange-600 dark:text-orange-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-zinc-50">
              {t("home.logs")}
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
              {t("home.logsDescription")}
            </p>
            <Button 
              className="w-full"
              onClick={() => setIsLogsModalOpen(true)}
            >
              {t("home.logs")}
            </Button>
          </div>
        </Card>
      </div>

      <CreateCreditRequestModal
        isOpen={isCreateModalOpen}
        onClose={handleCreateModalClose}
        onSuccess={handleSuccess}
      />

      <SearchCreditRequestsModal
        isOpen={isSearchModalOpen}
        onClose={handleSearchModalClose}
      />

      <LogsModal
        isOpen={isLogsModalOpen}
        onClose={() => setIsLogsModalOpen(false)}
      />

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={() => setToast({ ...toast, isVisible: false })}
      />
    </div>
  );
}
