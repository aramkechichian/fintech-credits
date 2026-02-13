import { useState, useEffect } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { creditRequestApi } from "../api/creditRequestApi";
import { translateError } from "../utils/errorTranslator";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import CreditRequestDetailModal from "../components/CreditRequestDetailModal";

// Status labels will be translated using the translation function

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  in_review: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  approved: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  cancelled: "bg-zinc-100 text-zinc-800 dark:bg-zinc-900/30 dark:text-zinc-400",
};

export default function CreditRequestsListPage() {
  const { t } = useTranslation();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    total_pages: 0,
  });
  const [selectedRequestId, setSelectedRequestId] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  // Get filters from URL
  const urlParams = new URLSearchParams(window.location.search);
  const countries = urlParams.getAll("countries");
  const identityDocument = urlParams.get("identity_document") || "";
  const status = urlParams.get("status") || "";
  const page = parseInt(urlParams.get("page") || "1", 10);

  useEffect(() => {
    loadRequests();
  }, [page, countries.join(","), identityDocument, status]);

  const loadRequests = async () => {
    setLoading(true);
    setError("");

    try {
      const params = new URLSearchParams();
      countries.forEach((country) => params.append("countries", country));
      if (identityDocument) params.append("identity_document", identityDocument);
      if (status) params.append("status", status);
      params.append("page", page.toString());
      params.append("limit", pagination.limit.toString());

      const data = await creditRequestApi.search(params);
      setRequests(data.items || []);
      setPagination({
        page: data.page || 1,
        limit: data.limit || 20,
        total: data.total || 0,
        total_pages: data.total_pages || 0,
      });
    } catch (err) {
      const errorMessage = translateError(err.message, t);
      setError(errorMessage || t("creditRequest.searchError"));
      // If session expired, redirect to login after a short delay
      if (err.message && (err.message.includes("sesión ha expirado") || err.message.includes("session expired"))) {
        setTimeout(() => {
          window.location.href = "/";
        }, 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage) => {
    const params = new URLSearchParams(window.location.search);
    params.set("page", newPage.toString());
    window.location.href = `/credit-requests/search?${params.toString()}`;
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
      month: "short",
      day: "numeric",
    }).format(date);
  };

  const hasFilters = countries.length > 0 || identityDocument || status;

  return (
    <div className="p-8">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
            {t("creditRequest.listTitle")}
          </h1>
          <Button
            variant="outline"
            onClick={() => (window.location.href = "/")}
          >
            {t("creditRequest.backToHome")}
          </Button>
        </div>

        {hasFilters && (
          <div className="flex flex-wrap gap-2 mb-4">
            {countries.length > 0 && (
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full text-sm">
                {t("creditRequest.country")}: {countries.join(", ")}
              </span>
            )}
            {identityDocument && (
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full text-sm">
                {t("creditRequest.identityDocument")}: {identityDocument}
              </span>
            )}
            {status && (
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full text-sm">
                {t("creditRequest.status._label")}: {t(`creditRequest.status.${status}`) || status}
              </span>
            )}
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Spinner />
        </div>
      ) : error ? (
        <Card className="p-6">
          <div className="text-center text-red-600 dark:text-red-400">
            {error}
          </div>
        </Card>
      ) : requests.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold mb-2 text-zinc-900 dark:text-zinc-50">
              {t("creditRequest.noResults")}
            </h3>
            <p className="text-zinc-600 dark:text-zinc-400 mb-4">
              {t("creditRequest.noResultsDescription")}
            </p>
            <Button
              variant="outline"
              onClick={() => (window.location.href = "/")}
            >
              {t("creditRequest.backToHome")}
            </Button>
          </div>
        </Card>
      ) : (
        <>
          <Card className="p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-zinc-100 dark:bg-zinc-800 border-b border-zinc-200 dark:border-zinc-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.country")}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.fullName")}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.identityDocument")}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.requestedAmount")}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.status._label")}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.requestDate")}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.actions")}
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-zinc-900 divide-y divide-zinc-200 dark:divide-zinc-800">
                  {requests.map((request) => (
                    <tr
                      key={request.id}
                      className="hover:bg-zinc-50 dark:hover:bg-zinc-800/50 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-900 dark:text-zinc-50">
                        {request.country}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-900 dark:text-zinc-50">
                        {request.full_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-900 dark:text-zinc-50">
                        {request.identity_document}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-900 dark:text-zinc-50">
                        {formatCurrency(
                          request.requested_amount,
                          request.currency_code
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${
                            STATUS_COLORS[request.status] || STATUS_COLORS.pending
                          }`}
                        >
                          {t(`creditRequest.status.${request.status}`) || request.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-600 dark:text-zinc-400">
                        {formatDate(request.request_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Button
                          variant="outline"
                          onClick={() => {
                            setSelectedRequestId(request.id);
                            setIsDetailModalOpen(true);
                          }}
                          className="text-xs px-3 py-1"
                        >
                          {t("creditRequest.viewDetail")}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Pagination */}
          {pagination.total_pages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-zinc-600 dark:text-zinc-400">
                {t("creditRequest.showingResults", {
                  from: (pagination.page - 1) * pagination.limit + 1,
                  to: Math.min(
                    pagination.page * pagination.limit,
                    pagination.total
                  ),
                  total: pagination.total,
                })}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={pagination.page === 1}
                >
                  {t("creditRequest.previous")}
                </Button>
                <span className="px-4 py-2 text-sm text-zinc-600 dark:text-zinc-400">
                  {t("creditRequest.pageOf", {
                    page: pagination.page,
                    total: pagination.total_pages,
                  })}
                </span>
                <Button
                  variant="outline"
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={pagination.page >= pagination.total_pages}
                >
                  {t("creditRequest.next")}
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      <CreditRequestDetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedRequestId(null);
        }}
        requestId={selectedRequestId}
        onUpdate={(updatedRequest) => {
          // Update the request in the list
          setRequests((prev) =>
            prev.map((req) =>
              req.id === updatedRequest.id ? updatedRequest : req
            )
          );
        }}
      />
    </div>
  );
}
