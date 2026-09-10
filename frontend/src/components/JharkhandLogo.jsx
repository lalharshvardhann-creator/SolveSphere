import React from "react";

export default function JharkhandLogo({ size = 36, showText = true, className = "" }) {
  return (
    <div className={`solvesphere-logo-wrap ${className}`} style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none" }}>
      {/* Clean Civic Emblem SVG */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ flexShrink: 0 }}
      >
        {/* Outer Circular Ring (Emerald Green) */}
        <circle cx="32" cy="32" r="30" fill="#15803d" />
        <circle cx="32" cy="32" r="27" fill="#ffffff" />
        <circle cx="32" cy="32" r="24" fill="#f0fdf4" stroke="#16a34a" strokeWidth="1.5" />

        {/* Stylized Civic Petals / AI Nodes */}
        <path
          d="M32 14C32 20 28 24 22 24C28 24 32 28 32 34C32 28 36 24 42 24C36 24 32 20 32 14Z"
          fill="#15803d"
        />
        
        {/* Central Hub */}
        <circle cx="32" cy="32" r="8" fill="#ffffff" stroke="#15803d" strokeWidth="2" />
        <circle cx="32" cy="32" r="3.5" fill="#16a34a" />

        {/* Radiating Solution Nodes */}
        <circle cx="32" cy="19" r="2" fill="#15803d" />
        <circle cx="45" cy="32" r="2" fill="#15803d" />
        <circle cx="32" cy="45" r="2" fill="#15803d" />
        <circle cx="19" cy="32" r="2" fill="#15803d" />

        <line x1="32" y1="24" x2="32" y2="28.5" stroke="#15803d" strokeWidth="1.5" />
        <line x1="32" y1="35.5" x2="32" y2="40" stroke="#15803d" strokeWidth="1.5" />
        <line x1="24" y1="32" x2="28.5" y2="32" stroke="#15803d" strokeWidth="1.5" />
        <line x1="35.5" y1="32" x2="40" y2="32" stroke="#15803d" strokeWidth="1.5" />
      </svg>

      {showText && (
        <span style={{ fontSize: "1.25rem", fontWeight: "800", color: "#0f172a", letterSpacing: "-0.02em" }}>
          Solve<span style={{ color: "#15803d" }}>Sphere</span>
        </span>
      )}
    </div>
  );
}
