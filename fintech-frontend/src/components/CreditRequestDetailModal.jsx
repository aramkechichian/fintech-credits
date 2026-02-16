import { useState, useEffect } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { creditRequestApi } from "../api/creditRequestApi";
import { translateError } from "../utils/errorTranslator";
import Modal from "./ui/Modal";
import Button from "./ui/Button";
import Spinner from "./ui/Spinner";
import Toast from "./ui/Toast";

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  in_review: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  approved: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  cancelled: "bg-zinc-100 text-zinc-800 dark:bg-zinc-900/30 dark:text-zinc-400",
};

export default function CreditRequestDetailModal({ isOpen, onClose, requestId, onUpdate }) {
  const { t } = useTranslation();
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState({ isVisible: false, message: "", type: "success" });

  useEffect(() => {
    if (isOpen && requestId) {
      loadRequest();
    }
  }, [isOpen, requestId]);

  const loadRequest = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await creditRequestApi.getById(requestId);
      setRequest(data);
    } catch (err) {
      const errorMessage = translateError(err.message, t);
      setError(errorMessage || t("creditRequest.errors.getByIdFailed"));
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    if (!request) return;

    setUpdating(true);
    setError("");

    try {
      const response = await creditRequestApi.update(requestId, {
        status: newStatus,
      });

      // Handle response - it can be the request object or an object with message and data
      const updatedRequest = response.data || response;
      // Use message from backend if available, otherwise use translation
      const message = response.message || t(`creditRequest.statusUpdate.${newStatus}`);

      setRequest(updatedRequest);
      
      // Show notification message based on status
      let toastMessage = message;
      if (newStatus === "in_review") {
        toastMessage = t("creditRequest.statusUpdate.inReviewNotification");
      }
      
      setToast({
        isVisible: true,
        message: toastMessage,
        type: "success",
      });

      if (onUpdate) {
        onUpdate(updatedRequest);
      }

      // Close modal after a short delay (only for approve/reject, not for in_review)
      if (newStatus === "approved" || newStatus === "rejected") {
        setTimeout(() => {
          onClose();
        }, 1500);
      }
    } catch (err) {
      const errorMessage = translateError(err.message, t);
      setError(errorMessage || t("creditRequest.errors.updateFailed"));
    } finally {
      setUpdating(false);
    }
  };

  const formatCurrency = (amount, currencyCode) => {
    return new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: currencyCode,
    }).format(amount);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("es-ES", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  const canApprove = request?.status === "pending" || request?.status === "in_review";
  const canReject = request?.status === "pending" || request?.status === "in_review";
  const canPutInReview = request?.status === "pending";

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title={t("creditRequest.detailTitle")}
        size="lg"
      >
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <Spinner />
          </div>
        ) : error ? (
          <div className="p-4 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">
            {error}
          </div>
        ) : request ? (
          <div className="space-y-6">
            {/* Status Badge */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
                {t("creditRequest.status._label")}:
              </span>
              <span
                className={`px-3 py-1 text-sm font-medium rounded-full ${
                  STATUS_COLORS[request.status] || STATUS_COLORS.pending
                }`}
              >
                {t(`creditRequest.status.${request.status}`) || request.status}
              </span>
            </div>

            {/* Request Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-1">
                  {t("creditRequest.country")}
                </label>
                <p className="text-zinc-900 dark:text-zinc-50">{request.country}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-1">
                  {t("creditRequest.fullName")}
                </label>
                <p className="text-zinc-900 dark:text-zinc-50">{request.full_name}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-1">
                  {t("creditRequest.email")}
                </label>
                <p className="text-zinc-900 dark:text-zinc-50">{request.email}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-1">
                  {t("creditRequest.identityDocument")}
                </label>
                <p className="text-zinc-900 dark:text-zinc-50">{request.identity_document}</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-1">
                  {t("creditRequest.requestedAmount")}
                </label>
                <p className="text-zinc-900 dark:text-zinc-50">
                  {formatCurrency(request.requested_amount, request.currency_code)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-1">
                  {t("creditRequest.monthlyIncome")}
                </label>
                <p className="text-zinc-900 dark:text-zinc-50">
                  {formatCurrency(request.monthly_income, request.currency_code)}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-1">
                  {t("creditRequest.requestDate")}
                </label>
                <p className="text-zinc-900 dark:text-zinc-50">
                  {formatDate(request.request_date)}
                </p>
              </div>
            </div>

            {/* Bank Information (if available) */}
            {request.bank_information && (
              <div>
                <h3 className="text-sm font-medium text-zinc-600 dark:text-zinc-400 mb-2">
                  {t("creditRequest.bankInformation")}
                </h3>
                <div className="p-4 bg-zinc-50 dark:bg-zinc-800 rounded-lg">
                  {request.bank_information.bank_name && (
                    <p className="text-sm text-zinc-900 dark:text-zinc-50">
                      <span className="font-medium">{t("creditRequest.bankName")}:</span>{" "}
                      {request.bank_information.bank_name}
                    </p>
                  )}
                  {request.bank_information.account_number && (
                    <p className="text-sm text-zinc-900 dark:text-zinc-50">
                      <span className="font-medium">{t("creditRequest.accountNumber")}:</span>{" "}
                      {request.bank_information.account_number}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            {(canPutInReview || canApprove || canReject) && (
              <div className="flex gap-3 pt-4 border-t border-zinc-200 dark:border-zinc-700">
                {canPutInReview && (
                  <Button
                    onClick={() => handleStatusUpdate("in_review")}
                    disabled={updating}
                    variant="outline"
                    className="flex-1 border-blue-300 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20"
                  >
                    {updating ? <Spinner /> : t("creditRequest.putInReview")}
                  </Button>
                )}
                {canApprove && (
                  <Button
                    onClick={() => handleStatusUpdate("approved")}
                    disabled={updating}
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                  >
                    {updating ? <Spinner /> : t("creditRequest.approve")}
                  </Button>
                )}
                {canReject && (
                  <Button
                    onClick={() => handleStatusUpdate("rejected")}
                    disabled={updating}
                    variant="outline"
                    className="flex-1 border-red-300 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    {updating ? <Spinner /> : t("creditRequest.reject")}
                  </Button>
                )}
              </div>
            )}
          </div>
        ) : null}
      </Modal>

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={() => setToast({ ...toast, isVisible: false })}
      />
    </>
  );
}
