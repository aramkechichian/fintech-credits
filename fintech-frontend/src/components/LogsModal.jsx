import { useState, useEffect } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { logApi } from "../api/logApi";
import Modal from "./ui/Modal";
import Input from "./ui/Input";
import Button from "./ui/Button";
import Spinner from "./ui/Spinner";
import Card from "./ui/Card";

export default function LogsModal({ isOpen, onClose }) {
  const { t } = useTranslation();
  
  const HTTP_METHODS = [
    { value: "", label: t("logs.allMethods") },
    { value: "GET", label: "GET" },
    { value: "POST", label: "POST" },
    { value: "PUT", label: "PUT" },
    { value: "DELETE", label: "DELETE" },
    { value: "PATCH", label: "PATCH" },
  ];
  const [filters, setFilters] = useState({
    method: "",
    module: "",
    date_from: "",
    date_to: "",
  });
  const [availableModules, setAvailableModules] = useState([]);
  const [loadingModules, setLoadingModules] = useState(false);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    total_pages: 0,
  });
  const [exporting, setExporting] = useState(false);

  // Load available modules when modal opens
  useEffect(() => {
    if (isOpen) {
      loadAvailableModules();
    }
  }, [isOpen]);

  const loadAvailableModules = async () => {
    setLoadingModules(true);
    try {
      const data = await logApi.getAvailableModules();
      setAvailableModules(data.modules || []);
    } catch (err) {
      console.error("Error loading modules:", err);
    } finally {
      setLoadingModules(false);
    }
  };

  // Search when pagination changes (but not on initial mount)
  useEffect(() => {
    if (isOpen && pagination.page > 0) {
      handleSearch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.page, pagination.limit]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSearch = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await logApi.search(filters, pagination.page, pagination.limit);
      setLogs(data.items || []);
      setPagination((prev) => ({
        ...prev,
        total: data.total || 0,
        total_pages: data.total_pages || 0,
      }));
    } catch (err) {
      console.error("Error searching logs:", err);
      setError(err.message || t("logs.searchError"));
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setExporting(true);
      // Export all fields by default
      await logApi.exportToExcel(filters);
      
      // Show success message (could use toast here)
    } catch (err) {
      console.error("Error exporting:", err);
      const errorMessage = err.message || t("logs.exportError");
      const isNoDataError = errorMessage.includes("No data found") || 
                           errorMessage.includes("No se encontraron datos") ||
                           errorMessage.includes("Nenhum dado encontrado") ||
                           errorMessage.includes("Nessun dato trovato");
      
      setError(isNoDataError ? t("logs.noDataFound") : errorMessage);
    } finally {
      setExporting(false);
    }
  };

  const handlePageChange = (newPage) => {
    setPagination((prev) => ({
      ...prev,
      page: newPage,
    }));
  };

  const handleLimitChange = (e) => {
    const newLimit = parseInt(e.target.value, 10);
    setPagination((prev) => ({
      ...prev,
      limit: newLimit,
      page: 1, // Reset to first page when changing limit
    }));
  };

  const handleClose = () => {
    setFilters({
      method: "",
      module: "",
      date_from: "",
      date_to: "",
    });
    setLogs([]);
    setError("");
    setPagination({
      page: 1,
      limit: 20,
      total: 0,
      total_pages: 0,
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={t("logs.title")}
      size="xl"
    >
      <div className="space-y-4">
        {/* Filters */}
        <Card className="p-4">
          <h3 className="text-lg font-semibold mb-4 text-zinc-900 dark:text-zinc-50">
            {t("logs.filters")}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                {t("logs.method")}
              </label>
              <select
                name="method"
                value={filters.method}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {HTTP_METHODS.map((method) => (
                  <option key={method.value} value={method.value}>
                    {method.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                {t("logs.module")}
              </label>
              <select
                name="module"
                value={filters.module}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loadingModules}
              >
                <option value="">{t("logs.allModules")}</option>
                {availableModules.map((module) => (
                  <option key={module} value={module}>
                    {t(`logs.modules.${module}`, module)}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                {t("logs.dateFrom")}
              </label>
              <Input
                type="date"
                name="date_from"
                value={filters.date_from}
                onChange={handleChange}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                {t("logs.dateTo")}
              </label>
              <Input
                type="date"
                name="date_to"
                value={filters.date_to}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="mt-4 flex gap-3">
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? <Spinner /> : t("logs.search")}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setFilters({
                  method: "",
                  module: "",
                  date_from: "",
                  date_to: "",
                });
                setPagination((prev) => ({ ...prev, page: 1 }));
              }}
            >
              {t("logs.resetFilters")}
            </Button>
          </div>
        </Card>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400">
            {error}
          </div>
        )}

        {/* Results */}
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Spinner />
            <span className="ml-2 text-zinc-600 dark:text-zinc-400">
              {t("logs.loading")}
            </span>
          </div>
        ) : logs.length > 0 ? (
          <>
            {/* Export Button */}
            <div className="flex justify-end">
              <Button
                onClick={handleExport}
                disabled={exporting}
                variant="outline"
              >
                {exporting ? (
                  <>
                    <Spinner />
                    <span className="ml-2">{t("logs.exporting")}</span>
                  </>
                ) : (
                  t("logs.export")
                )}
              </Button>
            </div>

            {/* Logs Table */}
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-zinc-300 dark:border-zinc-700">
                <thead>
                  <tr className="bg-zinc-100 dark:bg-zinc-800">
                    <th className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-left text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                      {t("logs.module")}
                    </th>
                    <th className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-left text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                      {t("logs.method")}
                    </th>
                    <th className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-left text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                      {t("logs.responseStatus")}
                    </th>
                    <th className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-left text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                      {t("logs.isSuccess")}
                    </th>
                    <th className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-left text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                      {t("logs.createdAt")}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => {
                    // Get friendly module name
                    const moduleKey = log.module || log.endpoint;
                    const moduleName = moduleKey && moduleKey.startsWith("/") 
                      ? log.endpoint 
                      : (moduleKey ? t(`logs.modules.${moduleKey}`, log.endpoint) : log.endpoint);
                    
                    return (
                      <tr
                        key={log.id}
                        className="hover:bg-zinc-50 dark:hover:bg-zinc-800"
                      >
                        <td className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300">
                          {moduleName}
                        </td>
                      <td className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300">
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            log.method === "GET"
                              ? "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
                              : log.method === "POST"
                              ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                              : log.method === "PUT"
                              ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400"
                              : log.method === "DELETE"
                              ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                              : "bg-zinc-100 text-zinc-800 dark:bg-zinc-900/30 dark:text-zinc-400"
                          }`}
                        >
                          {log.method}
                        </span>
                      </td>
                      <td className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300">
                        {log.response_status ? (
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              log.response_status >= 200 && log.response_status < 300
                                ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                                : log.response_status >= 400 && log.response_status < 500
                                ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400"
                                : log.response_status >= 500
                                ? "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                                : "bg-zinc-100 text-zinc-800 dark:bg-zinc-900/30 dark:text-zinc-400"
                            }`}
                          >
                            {log.response_status}
                          </span>
                        ) : (
                          "-"
                        )}
                      </td>
                      <td className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300">
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            log.is_success
                              ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                              : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
                          }`}
                        >
                          {log.is_success ? t("logs.yes") : t("logs.no")}
                        </span>
                      </td>
                      <td className="border border-zinc-300 dark:border-zinc-700 px-4 py-2 text-sm text-zinc-700 dark:text-zinc-300">
                        {log.created_at
                          ? new Date(log.created_at).toLocaleString()
                          : "-"}
                      </td>
                    </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pagination.total_pages > 1 && (
              <div className="flex items-center justify-between pt-4 border-t border-zinc-200 dark:border-zinc-700">
                <div className="text-sm text-zinc-600 dark:text-zinc-400">
                  {t("logs.showingResults", {
                    from: (pagination.page - 1) * pagination.limit + 1,
                    to: Math.min(
                      pagination.page * pagination.limit,
                      pagination.total
                    ),
                    total: pagination.total,
                  })}
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page === 1}
                  >
                    {t("logs.previous")}
                  </Button>
                  <span className="text-sm text-zinc-600 dark:text-zinc-400">
                    {t("logs.pageOf", {
                      page: pagination.page,
                      total: pagination.total_pages,
                    })}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page >= pagination.total_pages}
                  >
                    {t("logs.next")}
                  </Button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-8 text-zinc-600 dark:text-zinc-400">
            {t("logs.noResults")}
          </div>
        )}
      </div>
    </Modal>
  );
}
