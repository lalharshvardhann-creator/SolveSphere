import React from "react";
import { Check, Clock } from "lucide-react";

export default function Timeline({ currentStatus = "submitted", hasAI = false, hasMatch = false }) {
  const steps = [
    { key: "submitted", label: "Submitted" },
    { key: "analyzed", label: "AI Analyzed" },
    { key: "matched", label: "Institution Matched" },
    { key: "assigned", label: "Accepted" },
    { key: "in_progress", label: "In Progress" },
    { key: "resolved", label: "Resolved" },
  ];

  // Determine active step index
  let activeIndex = 0;
  if (currentStatus === "resolved") {
    activeIndex = 5;
  } else if (currentStatus === "in_progress") {
    activeIndex = 4;
  } else if (currentStatus === "assigned") {
    activeIndex = 3;
  } else if (hasMatch) {
    activeIndex = 2;
  } else if (hasAI) {
    activeIndex = 1;
  }

  return (
    <div className="civic-timeline-wrap">
      <div className="timeline-track">
        {steps.map((step, idx) => {
          const isDone = idx < activeIndex;
          const isCurrent = idx === activeIndex;

          return (
            <div
              key={step.key}
              className={`timeline-node ${isDone ? "node-done" : ""} ${
                isCurrent ? "node-current" : ""
              }`}
            >
              <div className="node-circle">
                {isDone ? (
                  <Check size={14} className="text-white" />
                ) : isCurrent ? (
                  <Clock size={14} className="text-green" />
                ) : (
                  <span className="node-index">{idx + 1}</span>
                )}
              </div>
              <span className="node-label">{step.label}</span>
              {idx < steps.length - 1 && <div className="node-line"></div>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
