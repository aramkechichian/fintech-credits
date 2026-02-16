import { useState, useEffect } from "react";
import { useTranslation } from "../i18n/I18nContext";
import testDataApi from "../api/testDataApi";
import Toast from "./ui/Toast";
import Button from "./ui/Button";

export default function TestModeModal({ isOpen, onClose }) {
  const { t } = useTranslation();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [toast, setToast] = useState({ isVisible: false, message: "", type: "success" });
  const [showConfirmGenerate, setShowConfirmGenerate] = useState(false);
  const [showConfirmClear, setShowConfirmClear] = useState(false);

  // Reset toast when modal closes
  useEffect(() => {
    if (!isOpen) {
      setToast({ isVisible: false, message: "", type: "success" });
      setShowConfirmGenerate(false);
      setShowConfirmClear(false);
    }
  }, [isOpen]);

  const handleGenerateClick = () => {
    setShowConfirmGenerate(true);
  };

  const handleGenerateConfirm = async () => {
    setShowConfirmGenerate(false);
    setIsGenerating(true);
    try {
      const result = await testDataApi.generateCreditRequests(50);
      const message = t("testMode.generateSuccess", { count: result.count }) ||
        `Se generaron ${result.count} solicitudes exitosamente`;
      setToast({
        isVisible: true,
        message: message,
        type: "success"
      });
      // Auto-hide toast after 3 seconds
      setTimeout(() => {
        setToast({ isVisible: false, message: "", type: "success" });
      }, 3000);
      // Close modal after 1.5 seconds
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error("Error generating credit requests:", error);
      const errorMessage = error.message ||
        t("testMode.generateError") ||
        "Error al generar solicitudes";
      setToast({
        isVisible: true,
        message: errorMessage,
        type: "error"
      });
      // Auto-hide error toast after 3 seconds
      setTimeout(() => {
        setToast({ isVisible: false, message: "", type: "success" });
      }, 3000);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClearClick = () => {
    setShowConfirmClear(true);
  };

  const handleClearConfirm = async () => {
    setShowConfirmClear(false);
    setIsClearing(true);
    try {
      const result = await testDataApi.clearCreditRequests();
      const message = t("testMode.clearSuccess", { count: result.deleted_count }) ||
        `Se eliminaron ${result.deleted_count} solicitudes exitosamente`;
      setToast({
        isVisible: true,
        message: message,
        type: "success"
      });
      // Auto-hide toast after 3 seconds
      setTimeout(() => {
        setToast({ isVisible: false, message: "", type: "success" });
      }, 3000);
      // Close modal after 1.5 seconds
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error("Error clearing credit requests:", error);
      const errorMessage = error.message ||
        t("testMode.clearError") ||
        "Error al limpiar solicitudes";
      setToast({
        isVisible: true,
        message: errorMessage,
        type: "error"
      });
      // Auto-hide error toast after 3 seconds
      setTimeout(() => {
        setToast({ isVisible: false, message: "", type: "success" });
      }, 3000);
    } finally {
      setIsClearing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Main Modal */}
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 max-w-md w-full mx-4">
          <h2 className="text-2xl font-bold mb-4 text-zinc-900 dark:text-zinc-50">
            {t("testMode.title")}
          </h2>

          <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <p className="text-sm text-yellow-800 dark:text-yellow-200">
              {t("testMode.description")}
            </p>
          </div>

          <div className="space-y-4">
            <button
              onClick={handleGenerateClick}
              disabled={isGenerating || isClearing || showConfirmGenerate || showConfirmClear}
              className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-400 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              {isGenerating
                ? t("testMode.generating") || "Generando..."
                : t("testMode.generateButton") || "Generar Solicitudes de Crédito"}
            </button>

            <button
              onClick={handleClearClick}
              disabled={isGenerating || isClearing || showConfirmGenerate || showConfirmClear}
              className="w-full px-4 py-3 bg-red-600 hover:bg-red-700 disabled:bg-zinc-400 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              {isClearing
                ? t("testMode.clearing") || "Limpiando..."
                : t("testMode.clearButton") || "Limpiar Solicitudes de Crédito"}
            </button>

            <button
              onClick={onClose}
              disabled={isGenerating || isClearing || showConfirmGenerate || showConfirmClear}
              className="w-full px-4 py-3 bg-zinc-200 dark:bg-zinc-700 hover:bg-zinc-300 dark:hover:bg-zinc-600 disabled:bg-zinc-400 disabled:cursor-not-allowed text-zinc-900 dark:text-zinc-50 rounded-lg font-medium transition-colors"
            >
              {t("creditRequest.cancel") || "Cancelar"}
            </button>
          </div>

          <Toast
            message={toast.message}
            type={toast.type}
            isVisible={toast.isVisible}
            onClose={() => setToast({ ...toast, isVisible: false })}
          />
        </div>
      </div>

      {/* Confirm Generate Modal */}
      {showConfirmGenerate && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-[60]">
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4 text-zinc-900 dark:text-zinc-50">
              {t("testMode.confirmTitle") || "Confirmar"}
            </h3>
            <p className="mb-6 text-zinc-700 dark:text-zinc-300">
              {t("testMode.confirmGenerate")}
            </p>
            <div className="flex gap-3">
              <Button
                onClick={handleGenerateConfirm}
                disabled={isGenerating}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
              >
                {t("testMode.confirm") || "Confirmar"}
              </Button>
              <Button
                onClick={() => setShowConfirmGenerate(false)}
                variant="secondary"
                className="flex-1"
                disabled={isGenerating}
              >
                {t("testMode.cancel") || "Cancelar"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Confirm Clear Modal */}
      {showConfirmClear && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-[60]">
          <div className="bg-white dark:bg-zinc-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4 text-zinc-900 dark:text-zinc-50">
              {t("testMode.confirmTitle") || "Confirmar"}
            </h3>
            <p className="mb-6 text-zinc-700 dark:text-zinc-300">
              {t("testMode.confirmClear")}
            </p>
            <div className="flex gap-3">
              <Button
                onClick={handleClearConfirm}
                disabled={isClearing}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white"
              >
                {t("testMode.confirm") || "Confirmar"}
              </Button>
              <Button
                onClick={() => setShowConfirmClear(false)}
                variant="secondary"
                className="flex-1"
                disabled={isClearing}
              >
                {t("testMode.cancel") || "Cancelar"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
