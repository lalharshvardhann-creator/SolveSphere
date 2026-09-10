import React from "react";
import { Award, Zap } from "lucide-react";

export default function MatchScore({ score }) {
  const num = typeof score === "number" ? score : parseFloat(score) || 0;
  const clamped = Math.min(100, Math.max(0, num));

  let tierClass = "match-tier-low";
  let tierLabel = "Low Match";

  if (clamped >= 80) {
    tierClass = "match-tier-high";
    tierLabel = "Excellent Match";
  } else if (clamped >= 60) {
    tierClass = "match-tier-medium";
    tierLabel = "Strong Match";
  } else if (clamped >= 40) {
    tierClass = "match-tier-fair";
    tierLabel = "Moderate Match";
  }

  return (
    <div className={`match-score-badge ${tierClass}`}>
      <div className="match-score-number">
        <Zap size={15} className="match-icon" />
        <span>{clamped.toFixed(1)}%</span>
      </div>
      <span className="match-score-label">{tierLabel}</span>
    </div>
  );
}
