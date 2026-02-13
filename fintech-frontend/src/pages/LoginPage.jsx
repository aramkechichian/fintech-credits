import { useState } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { useAuth } from "../context/AuthContext";
import { translateError } from "../utils/errorTranslator";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import Spinner from "../components/ui/Spinner";

export default function LoginPage({ onNavigate }) {
  const { t } = useTranslation();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(email, password);
      // Redirect will happen automatically via AuthContext
    } catch (err) {
      const errorMessage = translateError(err.message, t);
      setError(errorMessage || t("login.error"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-100 dark:bg-zinc-950 flex items-center justify-center px-4">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">{t("login.title")}</h1>
          <p className="text-zinc-600 dark:text-zinc-400">{t("login.subtitle")}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">{t("login.email")}</label>
            <Input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder={t("login.emailPlaceholder")}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">{t("login.password")}</label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder={t("login.passwordPlaceholder")}
            />
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? <Spinner /> : t("login.submit")}
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            {t("login.noAccount")}{" "}
            <button
              onClick={() => onNavigate && onNavigate("register")}
              className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
            >
              {t("login.registerLink")}
            </button>
          </p>
        </div>
      </Card>
    </div>
  );
}
