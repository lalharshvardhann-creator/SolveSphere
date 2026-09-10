import React from "react";
import { Building2, MapPin, CheckCircle, ExternalLink, Sparkles } from "lucide-react";
import MatchScore from "./MatchScore";

export default function InstitutionCard({ institution, matchData = null, onConnect = null, onView = null }) {
  const isVerified = institution.verification_status === "verified";
  const expertiseList = institution.expertise_entries || [];

  return (
    <div className="institution-card">
      <div className="inst-card-header">
        <div className="inst-avatar">
          <Building2 size={22} className="text-green" />
        </div>
        <div className="inst-header-text">
          <div className="inst-title-row">
            <h4 className="inst-name">{institution.name}</h4>
            {isVerified && (
              <span className="inst-verified-badge" title="Government Verified HEI">
                <CheckCircle size={14} />
              </span>
            )}
          </div>
          <div className="inst-sub-meta">
            <span className="inst-type-pill">{institution.institution_type}</span>
            <span className="inst-district">
              <MapPin size={13} className="text-green" />
              {institution.district}
            </span>
          </div>
        </div>
      </div>

      {/* If this is rendered within a match context */}
      {matchData && (
        <div className="inst-match-spotlight">
          <div className="inst-match-score-row">
            <MatchScore score={matchData.match_score} />
          </div>

          {matchData.match_reason && (
            <div className="inst-match-reason-box">
              <div className="reason-label">
                <Sparkles size={14} className="text-green" />
                <strong>Why this matches:</strong>
              </div>
              <p className="reason-text">{matchData.match_reason}</p>
            </div>
          )}
        </div>
      )}

      {/* Description */}
      {institution.description && !matchData && (
        <p className="inst-description">
          {institution.description.length > 140
            ? `${institution.description.substring(0, 140)}...`
            : institution.description}
        </p>
      )}

      {/* Expertise entries preview */}
      {expertiseList.length > 0 && !matchData && (
        <div className="inst-expertise-tags">
          {expertiseList.map((exp) => (
            <span key={exp.id} className="expertise-chip">
              {exp.domain} {exp.subdomain ? `• ${exp.subdomain}` : ""}
            </span>
          ))}
        </div>
      )}

      {/* Card Actions */}
      <div className="inst-card-actions">
        {institution.website && (
          <a
            href={institution.website}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-inst-link"
          >
            <span>Website</span>
            <ExternalLink size={13} />
          </a>
        )}

        {onConnect && (
          <button
            type="button"
            onClick={() => onConnect(institution)}
            className="btn-inst-connect"
          >
            Connect
          </button>
        )}
      </div>
    </div>
  );
}
