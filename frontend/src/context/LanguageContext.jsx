import React, { createContext, useContext, useState, useEffect } from "react";
import { LANGUAGES, translations } from "../translations";

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [currentLang, setCurrentLang] = useState(() => {
    return localStorage.getItem("solvesphere_lang") || "en";
  });

  const setLanguage = (langCode) => {
    if (translations[langCode]) {
      setCurrentLang(langCode);
      localStorage.setItem("solvesphere_lang", langCode);
    }
  };

  const t = (key) => {
    const langDict = translations[currentLang] || translations.en;
    return langDict[key] || translations.en[key] || key;
  };

  const getSpeechCode = () => {
    const langObj = LANGUAGES.find((l) => l.code === currentLang);
    return langObj ? langObj.speechCode : "en-IN";
  };

  return (
    <LanguageContext.Provider
      value={{
        currentLang,
        setLanguage,
        t,
        languages: LANGUAGES,
        speechCode: getSpeechCode(),
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
