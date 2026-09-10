import React, { useState } from "react";
import { useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import JharkhandLogo from "../components/JharkhandLogo";
import { UserPlus, LogIn, AlertCircle } from "lucide-react";

export default function RegisterPage() {
  const { navigate } = useLocation();
  const { t, currentLang } = useLanguage();
  const { register } = useAuth();
  const { addToast } = useToast();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    phone: "",
    role: "citizen",
    preferred_language: currentLang,
  });

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg("");

    if (!formData.name.trim()) {
      setErrorMsg("Please enter your full name.");
      return;
    }
    if (!formData.email.trim()) {
      setErrorMsg("Please enter a valid email address.");
      return;
    }
    if (formData.password.length < 6) {
      setErrorMsg("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);
    try {
      await register({
        name: formData.name.trim(),
        email: formData.email.trim().toLowerCase(),
        password: formData.password,
        phone: formData.phone.trim() || null,
        role: formData.role,
        preferred_language: formData.preferred_language,
      });

      addToast("Account created successfully! Welcome to SolveSphere.", "success");
      navigate("/dashboard");
    } catch (err) {
      console.error("Registration error:", err);
      setErrorMsg(err.message || "Failed to register. Please check details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-root">
      <div className="auth-card-container auth-card-lg">
        <div className="auth-brand-center">
          <JharkhandLogo size={42} showText={true} />
        </div>

        <div className="auth-header-text">
          <h2 className="auth-title">{t("btnRegister")}</h2>
          <p className="auth-subtitle">Join the SolveSphere civic innovation network</p>
        </div>

        {errorMsg && (
          <div className="form-error-banner">
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="auth-form">
          <div className="grid-2-col">
            <div className="form-field">
              <label className="form-label">{t("fieldName")} *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Birsa Munda"
                required
                className="form-input"
              />
            </div>

            <div className="form-field">
              <label className="form-label">{t("fieldEmail")} *</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="birsa@solvesphere.jh"
                required
                className="form-input"
              />
            </div>
          </div>

          <div className="grid-2-col">
            <div className="form-field">
              <label className="form-label">{t("fieldPassword")} *</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="Minimum 6 characters"
                required
                className="form-input"
              />
            </div>

            <div className="form-field">
              <label className="form-label">{t("fieldPhone")}</label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="9876543210"
                className="form-input"
              />
            </div>
          </div>

          <div className="grid-2-col">
            <div className="form-field">
              <label className="form-label">{t("fieldRole")} *</label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="form-select"
              >
                <option value="citizen">{t("roleCitizen")}</option>
                <option value="faculty">{t("roleFaculty")}</option>
                <option value="student">{t("roleStudent")}</option>
                <option value="admin">{t("roleAdmin")}</option>
              </select>
            </div>

            <div className="form-field">
              <label className="form-label">Preferred Language</label>
              <select
                value={formData.preferred_language}
                onChange={(e) => setFormData({ ...formData, preferred_language: e.target.value })}
                className="form-select"
              >
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="nag">नागपुरी (Nagpuri)</option>
                <option value="sat">ᱥᱟᱱᱛᱟᱲᱤ (Santali)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary btn-auth-submit"
          >
            <UserPlus size={16} />
            <span>{loading ? "Creating account..." : t("btnRegister")}</span>
          </button>
        </form>

        <div className="auth-footer-link">
          <span>Already registered?</span>
          <button
            type="button"
            onClick={() => navigate("/login")}
            className="link-btn"
          >
            {t("navLogin")}
          </button>
        </div>
      </div>
    </div>
  );
}
