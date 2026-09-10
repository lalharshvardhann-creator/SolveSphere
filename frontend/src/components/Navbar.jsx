import React, { useState } from "react";
import { Link, useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import JharkhandLogo from "./JharkhandLogo";
import LanguageSelector from "./LanguageSelector";
import {
  Menu,
  X,
  PlusCircle,
  FolderKanban,
  Building2,
  LayoutDashboard,
  BarChart3,
  User,
  LogOut,
  LogIn,
} from "lucide-react";

export default function Navbar() {
  const { t } = useLanguage();
  const { user, isAuthenticated, logout } = useAuth();
  const { currentPath, navigate } = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { path: "/", label: t("navHome"), icon: null },
    { path: "/report", label: t("navReport"), icon: <PlusCircle size={15} />, highlight: true },
    { path: "/challenges", label: t("navChallenges"), icon: <FolderKanban size={15} /> },
    { path: "/institutions", label: t("navInstitutions"), icon: <Building2 size={15} /> },
    { path: "/dashboard", label: t("navDashboard"), icon: <LayoutDashboard size={15} /> },
    { path: "/impact", label: t("navImpact"), icon: <BarChart3 size={15} /> },
  ];

  return (
    <header className="navbar-root">
      <div className="navbar-container">
        {/* Brand / Logo */}
        <a
          href="#/"
          onClick={(e) => {
            e.preventDefault();
            navigate("/");
          }}
          className="navbar-brand"
        >
          <JharkhandLogo size={36} showText={true} />
        </a>

        {/* Desktop Navigation Links */}
        <nav className="navbar-links" aria-label="Main Navigation">
          {navLinks.map((item) => {
            const isActive = currentPath === item.path;
            return (
              <a
                key={item.path}
                href={`#${item.path}`}
                onClick={(e) => {
                  e.preventDefault();
                  navigate(item.path);
                }}
                className={`nav-link ${isActive ? "nav-link-active" : ""} ${
                  item.highlight ? "nav-link-highlight" : ""
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>

        {/* Right Controls: Language Selector + Auth Action */}
        <div className="navbar-right-controls">
          <LanguageSelector />

          {isAuthenticated ? (
            <div className="auth-profile-group">
              <button
                type="button"
                onClick={() => navigate("/dashboard")}
                className="user-pill-btn"
                title="Go to Dashboard"
              >
                <div className="avatar-circle">
                  {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
                </div>
                <span className="user-pill-name">{user?.name || "Citizen"}</span>
              </button>

              <button
                type="button"
                onClick={logout}
                className="btn-nav-logout"
                title={t("navLogout")}
              >
                <LogOut size={14} />
                <span>{t("navLogout") || "Logout"}</span>
              </button>
            </div>
          ) : (
            <div className="auth-btn-group">
              <button
                type="button"
                onClick={() => navigate("/login")}
                className="btn-nav-login"
              >
                <LogIn size={15} />
                <span>{t("navLogin")}</span>
              </button>
            </div>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            type="button"
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="mobile-nav-drawer">
          <div className="mobile-nav-links">
            {navLinks.map((item) => (
              <a
                key={item.path}
                href={`#${item.path}`}
                onClick={(e) => {
                  e.preventDefault();
                  navigate(item.path);
                  setMobileMenuOpen(false);
                }}
                className={`mobile-nav-link ${currentPath === item.path ? "active" : ""}`}
              >
                {item.icon}
                <span>{item.label}</span>
              </a>
            ))}

            <div className="mobile-auth-section">
              {isAuthenticated ? (
                <button
                  type="button"
                  onClick={() => {
                    logout();
                    setMobileMenuOpen(false);
                  }}
                  className="btn-mobile-logout"
                >
                  <LogOut size={16} />
                  <span>{t("navLogout")} ({user?.name})</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    navigate("/login");
                    setMobileMenuOpen(false);
                  }}
                  className="btn-mobile-login"
                >
                  <LogIn size={16} />
                  <span>{t("navLogin")} / {t("navRegister")}</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
