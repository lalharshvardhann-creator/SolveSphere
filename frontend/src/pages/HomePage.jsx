import React, { useState, useEffect } from "react";
import { useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import { api } from "../services/api";
import ChallengeCard from "../components/ChallengeCard";
import JharkhandMap from "../components/JharkhandMap";
import { useTranslatedChallenges } from "../hooks/useTranslatedContent";
import {
  PlusCircle,
  FolderKanban,
  Mic,
  BrainCircuit,
  Cpu,
  ArrowRight,
  Building2,
  Sparkles,
  CheckCircle,
} from "lucide-react";

export default function HomePage() {
  const { navigate } = useLocation();
  const { t } = useLanguage();
  const [recentChallenges, setRecentChallenges] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const res = await api.challenges.list({ page: 1, pageSize: 3 });
        if (res?.items) {
          setRecentChallenges(res.items);
        }
      } catch (err) {
        console.warn("Could not load recent challenges:", err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const flowSteps = [
    {
      num: "01",
      title: t("flowStep1Title"),
      desc: t("flowStep1Desc"),
      icon: <Mic size={22} className="text-green" />,
    },
    {
      num: "02",
      title: t("flowStep2Title"),
      desc: t("flowStep2Desc"),
      icon: <BrainCircuit size={22} className="text-green" />,
    },
    {
      num: "03",
      title: t("flowStep3Title"),
      desc: t("flowStep3Desc"),
      icon: <Cpu size={22} className="text-green" />,
    },
    {
      num: "04",
      title: t("flowStep4Title"),
      desc: t("flowStep4Desc"),
      icon: <Building2 size={22} className="text-green" />,
    },
    {
      num: "05",
      title: t("flowStep5Title"),
      desc: t("flowStep5Desc"),
      icon: <CheckCircle size={22} className="text-green" />,
    },
  ];

  const { translatedChallenges } = useTranslatedChallenges(recentChallenges);

  return (
    <div className="home-page-root">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container hero-container">
          {/* Replaced Badge: AI-Powered Community Platform */}
          <div className="hero-badge-pill">
            <Sparkles size={14} className="text-green" />
            <span>{t("heroBadge")}</span>
          </div>

          <h1 className="hero-main-title">{t("heroTitle")}</h1>

          <p className="hero-sub-text">{t("heroSubtitle")}</p>

          <div className="hero-cta-group">
            <button
              type="button"
              onClick={() => navigate("/report")}
              className="btn-primary btn-hero"
            >
              <PlusCircle size={18} />
              <span>{t("btnReportProblem")}</span>
            </button>

            <button
              type="button"
              onClick={() => navigate("/challenges")}
              className="btn-secondary btn-hero"
            >
              <FolderKanban size={18} />
              <span>{t("btnViewChallenges")}</span>
            </button>
          </div>
        </div>
      </section>

      {/* 5-Step Civic AI Lifecycle Flow */}
      <section className="flow-section">
        <div className="container">
          <div className="section-header-center">
            <span className="section-kicker">Transparent Methodology</span>
            <h2 className="section-heading">{t("flowTitle")}</h2>
          </div>

          <div className="flow-grid-5">
            {flowSteps.map((step) => (
              <div key={step.num} className="flow-card">
                <div className="flow-card-header">
                  <div className="flow-icon-circle">{step.icon}</div>
                  <span className="flow-step-num">{step.num}</span>
                </div>
                <h3 className="flow-step-title">{step.title}</h3>
                <p className="flow-step-desc">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Regional Reach / Jharkhand Heatmap Section */}
      <section className="jharkhand-section">
        <div className="container">
          <JharkhandMap />
        </div>
      </section>

      {/* Recent Challenges Section */}
      <section className="recent-challenges-section">
        <div className="container">
          <div className="section-header-row">
            <div>
              <span className="section-kicker">Community Challenges</span>
              <h2 className="section-heading">Recent Reports</h2>
            </div>

            <button
              type="button"
              onClick={() => navigate("/challenges")}
              className="btn-view-all"
            >
              <span>{t("btnViewChallenges")}</span>
              <ArrowRight size={16} />
            </button>
          </div>

          {loading ? (
            <div className="loading-state-box">
              <div className="spinner"></div>
              <span>{t("loading")}</span>
            </div>
          ) : translatedChallenges.length > 0 ? (
            <div className="challenges-grid">
              {translatedChallenges.map((challenge) => (
                <ChallengeCard key={challenge.id} challenge={challenge} />
              ))}
            </div>
          ) : (
            <div className="empty-state-box">
              <p>No challenges submitted yet.</p>
              <button
                type="button"
                onClick={() => navigate("/report")}
                className="btn-primary mt-3"
              >
                {t("btnReportProblem")}
              </button>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
