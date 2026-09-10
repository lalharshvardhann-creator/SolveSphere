import React from "react";
import { useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import StatusBadge from "./StatusBadge";
import PriorityBadge from "./PriorityBadge";
import { MapPin, Users, Calendar, ArrowRight, BrainCircuit } from "lucide-react";

export default function ChallengeCard({ challenge, onQuickAction = null }) {
  const { navigate } = useLocation();
  const { t } = useLanguage();

  const district = challenge.location?.district || "Jharkhand";
  const dateStr = challenge.created_at
    ? new Date(challenge.created_at).toLocaleDateString()
    : "Recently";

  return (
    <div className="challenge-card">
      <div className="card-top-row">
        <span className="category-pill">{challenge.category || "General"}</span>
        <StatusBadge status={challenge.status} />
      </div>

      <h3 className="card-title">
        <a
          href={`#/challenges/${challenge.id}`}
          onClick={(e) => {
            e.preventDefault();
            navigate(`/challenges/${challenge.id}`);
          }}
        >
          {challenge.title}
        </a>
      </h3>

      <p className="card-description">
        {challenge.description?.length > 120
          ? `${challenge.description.substring(0, 120)}...`
          : challenge.description}
      </p>

      <div className="card-meta-list">
        <div className="meta-item">
          <MapPin size={14} className="meta-icon text-green" />
          <span>{district}</span>
        </div>

        {challenge.people_affected > 0 && (
          <div className="meta-item">
            <Users size={14} className="meta-icon" />
            <span>~{challenge.people_affected.toLocaleString()} affected</span>
          </div>
        )}

        <div className="meta-item">
          <Calendar size={14} className="meta-icon" />
          <span>{dateStr}</span>
        </div>
      </div>

      <div className="card-bottom-row">
        <PriorityBadge score={challenge.priority_score} />

        <button
          type="button"
          onClick={() => navigate(`/challenges/${challenge.id}`)}
          className="btn-card-action"
        >
          <span>{t("viewDetails")}</span>
          <ArrowRight size={14} />
        </button>
      </div>
    </div>
  );
}
