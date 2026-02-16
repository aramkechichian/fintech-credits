import { useState, useEffect } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { dataApi } from "../api/dataApi";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Spinner from "../components/ui/Spinner";
import Toast from "../components/ui/Toast";

const COUNTRIES = [
  { value: "Brazil", label: "Brasil" },
  { value: "Mexico", label: "México" },
  { value: "Portugal", label: "Portugal" },
  { value: "Spain", label: "España" },
  { value: "Italy", label: "Italia" },
  { value: "Colombia", label: "Colombia" },
];

const STATUS_OPTIONS = [
  { value: "", label: "Todos los Estados" },
  { value: "pending", label: "Pendiente" },
  { value: "in_review", label: "En Revisión" },
  { value: "approved", label: "Aprobada" },
  { value: "rejected", label: "Rechazada" },
  { value: "cancelled", label: "Cancelada" },
];

export default function AuditsPage() {
  const { t } = useTranslation();
  const [filters, setFilters] = useState({
    countries: [],
    request_date_from: "",
    request_date_to: "",
    status: "",
  });
  const [selectedCountries, setSelectedCountries] = useState([]);
  const [availableFields, setAvailableFields] = useState({});
  const [selectedFields, setSelectedFields] = useState([]);
  const [loadingFields, setLoadingFields] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [toast, setToast] = useState({ isVisible: false, message: "", type: "success" });

  useEffect(() => {
    loadAvailableFields();
  }, []);

  const loadAvailableFields = async () => {
    try {
      setLoadingFields(true);
      const response = await dataApi.getAvailableFields();
      setAvailableFields(response.fields || {});
      // Select all fields by default
      setSelectedFields(response.field_names || []);
    } catch (error) {
      console.error("Error loading fields:", error);
      setToast({
        isVisible: true,
        message: t("audits.fieldsError"),
        type: "error",
      });
    } finally {
      setLoadingFields(false);
    }
  };

  const handleCountryToggle = (countryValue) => {
    setSelectedCountries((prev) => {
      if (prev.includes(countryValue)) {
        return prev.filter((c) => c !== countryValue);
      } else {
        return [...prev, countryValue];
      }
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleFieldToggle = (fieldName) => {
    setSelectedFields((prev) => {
      if (prev.includes(fieldName)) {
        return prev.filter((f) => f !== fieldName);
      } else {
        return [...prev, fieldName];
      }
    });
  };

  const handleSelectAll = () => {
    setSelectedFields(Object.keys(availableFields));
  };

  const handleDeselectAll = () => {
    setSelectedFields([]);
  };

  const handleExport = async () => {
    if (selectedFields.length === 0) {
      setToast({
        isVisible: true,
        message: t("audits.noFieldsSelected"),
        type: "error",
      });
      return;
    }

    try {
      setExporting(true);
      const exportFilters = {
        countries: selectedCountries,
        request_date_from: filters.request_date_from || undefined,
        request_date_to: filters.request_date_to || undefined,
        status: filters.status || undefined,
      };

      await dataApi.exportToExcel(exportFilters, selectedFields);
      
      setToast({
        isVisible: true,
        message: t("audits.exportSuccess"),
        type: "success",
      });
    } catch (error) {
      console.error("Error exporting:", error);
      const errorMessage = error.message || t("audits.exportError");
      
      // Check if it's a "no data" error (404 or message contains "No data found")
      const isNoDataError = errorMessage.includes("No data found") || 
                           errorMessage.includes("No se encontraron datos") ||
                           errorMessage.includes("Nenhum dado encontrado") ||
                           errorMessage.includes("Nessun dato trovato") ||
                           errorMessage.includes("No data found matching");
      
      setToast({
        isVisible: true,
        message: isNoDataError ? t("audits.noDataFound") : errorMessage,
        type: "error",
      });
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2 text-zinc-900 dark:text-zinc-50">
              {t("audits.title")}
            </h1>
            <p className="text-zinc-600 dark:text-zinc-400">
              {t("audits.description")}
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => {
                window.history.pushState({ route: "home" }, "", "/");
                window.dispatchEvent(new Event("locationchange"));
              }}
            >
              {t("creditRequest.backToHome")}
            </Button>
          </div>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Filters Section */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 text-zinc-900 dark:text-zinc-50">
            {t("audits.filters")}
          </h2>

          <div className="space-y-4">
            {/* Countries */}
            <div>
              <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                {t("creditRequest.filterByCountry")}
              </label>
              <div className="flex flex-wrap gap-2">
                {COUNTRIES.map((country) => (
                  <button
                    key={country.value}
                    type="button"
                    onClick={() => handleCountryToggle(country.value)}
                    className={`px-3 py-1 rounded-full text-sm transition-colors ${
                      selectedCountries.includes(country.value)
                        ? "bg-blue-600 text-white"
                        : "bg-zinc-200 dark:bg-zinc-700 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-300 dark:hover:bg-zinc-600"
                    }`}
                  >
                    {country.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Request Date From */}
            <div>
              <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                {t("audits.requestDateFrom")}
              </label>
              <Input
                type="date"
                name="request_date_from"
                value={filters.request_date_from}
                onChange={handleChange}
              />
            </div>

            {/* Request Date To */}
            <div>
              <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                {t("audits.requestDateTo")}
              </label>
              <Input
                type="date"
                name="request_date_to"
                value={filters.request_date_to}
                onChange={handleChange}
              />
            </div>

            {/* Status */}
            <div>
              <label className="block text-sm font-medium mb-2 text-zinc-700 dark:text-zinc-300">
                {t("creditRequest.filterByStatus")}
              </label>
              <select
                name="status"
                value={filters.status}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-600 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">{t("creditRequest.allStatuses")}</option>
                <option value="pending">{t("creditRequest.status.pending")}</option>
                <option value="in_review">{t("creditRequest.status.in_review")}</option>
                <option value="approved">{t("creditRequest.status.approved")}</option>
                <option value="rejected">{t("creditRequest.status.rejected")}</option>
                <option value="cancelled">{t("creditRequest.status.cancelled")}</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Fields Selection Section */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
              {t("audits.selectFields")}
            </h2>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
              >
                {t("audits.selectAll")}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDeselectAll}
              >
                {t("audits.deselectAll")}
              </Button>
            </div>
          </div>

          <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
            {t("audits.selectFieldsDescription")}
          </p>

          {loadingFields ? (
            <div className="flex items-center justify-center py-8">
              <Spinner />
              <span className="ml-2 text-zinc-600 dark:text-zinc-400">
                {t("audits.loadingFields")}
              </span>
            </div>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {Object.entries(availableFields).map(([fieldName, fieldLabel]) => {
                // Translate field label if translation exists
                const translatedLabel = t(`audits.fields.${fieldName}`, fieldLabel);
                return (
                  <label
                    key={fieldName}
                    className="flex items-center p-2 rounded hover:bg-zinc-100 dark:hover:bg-zinc-800 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedFields.includes(fieldName)}
                      onChange={() => handleFieldToggle(fieldName)}
                      className="w-4 h-4 text-blue-600 border-zinc-300 rounded focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-zinc-700 dark:text-zinc-300">
                      {translatedLabel}
                    </span>
                  </label>
                );
              })}
            </div>
          )}
        </Card>
      </div>

      {/* Export Button */}
      <div className="mt-6 flex justify-end">
        <Button
          onClick={handleExport}
          disabled={exporting || selectedFields.length === 0}
          className="min-w-[200px]"
        >
          {exporting ? (
            <>
              <Spinner />
              <span className="ml-2">{t("audits.exporting")}</span>
            </>
          ) : (
            t("audits.export")
          )}
        </Button>
      </div>

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={() => setToast({ ...toast, isVisible: false })}
      />
    </div>
  );
}
