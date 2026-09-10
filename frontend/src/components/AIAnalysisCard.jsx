import React from "react";
import { useLanguage } from "../context/LanguageContext";
import {
  BrainCircuit,
  Sparkles,
  Target,
  Gauge,
  Tag,
  Lightbulb,
  Cpu,
  CheckCircle2,
} from "lucide-react";
import PriorityBadge from "./PriorityBadge";

export default function AIAnalysisCard({ analysis, onRunAnalysis = null, loading = false }) {
  const { t } = useLanguage();

  if (!analysis) {
    return (
      <div className="ai-empty-card">
        <div className="ai-empty-icon">
          <BrainCircuit size={32} className="text-green" />
        </div>
        <div className="ai-empty-text">
          <h4>{t("aiTitle")}</h4>
          <p>{t("aiNotAnalyzedYet")}</p>
        </div>
        {onRunAnalysis && (
          <button
            type="button"
            onClick={onRunAnalysis}
            disabled={loading}
            className="btn-primary btn-run-ai"
          >
            <Sparkles size={16} className={loading ? "animate-spin" : ""} />
            <span>{loading ? t("aiBtnRunning") : t("aiBtnRun")}</span>
          </button>
        )}
      </div>
    );
  }

  // Parse keywords and suggestions if they are strings
  const keywordsList = typeof analysis.keywords === "string"
    ? analysis.keywords.split(",").map((k) => k.trim()).filter(Boolean)
    : Array.isArray(analysis.keywords) ? analysis.keywords : [];

  const expertiseList = typeof analysis.required_expertise === "string"
    ? analysis.required_expertise.split(";").map((e) => e.trim()).filter(Boolean)
    : [];

  const confidencePct = analysis.confidence_score
    ? Math.round(analysis.confidence_score * 100)
    : 95;

  return (
    <div className="ai-analysis-container">
      <div className="ai-header-bar">
        <div className="ai-title-badge">
          <BrainCircuit size={20} className="text-green" />
          <h3>{t("aiTitle")}</h3>
          <span className="model-version-tag">{analysis.model_version || "Gemini 2.5"}</span>
        </div>

        <div className="ai-meta-pills">
          <PriorityBadge score={analysis.priority_score} />

          <div className="confidence-pill" title="AI Confidence Score">
            <Gauge size={14} className="text-green" />
            <span>Confidence: <strong>{confidencePct}%</strong></span>
          </div>
        </div>
      </div>

      {/* Problem Summary (Gemini generated) */}
      {analysis.problem_summary && (
        <div className="ai-summary-block">
          <div className="summary-label-row">
            <Target size={16} className="text-green" />
            <strong>{t("aiProblemSummary")}</strong>
          </div>
          <p className="summary-content-text">{analysis.problem_summary}</p>
        </div>
      )}

      {/* Classified Domain Grid */}
      <div className="ai-classification-grid">
        <div className="ai-stat-box">
          <span className="ai-stat-label">{t("aiDetectedCategory")}</span>
          <span className="ai-stat-val text-green font-semibold">
            {analysis.category || "General"}
          </span>
        </div>

        <div className="ai-stat-box">
          <span className="ai-stat-label">{t("aiDetectedSubcategory")}</span>
          <span className="ai-stat-val font-semibold">
            {analysis.subcategory || "N/A"}
          </span>
        </div>

        <div className="ai-stat-box">
          <span className="ai-stat-label">Urgency Score</span>
          <span className="ai-stat-val">
            <strong className="text-green">{analysis.priority_score || 8.0}</strong> / 10.0
          </span>
        </div>
      </div>

      {/* Required Expertise & Solutions */}
      {expertiseList.length > 0 && (
        <div className="ai-section-block">
          <div className="section-label-row">
            <Lightbulb size={16} className="text-green" />
            <strong>{t("aiRequiredExpertise")}</strong>
          </div>
          <ul className="solution-directions-list">
            {expertiseList.map((item, idx) => (
              <li key={idx} className="solution-item">
                <CheckCircle2 size={16} className="text-green flex-shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Keywords Chips */}
      {keywordsList.length > 0 && (
        <div className="ai-keywords-block">
          <div className="keywords-label-row">
            <Tag size={14} className="text-green" />
            <span>{t("aiKeywords")}:</span>
          </div>
          <div className="keywords-chip-row">
            {keywordsList.map((kw, i) => (
              <span key={i} className="ai-keyword-tag">
                #{kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
