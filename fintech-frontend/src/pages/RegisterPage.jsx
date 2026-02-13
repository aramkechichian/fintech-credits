import { useState } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { authApi } from "../api/authApi";
import { translateError } from "../utils/errorTranslator";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import Spinner from "../components/ui/Spinner";

export default function RegisterPage({ onNavigate }) {
  const { t } = useTranslation();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (password !== confirmPassword) {
      setError(t("register.passwordMismatch"));
      return;
    }

    if (password.length < 6) {
      setError(t("register.passwordTooShort"));
      return;
    }

    setIsLoading(true);

    try {
      await authApi.register(fullName, email, password);
      // Redirect to login page after successful registration
      if (onNavigate) {
        onNavigate("login");
      }
    } catch (err) {
      const errorMessage = translateError(err.message, t);
      setError(errorMessage || t("register.error"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-100 dark:bg-zinc-950 flex items-center justify-center px-4 py-8">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">{t("register.title")}</h1>
          <p className="text-zinc-600 dark:text-zinc-400">{t("register.subtitle")}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="p-3 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">{t("register.fullName")}</label>
            <Input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              placeholder={t("register.fullNamePlaceholder")}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">{t("register.email")}</label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder={t("register.emailPlaceholder")}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">{t("register.password")}</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder={t("register.passwordPlaceholder")}
              minLength={6}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">{t("register.confirmPassword")}</label>
            <Input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder={t("register.confirmPasswordPlaceholder")}
              minLength={6}
            />
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2"
          >
            {isLoading ? <Spinner /> : t("register.submit")}
          </Button>
        </form>

        <div className="mt-8 text-center">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            {t("register.hasAccount")}{" "}
            <button
              onClick={() => onNavigate && onNavigate("login")}
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              {t("register.loginLink")}
            </button>
          </p>
        </div>
      </Card>
    </div>
  );
}
