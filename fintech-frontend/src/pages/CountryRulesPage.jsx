import { useState, useEffect } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { countryRuleApi } from "../api/countryRuleApi";
import { translateError } from "../utils/errorTranslator";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import Modal from "../components/ui/Modal";
import Toast from "../components/ui/Toast";
import Spinner from "../components/ui/Spinner";
import Input from "../components/ui/Input";

const COUNTRIES = [
  { value: "Brazil", label: "Brasil" },
  { value: "Mexico", label: "México" },
  { value: "Portugal", label: "Portugal" },
  { value: "Spain", label: "España" },
  { value: "Italy", label: "Italia" },
  { value: "Colombia", label: "Colombia" },
];


export default function CountryRulesPage() {
  const { t } = useTranslation();
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [toast, setToast] = useState({ isVisible: false, message: "", type: "success" });

  // Form state
  const [formData, setFormData] = useState({
    required_document_type: "",
    description: "",
    is_active: true,
    validation_rules: [],
  });

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await countryRuleApi.getAll();
      setRules(response.items || []);
    } catch (err) {
      const errorMessage = translateError(err.message, t);
      setError(errorMessage || t("countryRules.errors.loadFailed"));
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (rule) => {
    setEditingRule(rule);
    setFormData({
      required_document_type: rule.required_document_type,
      description: rule.description || "",
      is_active: rule.is_active,
      validation_rules: rule.validation_rules || [],
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (ruleId) => {
    if (!window.confirm(t("countryRules.deleteConfirm"))) {
      return;
    }

    try {
      await countryRuleApi.delete(ruleId);
      setToast({
        isVisible: true,
        message: t("countryRules.success.deleted"),
        type: "success",
      });
      loadRules();
    } catch (err) {
      const errorMessage = translateError(err.message, t);
      setToast({
        isVisible: true,
        message: errorMessage || t("countryRules.errors.deleteFailed"),
        type: "error",
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!editingRule) {
      return;
    }
    try {
      await countryRuleApi.update(editingRule.id, formData);
      setToast({
        isVisible: true,
        message: t("countryRules.success.updated"),
        type: "success",
      });
      setIsModalOpen(false);
      loadRules();
    } catch (err) {
      const errorMessage = translateError(err.message, t);
      setToast({
        isVisible: true,
        message: errorMessage || t("countryRules.errors.updateFailed"),
        type: "error",
      });
    }
  };

  const addValidationRule = () => {
    setFormData({
      ...formData,
      validation_rules: [
        ...formData.validation_rules,
        {
          rule_type: "document_verification",
          enabled: true,
          config: {},
          error_message: "",
        },
      ],
    });
  };

  const removeValidationRule = (index) => {
    setFormData({
      ...formData,
      validation_rules: formData.validation_rules.filter((_, i) => i !== index),
    });
  };

  const updateValidationRule = (index, field, value) => {
    const updatedRules = [...formData.validation_rules];
    updatedRules[index] = { ...updatedRules[index], [field]: value };
    setFormData({ ...formData, validation_rules: updatedRules });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2 text-zinc-900 dark:text-zinc-50">
          {t("countryRules.title")}
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          {t("countryRules.description")}
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">
          {error}
        </div>
      )}

      {rules.length === 0 ? (
        <Card>
          <div className="text-center py-12 px-6">
            <p className="text-zinc-600 dark:text-zinc-400">
              {t("countryRules.noRules")}
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {rules.map((rule) => (
            <Card key={rule.id}>
              <div className="flex items-start justify-between gap-4 p-6">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold mb-3 text-zinc-900 dark:text-zinc-50">
                    {COUNTRIES.find((c) => c.value === rule.country)?.label || rule.country}
                  </h3>
                  <div className="space-y-2 text-sm text-zinc-600 dark:text-zinc-400">
                    <p>
                      <span className="font-medium">{t("countryRules.requiredDocument")}:</span>{" "}
                      {rule.required_document_type}
                    </p>
                    {rule.description && (
                      <p>
                        <span className="font-medium">{t("countryRules.description")}:</span>{" "}
                        {rule.description}
                      </p>
                    )}
                    <p>
                      <span className="font-medium">{t("countryRules.isActive")}:</span>{" "}
                      {rule.is_active ? "Sí" : "No"}
                    </p>
                    <p>
                      <span className="font-medium">{t("countryRules.validationRules")}:</span>{" "}
                      {rule.validation_rules?.length || 0}
                    </p>
                    {rule.validation_rules && rule.validation_rules.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {rule.validation_rules.map((vr, idx) => (
                          <p key={idx} className="text-xs">
                            <span className="font-medium">Regla {idx + 1}:</span>{" "}
                            {vr.enabled ? `Máx. ${vr.max_percentage}%` : "Deshabilitada"}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(rule)}
                  >
                    {t("countryRules.edit")}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(rule.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    {t("countryRules.delete")}
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={t("countryRules.editRule")}
        size="md"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          {editingRule && (
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
                {t("countryRules.country")}
              </label>
              <div className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
                {COUNTRIES.find((c) => c.value === editingRule.country)?.label || editingRule.country}
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
              {t("countryRules.requiredDocument")} *
            </label>
            <Input
              type="text"
              value={formData.required_document_type}
              onChange={(e) => setFormData({ ...formData, required_document_type: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
              {t("countryRules.description")}
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-zinc-300 dark:border-zinc-700 rounded-lg bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-50"
              rows="3"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="mr-2"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
              {t("countryRules.isActive")}
            </label>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                {t("countryRules.validationRules")}
              </label>
              <Button type="button" variant="outline" size="sm" onClick={addValidationRule}>
                + {t("countryRules.addRule")}
              </Button>
            </div>
            <div className="space-y-2">
              {formData.validation_rules.map((rule, index) => (
                <div key={index} className="p-3 border border-zinc-300 dark:border-zinc-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                      Regla {index + 1}
                    </span>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => removeValidationRule(index)}
                      className="text-red-600"
                    >
                      ×
                    </Button>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <label className="block text-xs text-zinc-600 dark:text-zinc-400 mb-1">
                        {t("countryRules.maxPercentage")} (%)
                      </label>
                      <Input
                        type="number"
                        step="0.1"
                        min="0"
                        max="100"
                        value={rule.max_percentage || ""}
                        onChange={(e) => updateValidationRule(index, "max_percentage", parseFloat(e.target.value) || 0)}
                        size="sm"
                        required
                      />
                      <p className="text-xs text-zinc-500 dark:text-zinc-500 mt-1">
                        {t("countryRules.maxPercentageHelp")}
                      </p>
                    </div>
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={rule.enabled}
                        onChange={(e) => updateValidationRule(index, "enabled", e.target.checked)}
                        className="mr-2"
                      />
                      <label className="text-xs text-zinc-600 dark:text-zinc-400">
                        {t("countryRules.enabled")}
                      </label>
                    </div>
                    <div>
                      <label className="block text-xs text-zinc-600 dark:text-zinc-400 mb-1">
                        {t("countryRules.errorMessage")}
                      </label>
                      <Input
                        type="text"
                        value={rule.error_message || ""}
                        onChange={(e) => updateValidationRule(index, "error_message", e.target.value)}
                        size="sm"
                        placeholder={t("countryRules.errorMessagePlaceholder")}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="submit" className="flex-1">
              {t("countryRules.save")}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => setIsModalOpen(false)}
              className="flex-1"
            >
              {t("countryRules.cancel")}
            </Button>
          </div>
        </form>
      </Modal>

      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={() => setToast({ ...toast, isVisible: false })}
      />
    </div>
  );
}
