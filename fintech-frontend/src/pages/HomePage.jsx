import { useTranslation } from "../i18n/I18nContext";
import { useAuth } from "../context/AuthContext";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";

export default function HomePage() {
  const { t } = useTranslation();
  const { user } = useAuth();

  const handleCreateCreditRequest = () => {
    // TODO: Implementar navegación a la página de crear solicitud de crédito
    console.log("Crear solicitud de crédito");
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2 text-zinc-900 dark:text-zinc-50">
          {t("home.welcome")}, {user?.full_name || ""}
        </h1>
        <p className="text-zinc-600 dark:text-zinc-400">
          {t("home.description")}
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer" onClick={handleCreateCreditRequest}>
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-4">
              <svg
                className="w-8 h-8 text-blue-600 dark:text-blue-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2 text-zinc-900 dark:text-zinc-50">
              {t("home.createCreditRequest")}
            </h3>
            <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-4">
              {t("home.startNewRequest")}
            </p>
            <Button className="w-full">
              {t("home.createCreditRequest")}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
