import { useState } from "react";
import { useTranslation } from "../i18n/I18nContext";
import { useAuth } from "../context/AuthContext";
import Button from "./ui/Button";

const languages = [
  { code: "es", name: "Español", flag: "🇪🇸" },
  { code: "en", name: "English", flag: "🇬🇧" },
  { code: "pt", name: "Português", flag: "🇵🇹" },
  { code: "it", name: "Italiano", flag: "🇮🇹" },
];

export default function Header() {
  const { t, language, changeLanguage } = useTranslation();
  const { logout, user } = useAuth();
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);

  const currentLanguage = languages.find((lang) => lang.code === language) || languages[0];

  return (
    <header className="bg-white dark:bg-zinc-900 border-b border-zinc-200 dark:border-zinc-800 sticky top-0 z-50">
      <div className="mx-auto max-w-6xl px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
              {t("home.title")}
            </h1>
          </div>

          <div className="flex items-center gap-4">
            {user && (
              <span className="text-sm text-zinc-600 dark:text-zinc-400">
                {user.full_name}
              </span>
            )}

            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
                aria-label={t("header.language")}
              >
                <span className="text-lg">{currentLanguage.flag}</span>
                <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  {currentLanguage.code.toUpperCase()}
                </span>
              </button>

              {showLanguageMenu && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setShowLanguageMenu(false)}
                  />
                  <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-zinc-800 rounded-lg shadow-lg border border-zinc-200 dark:border-zinc-700 z-50">
                    <div className="py-1">
                      {languages.map((lang) => (
                        <button
                          key={lang.code}
                          onClick={() => {
                            changeLanguage(lang.code);
                            setShowLanguageMenu(false);
                          }}
                          className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-zinc-100 dark:hover:bg-zinc-700 transition-colors ${
                            language === lang.code
                              ? "bg-zinc-100 dark:bg-zinc-700 font-medium"
                              : ""
                          }`}
                        >
                          <span className="text-lg">{lang.flag}</span>
                          <span className="text-zinc-700 dark:text-zinc-300">
                            {lang.name}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Logout Button */}
            <Button
              onClick={logout}
              variant="outline"
              className="text-sm"
            >
              {t("header.logout")}
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
