import React, { useState, useEffect } from "react";
import { useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import ChallengeCard from "../components/ChallengeCard";
import { useTranslatedChallenges } from "../hooks/useTranslatedContent";
import {
  PlusCircle,
  BrainCircuit,
  Building2,
  CheckCircle,
  FolderKanban,
  User,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

export default function CitizenDashboard() {
  const { navigate } = useLocation();
  const { t } = useLanguage();
  const { user } = useAuth();

  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("all"); // 'all', 'analyzed', 'matched', 'resolved'

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const res = await api.challenges.list({ page: 1, pageSize: 50 });
        const allItems = res?.items || [];

        // Filter challenges submitted by the logged-in user if available
        const userChallenges = user?.id
          ? allItems.filter((c) => c.submitted_by === user.id)
          : allItems;

        // Fetch stored institution matches for each challenge in parallel
        const matchPromises = userChallenges.map((c) =>
          api.challenges.getMatches(c.id).catch(() => ({ matches: [] }))
        );
        const matchResults = await Promise.allSettled(matchPromises);

        const enriched = userChallenges.map((c, idx) => {
          const mRes = matchResults[idx];
          const matches =
            mRes.status === "fulfilled" && mRes.value?.matches
              ? mRes.value.matches
              : [];
          return {
            ...c,
            matches,
            matchCount: matches.length,
          };
        });

        setChallenges(enriched);
      } catch (err) {
        console.warn("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [user?.id]);

  const totalCount = challenges.length;
  const analyzedCount = challenges.filter((c) => c.priority_score !== null).length;

  // Aggregate unique matched institutions across all challenges of the logged-in user
  const allMatchedInstitutionIds = new Set();
  challenges.forEach((c) => {
    if (c.matches && Array.isArray(c.matches)) {
      c.matches.forEach((m) => {
        if (m.institution_id) {
          allMatchedInstitutionIds.add(m.institution_id);
        }
      });
    }
  });
  const matchedInstitutionsCount = allMatchedInstitutionIds.size;

  const challengesWithMatches = challenges.filter(
    (c) =>
      (c.matches && c.matches.length > 0) ||
      c.status === "assigned" ||
      c.status === "in_progress"
  );
  const resolvedCount = challenges.filter((c) => c.status === "resolved").length;

  const filtered = challenges.filter((c) => {
    if (activeTab === "analyzed") return c.priority_score !== null;
    if (activeTab === "matched")
      return (
        (c.matches && c.matches.length > 0) ||
        c.status === "assigned" ||
        c.status === "in_progress"
      );
    if (activeTab === "resolved") return c.status === "resolved";
    return true;
  });

  const { translatedChallenges, isTranslating } = useTranslatedChallenges(filtered);

  return (
    <div className="dashboard-page-root">
      <div className="container">
        {/* User Welcome Banner */}
        <div className="dashboard-hero-banner">
          <div className="dashboard-user-info">
            <div className="dash-avatar-circle">
              <User size={28} />
            </div>
            <div>
              <div className="dash-role-badge">
                <ShieldCheck size={13} className="text-green" />
                <span>{user?.role ? user.role.toUpperCase() : "CITIZEN"} DASHBOARD</span>
              </div>
              <h1 className="dash-welcome-name">
                Welcome back, {user?.name || "Citizen of Jharkhand"}
              </h1>
              <p className="dash-welcome-email">{user?.email || "citizen@solvesphere.jh"}</p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => navigate("/report")}
            className="btn-primary btn-dash-report"
          >
            <PlusCircle size={18} />
            <span>{t("btnReportProblem")}</span>
          </button>
        </div>

        {/* 4 Metric Cards */}
        <div className="dash-stats-grid">
          <div
            onClick={() => setActiveTab("all")}
            className={`dash-stat-card ${activeTab === "all" ? "stat-card-active" : ""}`}
          >
            <div className="stat-card-top">
              <span className="stat-label">{t("statTotal")}</span>
              <FolderKanban size={20} className="text-green" />
            </div>
            <span className="stat-value">{totalCount}</span>
            <span className="stat-sub">Active community issues</span>
          </div>

          <div
            onClick={() => setActiveTab("analyzed")}
            className={`dash-stat-card ${activeTab === "analyzed" ? "stat-card-active" : ""}`}
          >
            <div className="stat-card-top">
              <span className="stat-label">{t("statAIAnalyzed")}</span>
              <BrainCircuit size={20} className="text-green" />
            </div>
            <span className="stat-value">{analyzedCount}</span>
            <span className="stat-sub">Scored by Gemini AI</span>
          </div>

          <div
            onClick={() => setActiveTab("matched")}
            className={`dash-stat-card ${activeTab === "matched" ? "stat-card-active" : ""}`}
          >
            <div className="stat-card-top">
              <span className="stat-label">{t("statMatched")}</span>
              <Building2 size={20} className="text-green" />
            </div>
            <span className="stat-value">{matchedInstitutionsCount}</span>
            <span className="stat-sub">Matched to HEIs</span>
          </div>

          <div
            onClick={() => setActiveTab("resolved")}
            className={`dash-stat-card ${activeTab === "resolved" ? "stat-card-active" : ""}`}
          >
            <div className="stat-card-top">
              <span className="stat-label">{t("statResolved")}</span>
              <CheckCircle size={20} className="text-green" />
            </div>
            <span className="stat-value">{resolvedCount}</span>
            <span className="stat-sub">Solutions deployed</span>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="dash-filter-tabs">
          <button
            type="button"
            className={`dash-tab ${activeTab === "all" ? "active" : ""}`}
            onClick={() => setActiveTab("all")}
          >
            All Problems ({totalCount})
          </button>
          <button
            type="button"
            className={`dash-tab ${activeTab === "analyzed" ? "active" : ""}`}
            onClick={() => setActiveTab("analyzed")}
          >
            AI Analyzed ({analyzedCount})
          </button>
          <button
            type="button"
            className={`dash-tab ${activeTab === "matched" ? "active" : ""}`}
            onClick={() => setActiveTab("matched")}
          >
            Matched HEIs ({challengesWithMatches.length})
          </button>
          <button
            type="button"
            className={`dash-tab ${activeTab === "resolved" ? "active" : ""}`}
            onClick={() => setActiveTab("resolved")}
          >
            Resolved ({resolvedCount})
          </button>

          {isTranslating && (
            <span className="translating-tag ml-auto">
              <Sparkles size={12} className="animate-spin text-green" />
              <span>Translating content...</span>
            </span>
          )}
        </div>

        {/* Challenges List */}
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
            <FolderKanban size={40} className="text-muted" />
            <p>No challenges found under this category.</p>
            <button
              type="button"
              onClick={() => navigate("/report")}
              className="btn-primary mt-2"
            >
              {t("btnReportProblem")}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
