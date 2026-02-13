import { useState } from "react";
import { useTranslation } from "../i18n/I18nContext";
import Modal from "./ui/Modal";
import Input from "./ui/Input";
import Button from "./ui/Button";
import Spinner from "./ui/Spinner";
import { creditRequestApi } from "../api/creditRequestApi";

const COUNTRIES = [
  { value: "Brazil", label: "Brasil" },
  { value: "Mexico", label: "México" },
  { value: "Portugal", label: "Portugal" },
  { value: "Spain", label: "España" },
  { value: "Italy", label: "Italia" },
  { value: "Colombia", label: "Colombia" },
];

export default function CreateCreditRequestModal({ isOpen, onClose, onSuccess }) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    country: "",
    full_name: "",
    identity_document: "",
    requested_amount: "",
    monthly_income: "",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.country) {
      setError(t("creditRequest.errors.countryRequired"));
      return;
    }
    if (!formData.full_name || formData.full_name.trim().length === 0) {
      setError(t("creditRequest.errors.fullNameRequired"));
      return;
    }
    if (!formData.identity_document || formData.identity_document.trim().length === 0) {
      setError(t("creditRequest.errors.identityDocumentRequired"));
      return;
    }
    const requestedAmount = parseFloat(formData.requested_amount);
    if (!formData.requested_amount || isNaN(requestedAmount) || requestedAmount <= 0) {
      setError(t("creditRequest.errors.amountRequired"));
      return;
    }
    const monthlyIncome = parseFloat(formData.monthly_income);
    if (!formData.monthly_income || isNaN(monthlyIncome) || monthlyIncome <= 0) {
      setError(t("creditRequest.errors.incomeRequired"));
      return;
    }

    setIsLoading(true);

    try {
      const requestData = {
        country: formData.country,
        full_name: formData.full_name.trim(),
        identity_document: formData.identity_document.trim(),
        requested_amount: requestedAmount,
        monthly_income: monthlyIncome,
      };

      await creditRequestApi.create(requestData);
      
      // Reset form
      setFormData({
        country: "",
        full_name: "",
        identity_document: "",
        requested_amount: "",
        monthly_income: "",
      });
      
      onClose();
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setError(err.message || t("creditRequest.errors.createFailed"));
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      setFormData({
        country: "",
        full_name: "",
        identity_document: "",
        requested_amount: "",
        monthly_income: "",
      });
      setError("");
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={t("creditRequest.createTitle")}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.country")} *
          </label>
          <select
            name="country"
            value={formData.country}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">{t("creditRequest.selectCountry")}</option>
            {COUNTRIES.map((country) => (
              <option key={country.value} value={country.value}>
                {country.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.fullName")} *
          </label>
          <Input
            type="text"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            required
            placeholder={t("creditRequest.fullNamePlaceholder")}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.identityDocument")} *
          </label>
          <Input
            type="text"
            name="identity_document"
            value={formData.identity_document}
            onChange={handleChange}
            required
            placeholder={t("creditRequest.identityDocumentPlaceholder")}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.requestedAmount")} *
          </label>
          <Input
            type="number"
            name="requested_amount"
            value={formData.requested_amount}
            onChange={handleChange}
            required
            min="0"
            step="0.01"
            placeholder={t("creditRequest.requestedAmountPlaceholder")}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.monthlyIncome")} *
          </label>
          <Input
            type="number"
            name="monthly_income"
            value={formData.monthly_income}
            onChange={handleChange}
            required
            min="0"
            step="0.01"
            placeholder={t("creditRequest.monthlyIncomePlaceholder")}
          />
        </div>

        <div className="flex gap-3 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isLoading}
            className="flex-1"
          >
            {t("creditRequest.cancel")}
          </Button>
          <Button
            type="submit"
            disabled={isLoading}
            className="flex-1"
          >
            {isLoading ? <Spinner /> : t("creditRequest.submit")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
