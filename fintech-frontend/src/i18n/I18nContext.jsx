import { createContext, useContext, useState, useEffect } from "react";
import esTranslations from "./translations/es.json";
import enTranslations from "./translations/en.json";
import ptTranslations from "./translations/pt.json";
import itTranslations from "./translations/it.json";

const translations = {
  es: esTranslations,
  en: enTranslations,
  pt: ptTranslations,
  it: itTranslations,
};

const I18nContext = createContext();

export function I18nProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem("language");
    return saved || "es";
  });

  useEffect(() => {
    localStorage.setItem("language", language);
  }, [language]);

  const t = (key, values = {}) => {
    const keys = key.split(".");
    let value = translations[language];
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    if (!value && language !== "es") {
      value = translations.es;
      for (const k of keys) {
        value = value?.[k];
      }
    }
    
    if (typeof value === "string") {
      return Object.keys(values).reduce((acc, currentKey) => {
        const placeholder = `{{${currentKey}}}`;
        return acc.split(placeholder).join(values[currentKey] ?? "");
      }, value);
    }
    
    return value || key;
  };

  const changeLanguage = (lang) => {
    if (translations[lang]) {
      setLanguage(lang);
    }
  };

  return (
    <I18nContext.Provider value={{ language, t, changeLanguage }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useTranslation() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useTranslation must be used within I18nProvider");
  }
  return context;
}
