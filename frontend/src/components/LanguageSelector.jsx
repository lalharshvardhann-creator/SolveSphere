import React, { useState, useRef, useEffect } from "react";
import { useLanguage } from "../context/LanguageContext";
import { Globe, ChevronDown, Check } from "lucide-react";

export default function LanguageSelector({ compact = false }) {
  const { currentLang, setLanguage, languages } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const currentObj = languages.find((l) => l.code === currentLang) || languages[0];

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="language-selector-wrapper" ref={dropdownRef}>
      <button
        type="button"
        className={`lang-btn ${compact ? "lang-btn-compact" : ""}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Select language"
        aria-expanded={isOpen}
      >
        <Globe size={16} className="lang-icon" />
        <span className="lang-current-label">
          {compact ? currentObj.code.toUpperCase() : currentObj.nativeName}
        </span>
        <ChevronDown size={14} className={`lang-arrow ${isOpen ? "rotate" : ""}`} />
      </button>

      {isOpen && (
        <div className="lang-dropdown-menu">
          <div className="lang-dropdown-header">Select Language / भाषा चुनें</div>
          {languages.map((lang) => {
            const isSelected = lang.code === currentLang;
            return (
              <button
                key={lang.code}
                type="button"
                className={`lang-option ${isSelected ? "selected" : ""}`}
                onClick={() => {
                  setLanguage(lang.code);
                  setIsOpen(false);
                }}
              >
                <div className="lang-option-text">
                  <span className="lang-native">{lang.nativeName}</span>
                  <span className="lang-name">({lang.name})</span>
                </div>
                {isSelected && <Check size={16} className="lang-check" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
