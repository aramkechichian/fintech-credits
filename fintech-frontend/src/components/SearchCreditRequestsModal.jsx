import { useState } from "react";
import { useTranslation } from "../i18n/I18nContext";
import Modal from "./ui/Modal";
import Input from "./ui/Input";
import Button from "./ui/Button";

const COUNTRIES = [
  { value: "Brazil", label: "Brasil" },
  { value: "Mexico", label: "México" },
  { value: "Portugal", label: "Portugal" },
  { value: "Spain", label: "España" },
  { value: "Italy", label: "Italia" },
  { value: "Colombia", label: "Colombia" },
];

// Status options will be translated in the component

export default function SearchCreditRequestsModal({ isOpen, onClose }) {
  const { t } = useTranslation();
  const [filters, setFilters] = useState({
    countries: [],
    identity_document: "",
    status: "",
  });
  const [selectedCountries, setSelectedCountries] = useState([]);

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

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Build query params
    const params = new URLSearchParams();
    
    if (selectedCountries.length > 0) {
      selectedCountries.forEach((country) => {
        params.append("countries", country);
      });
    }
    
    if (filters.identity_document.trim()) {
      params.append("identity_document", filters.identity_document.trim());
    }
    
    if (filters.status) {
      params.append("status", filters.status);
    }
    
    // Navigate to search results page using history API (no page reload)
    const queryString = params.toString();
    const searchUrl = `/credit-requests/search${queryString ? `?${queryString}` : ""}`;
    
    // Update URL - this will trigger the useEffect in App.jsx that syncs route with URL
    window.history.pushState({ route: "search" }, "", searchUrl);
    
    // Close modal
    onClose();
    
    // Force route update by dispatching a custom event
    window.dispatchEvent(new Event("locationchange"));
  };

  const handleReset = () => {
    setFilters({
      countries: [],
      identity_document: "",
      status: "",
    });
    setSelectedCountries([]);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={t("creditRequest.searchTitle")}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.filterByCountry")}
          </label>
          <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto p-2 border border-zinc-200 dark:border-zinc-700 rounded-lg">
            {COUNTRIES.map((country) => (
              <label
                key={country.value}
                className="flex items-center gap-2 cursor-pointer hover:bg-zinc-100 dark:hover:bg-zinc-800 p-2 rounded"
              >
                <input
                  type="checkbox"
                  checked={selectedCountries.includes(country.value)}
                  onChange={() => handleCountryToggle(country.value)}
                  className="rounded border-zinc-300 dark:border-zinc-700"
                />
                <span className="text-sm text-zinc-700 dark:text-zinc-300">
                  {country.label}
                </span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.filterByIdentityDocument")}
          </label>
          <Input
            type="text"
            name="identity_document"
            value={filters.identity_document}
            onChange={handleChange}
            placeholder={t("creditRequest.identityDocumentPlaceholder")}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.filterByStatus")}
          </label>
          <select
            name="status"
            value={filters.status}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">{t("creditRequest.allStatuses")}</option>
            <option value="pending">{t("creditRequest.status.pending")}</option>
            <option value="in_review">{t("creditRequest.status.in_review")}</option>
            <option value="approved">{t("creditRequest.status.approved")}</option>
            <option value="rejected">{t("creditRequest.status.rejected")}</option>
            <option value="cancelled">{t("creditRequest.status.cancelled")}</option>
          </select>
        </div>

        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={handleReset}
            className="flex-1"
          >
            {t("creditRequest.resetFilters")}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            {t("creditRequest.cancel")}
          </Button>
          <Button type="submit" className="flex-1">
            {t("creditRequest.search")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
