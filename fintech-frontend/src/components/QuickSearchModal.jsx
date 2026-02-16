import { useState } from "react";
import { useTranslation } from "../i18n/I18nContext";
import Modal from "./ui/Modal";
import Input from "./ui/Input";
import Button from "./ui/Button";
import Spinner from "./ui/Spinner";

export default function QuickSearchModal({ isOpen, onClose, onSearch }) {
  const { t } = useTranslation();
  const [requestId, setRequestId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    if (!requestId.trim()) {
      setError(t("creditRequest.quickSearch.errors.requestIdRequired"));
      return;
    }

    setLoading(true);
    try {
      await onSearch(requestId.trim());
      setRequestId("");
      onClose();
    } catch (err) {
      setError(err.message || t("creditRequest.quickSearch.errors.searchFailed"));
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setRequestId("");
      setError("");
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={t("creditRequest.quickSearch.title")}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            {t("creditRequest.quickSearch.requestIdLabel")}
          </label>
          <Input
            type="text"
            value={requestId}
            onChange={(e) => {
              setRequestId(e.target.value);
              setError("");
            }}
            placeholder={t("creditRequest.quickSearch.requestIdPlaceholder")}
            required
            disabled={loading}
            autoFocus
          />
          {error && (
            <p className="mt-2 text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          )}
        </div>

        <div className="flex gap-3 justify-end pt-4 border-t border-zinc-200 dark:border-zinc-700">
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={loading}
          >
            {t("creditRequest.cancel")}
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? <Spinner /> : t("creditRequest.quickSearch.search")}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
