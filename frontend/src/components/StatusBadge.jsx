import React from "react";
import { useLanguage } from "../context/LanguageContext";

export default function StatusBadge({ status }) {
  const { t } = useLanguage();
  const norm = (status || "submitted").toLowerCase().replace(/\s+/g, "_");

  const statusMap = {
    submitted: { label: t("statusSubmitted"), className: "status-submitted" },
    under_review: { label: t("statusUnderReview"), className: "status-review" },
    verified: { label: t("statusVerified"), className: "status-verified" },
    assigned: { label: t("statusAssigned"), className: "status-assigned" },
    in_progress: { label: t("statusInProgress"), className: "status-inprogress" },
    resolved: { label: t("statusResolved"), className: "status-resolved" },
    rejected: { label: t("statusRejected"), className: "status-rejected" },
  };

  const item = statusMap[norm] || { label: status, className: "status-default" };

  return <span className={`status-badge ${item.className}`}>{item.label}</span>;
}
