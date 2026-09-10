import React from "react";
import { RouterProvider, useLocation } from "./router";
import { LanguageProvider, useLanguage } from "./context/LanguageContext";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import Navbar from "./components/Navbar";
import JharkhandLogo from "./components/JharkhandLogo";

import HomePage from "./pages/HomePage";
import ReportProblemPage from "./pages/ReportProblemPage";
import ChallengesListPage from "./pages/ChallengesListPage";
import ChallengeDetailPage from "./pages/ChallengeDetailPage";
import InstitutionsPage from "./pages/InstitutionsPage";
import CitizenDashboard from "./pages/CitizenDashboard";
import ImpactPage from "./pages/ImpactPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

function PageRouter() {
  const { currentPath } = useLocation();

  if (currentPath === "/" || currentPath === "") {
    return <HomePage />;
  }
  if (currentPath.startsWith("/report")) {
    return <ReportProblemPage />;
  }
  if (currentPath.startsWith("/challenges/")) {
    return <ChallengeDetailPage />;
  }
  if (currentPath === "/challenges") {
    return <ChallengesListPage />;
  }
  if (currentPath === "/institutions") {
    return <InstitutionsPage />;
  }
  if (currentPath === "/dashboard") {
    return <CitizenDashboard />;
  }
  if (currentPath === "/impact") {
    return <ImpactPage />;
  }
  if (currentPath === "/login") {
    return <LoginPage />;
  }
  if (currentPath === "/register") {
    return <RegisterPage />;
  }

  return <HomePage />;
}

function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="footer-root">
      <div className="container footer-container">
        <div className="footer-top-row">
          <div className="footer-brand-column">
            <JharkhandLogo size={32} showText={true} />
            <p className="footer-tagline">{t("tagline")}</p>
            <p className="footer-subtext">{t("subtagline")}</p>
          </div>

          <div className="footer-links-group">
            <div className="footer-col">
              <span className="footer-col-title">Citizens</span>
              <a href="#/report">{t("navReport")}</a>
              <a href="#/challenges">{t("navChallenges")}</a>
              <a href="#/dashboard">{t("navDashboard")}</a>
            </div>

            <div className="footer-col">
              <span className="footer-col-title">Academia</span>
              <a href="#/institutions">{t("navInstitutions")}</a>
              <a href="#/impact">{t("navImpact")}</a>
              <a href="#/login">{t("navLogin")}</a>
            </div>

            <div className="footer-col">
              <span className="footer-col-title">State Reach</span>
              <span>24 Districts of Jharkhand</span>
              <span>Ranchi • Dhanbad • Jamshedpur</span>
              <span>Bokaro • Deoghar • Hazaribagh</span>
            </div>
          </div>
        </div>

        <div className="footer-bottom-row">
          <p>© {new Date().getFullYear()} SolveSphere • AI-Powered Community Platform</p>
          <div className="footer-lang-pill">
            <span>5 Regional Languages Supported</span>
          </div>
        </div>

      </div>
    </footer>
  );
}

export default function App() {
  return (
    <RouterProvider>
      <LanguageProvider>
        <AuthProvider>
          <ToastProvider>
            <div className="app-layout">
              <Navbar />
              <main className="main-content">
                <PageRouter />
              </main>
              <Footer />
            </div>
          </ToastProvider>
        </AuthProvider>
      </LanguageProvider>
    </RouterProvider>
  );
}
