import React, { useState, useEffect } from "react";
import { useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";
import PriorityBadge from "../components/PriorityBadge";
import AIAnalysisCard from "../components/AIAnalysisCard";
import InstitutionCard from "../components/InstitutionCard";
import Timeline from "../components/Timeline";
import { useTranslatedChallengeDetail } from "../hooks/useTranslatedContent";
import {
  ArrowLeft,
  MapPin,
  Users,
  Calendar,
  Sparkles,
  Building2,
  AlertCircle,
  Send,
} from "lucide-react";

export default function ChallengeDetailPage() {
  const { currentPath, navigate } = useLocation();
  const { t } = useLanguage();
  const { isAuthenticated } = useAuth();
  const { addToast } = useToast();

  // Extract challenge ID from path (e.g. /challenges/3)
  const challengeId = currentPath.split("/")[2];

  const [challenge, setChallenge] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [matchLoading, setMatchLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [connectModal, setConnectModal] = useState(null);

  useEffect(() => {
    async function loadChallengeDetails() {
      if (!challengeId) return;
      setLoading(true);
      setErrorMsg("");

      try {
        const chData = await api.challenges.getById(challengeId);
        setChallenge(chData);

        // Try loading stored AI analysis
        try {
          const aiData = await api.challenges.getAnalysis(challengeId);
          setAiAnalysis(aiData);
        } catch {
          // No AI analysis yet
        }

        // Try loading stored institution matches
        try {
          const matchData = await api.challenges.getMatches(challengeId);
          if (matchData?.matches) {
            setMatches(matchData.matches);
          }
        } catch {
          // No matches yet
        }
      } catch (err) {
        setErrorMsg(err.message || "Failed to load challenge details.");
      } finally {
        setLoading(false);
      }
    }
    loadChallengeDetails();
  }, [challengeId]);

  const handleRunAI = async () => {
    if (!isAuthenticated) {
      addToast("Please login to trigger Gemini AI analysis", "info");
      navigate("/login");
      return;
    }

    setAiLoading(true);
    try {
      const res = await api.challenges.analyze(challengeId);
      setAiAnalysis(res);
      addToast("Gemini AI analysis completed and persisted!", "success");

      // Reload challenge to update priority_score
      const updatedCh = await api.challenges.getById(challengeId);
      setChallenge(updatedCh);
    } catch (err) {
      addToast(err.message || "AI analysis failed.", "error");
    } finally {
      setAiLoading(false);
    }
  };

  const handleRunMatching = async () => {
    if (!isAuthenticated) {
      addToast("Please login to match institutions", "info");
      navigate("/login");
      return;
    }

    if (!aiAnalysis) {
      addToast("Please run Gemini AI analysis first before matching institutions.", "info");
      return;
    }

    setMatchLoading(true);
    try {
      const res = await api.challenges.match(challengeId);
      if (res?.matches) {
        setMatches(res.matches);
        addToast(`Found ${res.matches.length} matching institutions!`, "success");
      }
    } catch (err) {
      addToast(err.message || "Matching failed.", "error");
    } finally {
      setMatchLoading(false);
    }
  };

  const handleConnect = (inst) => {
    setConnectModal(inst);
  };

  const submitCollaborationInterest = () => {
    addToast(`Collaboration request sent to ${connectModal.name}!`, "success");
    setConnectModal(null);
  };

  if (loading) {
    return (
      <div className="container py-8">
        <div className="loading-state-box">
          <div className="spinner"></div>
          <span>{t("loading")}</span>
        </div>
      </div>
    );
  }

  if (errorMsg || !challenge) {
    return (
      <div className="container py-8">
        <div className="empty-state-box">
          <AlertCircle size={40} className="text-red-500" />
          <h3>{errorMsg || "Challenge not found"}</h3>
          <button
            type="button"
            onClick={() => navigate("/challenges")}
            className="btn-primary mt-3"
          >
            <ArrowLeft size={16} />
            <span>Back to Challenges</span>
          </button>
        </div>
      </div>
    );
  }

  const {
    translatedChallenge,
    translatedAIAnalysis,
    translatedMatches,
    isTranslating,
  } = useTranslatedChallengeDetail(challenge, aiAnalysis, matches);

  const displayChallenge = translatedChallenge || challenge;
  const displayAI = translatedAIAnalysis || aiAnalysis;
  const displayMatches = translatedMatches || matches;

  const district = displayChallenge.location?.district || "Jharkhand";
  const locationDetails = [
    displayChallenge.location?.village,
    displayChallenge.location?.panchayat,
    displayChallenge.location?.block,
    district,
    "Jharkhand",
  ].filter(Boolean).join(", ");

  return (
    <div className="challenge-detail-root">
      <div className="container">
        {/* Navigation Breadcrumb */}
        <div className="detail-breadcrumb-bar">
          <button
            type="button"
            onClick={() => navigate("/challenges")}
            className="btn-back-link"
          >
            <ArrowLeft size={16} />
            <span>All Challenges</span>
          </button>

          <div className="breadcrumb-right-group">
            {isTranslating && (
              <span className="translating-tag">
                <Sparkles size={12} className="animate-spin text-green" />
                <span>Translating content...</span>
              </span>
            )}
            <span className="breadcrumb-id">Challenge #{displayChallenge.id}</span>
          </div>
        </div>

        {/* Main Title Header Card */}
        <div className="detail-hero-card">
          <div className="detail-top-badges">
            <span className="category-pill">{displayChallenge.category}</span>
            {displayChallenge.subcategory && (
              <span className="subcategory-pill">{displayChallenge.subcategory}</span>
            )}
            <StatusBadge status={displayChallenge.status} />
          </div>

          <h1 className="detail-challenge-title">{displayChallenge.title}</h1>

          <div className="detail-meta-strip">
            <div className="meta-strip-item">
              <MapPin size={16} className="text-green" />
              <span>{locationDetails}</span>
            </div>

            {displayChallenge.people_affected > 0 && (
              <div className="meta-strip-item">
                <Users size={16} className="text-green" />
                <span>~{displayChallenge.people_affected.toLocaleString()} People Affected</span>
              </div>
            )}

            <div className="meta-strip-item">
              <Calendar size={16} className="text-green" />
              <span>Reported on {new Date(displayChallenge.created_at).toLocaleDateString()}</span>
            </div>
          </div>

          <div className="detail-priority-meter-row">
            <PriorityBadge score={displayChallenge.priority_score} />
          </div>
        </div>

        {/* Civic Progress Lifecycle Timeline */}
        <div className="timeline-section-card">
          <div className="timeline-card-header">
            <span className="section-kicker">Resolution Pipeline</span>
            <h4>Progress Status</h4>
          </div>
          <Timeline
            currentStatus={displayChallenge.status}
            hasAI={!!displayAI}
            hasMatch={displayMatches.length > 0}
          />
        </div>

        {/* Problem Description Card */}
        <div className="detail-section-card">
          <h3 className="section-card-title">Problem Description</h3>
          <p className="detail-description-text">{displayChallenge.description}</p>
        </div>

        {/* AI Analysis Section */}
        <div className="detail-ai-section">
          <div className="section-header-row">
            <div>
              <span className="section-kicker">Gemini AI Intelligence</span>
              <h2 className="section-heading">{t("aiTitle")}</h2>
            </div>

            {!displayAI && (
              <button
                type="button"
                onClick={handleRunAI}
                disabled={aiLoading}
                className="btn-primary"
              >
                <Sparkles size={16} className={aiLoading ? "animate-spin" : ""} />
                <span>{aiLoading ? t("aiBtnRunning") : t("aiBtnRun")}</span>
              </button>
            )}
          </div>

          <AIAnalysisCard
            analysis={displayAI}
            onRunAnalysis={handleRunAI}
            loading={aiLoading}
          />
        </div>

        {/* Institution Matching Section */}
        <div className="detail-matching-section">
          <div className="section-header-row">
            <div>
              <span className="section-kicker">Explainable Academic Matching</span>
              <h2 className="section-heading">{t("matchTitle")}</h2>
            </div>

            <button
              type="button"
              onClick={handleRunMatching}
              disabled={matchLoading}
              className="btn-primary"
            >
              <Building2 size={16} className={matchLoading ? "animate-spin" : ""} />
              <span>{matchLoading ? t("matchBtnRunning") : t("matchBtnRun")}</span>
            </button>
          </div>

          {displayMatches.length > 0 ? (
            <div className="institution-matches-grid">
              {displayMatches.map((item, idx) => (
                <div key={item.institution_id || idx} className="match-item-wrapper">
                  <div className="match-rank-badge">#{idx + 1} Recommended Match</div>
                  <InstitutionCard
                    institution={{
                      id: item.institution_id,
                      name: item.institution_name,
                      institution_type: item.institution_type,
                      district: item.district,
                      verification_status: "verified",
                    }}
                    matchData={item}
                    onConnect={handleConnect}
                  />
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-matches-card">
              <Building2 size={36} className="text-muted" />
              <h4>{t("matchTitle")}</h4>
              <p>
                {aiAnalysis
                  ? "Click 'Find Matching Institutions' to run our explainable algorithm and rank universities."
                  : t("matchRequiresAI")}
              </p>
              {aiAnalysis && (
                <button
                  type="button"
                  onClick={handleRunMatching}
                  disabled={matchLoading}
                  className="btn-primary mt-2"
                >
                  <Sparkles size={16} />
                  <span>{matchLoading ? t("matchBtnRunning") : t("matchBtnRun")}</span>
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Connect / Collaboration Modal */}
      {connectModal && (
        <div className="modal-backdrop">
          <div className="modal-content-box">
            <div className="modal-header">
              <h3>Collaborate with {connectModal.name}</h3>
              <button
                type="button"
                onClick={() => setConnectModal(null)}
                className="modal-close-btn"
              >
                &times;
              </button>
            </div>
            <div className="modal-body">
              <p>
                Submit an official expression of collaboration interest to the faculty and research cell at <strong>{connectModal.name}</strong> for Challenge #{challenge.id}.
              </p>
              <div className="form-field mt-3">
                <label className="form-label">Note to Institution (Optional)</label>
                <textarea
                  rows={3}
                  placeholder="e.g. Seeking support for immediate groundwater filtration deployment..."
                  className="form-textarea"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                type="button"
                onClick={() => setConnectModal(null)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={submitCollaborationInterest}
                className="btn-primary"
              >
                <Send size={15} />
                <span>Submit Collaboration</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
