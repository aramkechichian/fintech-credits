import { useState, useEffect } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { creditRequestApi } from "../api/creditRequestApi";
import { bankProviderApi } from "../api/bankProviderApi";
import { translateError } from "../utils/errorTranslator";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import Spinner from "../components/ui/Spinner";
import CreditRequestDetailModal from "../components/CreditRequestDetailModal";
import Modal from "../components/ui/Modal";

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
    limit: 5,
    total: 0,
    total_pages: 0,
  });
  const [selectedRequestId, setSelectedRequestId] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [isBankInfoModalOpen, setIsBankInfoModalOpen] = useState(false);
  const [bankInfoData, setBankInfoData] = useState(null);
  const [bankInfoLoading, setBankInfoLoading] = useState(false);
  const [bankInfoError, setBankInfoError] = useState("");
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [urlParams, setUrlParams] = useState(new URLSearchParams(window.location.search));

  // Update URL params when location changes
  useEffect(() => {
    const handleLocationChange = () => {
      setUrlParams(new URLSearchParams(window.location.search));
    };

    window.addEventListener('locationchange', handleLocationChange);
    window.addEventListener('popstate', handleLocationChange);

    return () => {
      window.removeEventListener('locationchange', handleLocationChange);
      window.removeEventListener('popstate', handleLocationChange);
    };
  }, []);

  // Get filters from URL (now reactive)
  const countries = urlParams.getAll("countries");
  const identityDocument = urlParams.get("identity_document") || "";
  const status = urlParams.get("status") || "";
  const page = parseInt(urlParams.get("page") || "1", 10);
  const limitFromUrl = parseInt(urlParams.get("limit") || "5", 10);

  // Update pagination when URL params change
  useEffect(() => {
    setPagination(prev => ({
      ...prev,
      limit: limitFromUrl,
      page: page
    }));
  }, [limitFromUrl, page]);

  useEffect(() => {
    loadRequests();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlParams]);

  const loadRequests = async () => {
    setLoading(true);
    setError("");

    try {
      // Always read from current URL to ensure we have the latest values
      const currentParams = new URLSearchParams(window.location.search);
      const currentPage = parseInt(currentParams.get("page") || "1", 10);
      const currentLimit = parseInt(currentParams.get("limit") || "5", 10);
      const currentCountries = currentParams.getAll("countries");
      const currentIdentityDocument = currentParams.get("identity_document") || "";
      const currentStatus = currentParams.get("status") || "";

      const params = new URLSearchParams();
      currentCountries.forEach((country) => params.append("countries", country));
      if (currentIdentityDocument) params.append("identity_document", currentIdentityDocument);
      if (currentStatus) params.append("status", currentStatus);
      params.append("page", currentPage.toString());
      params.append("limit", currentLimit.toString());

      const data = await creditRequestApi.search(params);
      setRequests(data.items || []);
      setPagination({
        page: data.page || 1,
        limit: data.limit || 5,
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
    params.set("limit", pagination.limit.toString());
    window.history.pushState({ path: window.location.pathname }, "", `${window.location.pathname}?${params.toString()}`);
    window.dispatchEvent(new Event('locationchange'));
  };

  const handleLimitChange = (newLimit) => {
    const params = new URLSearchParams(window.location.search);
    params.set("limit", newLimit.toString());
    params.set("page", "1"); // Reset to first page when changing limit
    window.history.pushState({ path: window.location.pathname }, "", `${window.location.pathname}?${params.toString()}`);
    window.dispatchEvent(new Event('locationchange'));
    setPagination(prev => ({ ...prev, limit: newLimit, page: 1 }));
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
      year: "2-digit",
      month: "2-digit",
      day: "2-digit",
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
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => (window.location.href = "/")}
            >
              {t("creditRequest.backToHome")}
            </Button>
          </div>
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
              <table className="w-full text-xs">
                <thead className="bg-zinc-100 dark:bg-zinc-800 border-b border-zinc-200 dark:border-zinc-700">
                  <tr>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.requestNumber")}
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.country")}
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.fullName")}
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.email")}
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.identityDocument")}
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.requestedAmount")}
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.status._label")}
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                      {t("creditRequest.requestDate")}
                    </th>
                    <th className="px-2 py-2 text-left text-xs font-medium text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
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
                      <td className="px-2 py-2 whitespace-nowrap text-xs text-zinc-900 dark:text-zinc-50 font-mono">
                        <span className="truncate block max-w-[100px]">{request.id}</span>
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap text-xs text-zinc-900 dark:text-zinc-50">
                        {request.country}
                      </td>
                      <td className="px-2 py-2 text-xs text-zinc-900 dark:text-zinc-50">
                        <span className="truncate block max-w-[120px]" title={request.full_name}>
                          {request.full_name}
                        </span>
                      </td>
                      <td className="px-2 py-2 text-xs text-zinc-900 dark:text-zinc-50">
                        <span className="truncate block max-w-[150px]" title={request.email}>
                          {request.email}
                        </span>
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap text-xs text-zinc-900 dark:text-zinc-50">
                        <span className="truncate block max-w-[100px]" title={request.identity_document}>
                          {request.identity_document}
                        </span>
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap text-xs text-zinc-900 dark:text-zinc-50">
                        {formatCurrency(
                          request.requested_amount,
                          request.currency_code
                        )}
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap">
                        <span
                          className={`px-1.5 py-0.5 text-xs font-medium rounded-full ${
                            STATUS_COLORS[request.status] || STATUS_COLORS.pending
                          }`}
                        >
                          {t(`creditRequest.status.${request.status}`) || request.status}
                        </span>
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap text-xs text-zinc-600 dark:text-zinc-400">
                        {formatDate(request.request_date)}
                      </td>
                      <td className="px-2 py-2 whitespace-nowrap">
                        <div className="flex gap-1">
                          <Button
                            variant="outline"
                            onClick={() => {
                              setSelectedRequestId(request.id);
                              setIsDetailModalOpen(true);
                            }}
                            className="text-xs px-2 py-1"
                          >
                            {t("creditRequest.viewDetail")}
                          </Button>
                          <Button
                            variant="outline"
                            onClick={async () => {
                              setBankInfoData(null);
                              setBankInfoError("");
                              setSelectedCountry(request.country);
                              setIsBankInfoModalOpen(true);
                              setBankInfoLoading(true);
                              
                              try {
                                const data = await bankProviderApi.getBankInformation(
                                  request.country,
                                  request.full_name,
                                  request.identity_document
                                );
                                setBankInfoData(data);
                                setBankInfoError("");
                              } catch (err) {
                                // If it's a 404 or connection error, show a friendly message
                                if (err.message.includes("404") || err.message.includes("Not Found") || err.message.includes("Failed to fetch")) {
                                  setBankInfoData({
                                    status: "not_connected",
                                    message: t("creditRequest.bankInfo.notConnectedMessage", { country: request.country }),
                                    description: t("creditRequest.bankInfo.description"),
                                    country: request.country,
                                    full_name: request.full_name,
                                    identity_document: request.identity_document,
                                    bank_information: null
                                  });
                                  setBankInfoError("");
                                } else {
                                  const errorMessage = translateError(err.message, t);
                                  setBankInfoError(errorMessage || t("creditRequest.bankInfo.error"));
                                }
                              } finally {
                                setBankInfoLoading(false);
                              }
                            }}
                            className="text-xs px-2 py-1"
                          >
                            {t("creditRequest.consultBankSituation")}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Pagination */}
          {(pagination.total_pages > 1 || pagination.total > 0) && (
            <div className="mt-6 space-y-4">
              <div className="flex items-center justify-between">
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
                <div className="flex items-center gap-3">
                  <label className="text-sm text-zinc-600 dark:text-zinc-400">
                    {t("creditRequest.itemsPerPage")}:
                  </label>
                  <select
                    value={pagination.limit}
                    onChange={(e) => handleLimitChange(parseInt(e.target.value, 10))}
                    className="px-3 py-1.5 text-sm border border-zinc-300 dark:border-zinc-700 rounded-md bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={5}>5</option>
                    <option value={10}>10</option>
                    <option value={50}>50</option>
                  </select>
                </div>
              </div>
              {pagination.total_pages > 1 && (
                <div className="flex items-center justify-center gap-2">
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
              )}
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

      {/* Bank Information Modal */}
      <Modal
        isOpen={isBankInfoModalOpen}
        onClose={() => {
          setIsBankInfoModalOpen(false);
          setBankInfoData(null);
          setBankInfoError("");
          setSelectedCountry(null);
        }}
        title={t("creditRequest.bankInfo.title")}
        size="md"
      >
        {bankInfoLoading ? (
          <div className="flex justify-center items-center py-8">
            <Spinner />
          </div>
        ) : bankInfoError ? (
          <div className="p-4 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">
            {bankInfoError}
          </div>
        ) : bankInfoData ? (
          <div className="space-y-4">
            {bankInfoData.status === "not_connected" ? (
              <div className="space-y-3">
                <div className="p-4 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400">
                  <p className="font-medium mb-2">{t("creditRequest.bankInfo.notConnected")}</p>
                  <p className="text-sm mb-3">
                    {bankInfoData.message || t("creditRequest.bankInfo.notConnectedMessage", { country: bankInfoData.country || selectedCountry || "" })}
                  </p>
                  <div className="mt-3 pt-3 border-t border-yellow-300 dark:border-yellow-700">
                    <p className="text-sm font-medium mb-1">{t("creditRequest.bankInfo.about")}</p>
                    <p className="text-sm">
                      {bankInfoData.description || t("creditRequest.bankInfo.description")}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="p-4 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400">
                  <p className="font-medium">{t("creditRequest.bankInfo.connected")}</p>
                </div>
                {bankInfoData.bank_information && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-zinc-900 dark:text-zinc-50">
                      {t("creditRequest.bankInfo.details")}
                    </h4>
                    <div className="bg-zinc-50 dark:bg-zinc-800 p-4 rounded-lg space-y-2 text-sm">
                      {bankInfoData.bank_information.bank_name && (
                        <div>
                          <span className="font-medium text-zinc-700 dark:text-zinc-300">
                            {t("creditRequest.bankName")}:
                          </span>{" "}
                          <span className="text-zinc-900 dark:text-zinc-50">
                            {bankInfoData.bank_information.bank_name}
                          </span>
                        </div>
                      )}
                      {bankInfoData.bank_information.account_number && (
                        <div>
                          <span className="font-medium text-zinc-700 dark:text-zinc-300">
                            {t("creditRequest.accountNumber")}:
                          </span>{" "}
                          <span className="text-zinc-900 dark:text-zinc-50">
                            {bankInfoData.bank_information.account_number}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
            <div className="pt-4 border-t border-zinc-200 dark:border-zinc-700">
              <div className="text-xs text-zinc-600 dark:text-zinc-400 space-y-1">
                <div>
                  <span className="font-medium">{t("creditRequest.country")}:</span> {bankInfoData.country}
                </div>
                <div>
                  <span className="font-medium">{t("creditRequest.fullName")}:</span> {bankInfoData.full_name}
                </div>
                <div>
                  <span className="font-medium">{t("creditRequest.identityDocument")}:</span> {bankInfoData.identity_document}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
}
