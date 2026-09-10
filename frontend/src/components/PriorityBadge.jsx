import React from "react";
import { AlertTriangle, AlertCircle, ArrowUpCircle } from "lucide-react";

export default function PriorityBadge({ score, showScore = true }) {
  if (score === null || score === undefined) {
    return <span className="priority-badge priority-none">Pending Priority</span>;
  }

  const num = parseFloat(score);
  let level = "low";
  let label = "Low Priority";
  let icon = null;

  if (num >= 8.0) {
    level = "critical";
    label = "Critical Priority";
    icon = <AlertTriangle size={13} />;
  } else if (num >= 6.0) {
    level = "high";
    label = "High Priority";
    icon = <AlertCircle size={13} />;
  } else if (num >= 4.0) {
    level = "medium";
    label = "Medium Priority";
    icon = <ArrowUpCircle size={13} />;
  }

  return (
    <span className={`priority-badge priority-${level}`}>
      {icon}
      <span>{label}</span>
      {showScore && <strong className="priority-num">{num.toFixed(1)}/10</strong>}
    </span>
  );
}
