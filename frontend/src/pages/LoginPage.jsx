import React, { useState } from "react";
import { useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import JharkhandLogo from "../components/JharkhandLogo";
import { LogIn, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const { navigate } = useLocation();
  const { t } = useLanguage();
  const { login } = useAuth();
  const { addToast } = useToast();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      await login(email, password);
      addToast("Logged in successfully!", "success");
      navigate("/dashboard");
    } catch (err) {
      console.error("Login failed:", err);
      setErrorMsg(err.message || "Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-root">
      <div className="auth-card-container">
        <div className="auth-brand-center">
          <JharkhandLogo size={42} showText={true} />
        </div>

        <div className="auth-header-text">
          <h2 className="auth-title">{t("loginTitle")}</h2>
          <p className="auth-subtitle">{t("loginSubtitle")}</p>
        </div>

        {errorMsg && (
          <div className="form-error-banner">
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="auth-form">
          <div className="form-field">
            <label className="form-label">{t("fieldEmail")} *</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="citizen@solvesphere.jh"
              required
              className="form-input"
            />
          </div>

          <div className="form-field">
            <label className="form-label">{t("fieldPassword")} *</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="form-input"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary btn-auth-submit"
          >
            <LogIn size={16} />
            <span>{loading ? "Authenticating..." : t("btnLogin")}</span>
          </button>
        </form>

        <div className="auth-footer-link">
          <span>Don't have an account?</span>
          <button
            type="button"
            onClick={() => navigate("/register")}
            className="link-btn"
          >
            {t("btnRegister")}
          </button>
        </div>
      </div>
    </div>
  );
}

