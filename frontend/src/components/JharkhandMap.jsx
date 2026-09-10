import React, { useState } from "react";
import { MapPin, ArrowRight, CheckCircle2 } from "lucide-react";
import { useLocation } from "../router";
import { JHARKHAND_DISTRICTS } from "./LocationPicker";

export default function JharkhandMap({ onSelectDistrict = null, selectedDistrict = null }) {
  const { navigate } = useLocation();
  const [hovered, setHovered] = useState(null);

  const districtProfiles = {
    Ranchi: { zone: "South Chotanagpur", count: 18, color: "#15803d" },
    Dhanbad: { zone: "North Chotanagpur", count: 14, color: "#16a34a" },
    "East Singhbhum": { zone: "Kolhan", count: 12, color: "#16a34a" },
    Bokaro: { zone: "North Chotanagpur", count: 9, color: "#22c55e" },
    Deoghar: { zone: "Santhal Pargana", count: 8, color: "#22c55e" },
    Hazaribagh: { zone: "North Chotanagpur", count: 7, color: "#22c55e" },
    Dumka: { zone: "Santhal Pargana", count: 6, color: "#4ade80" },
    Giridih: { zone: "North Chotanagpur", count: 5, color: "#4ade80" },
    Palamu: { zone: "Palamu", count: 5, color: "#4ade80" },
    Ramgarh: { zone: "North Chotanagpur", count: 4, color: "#86efac" },
    "West Singhbhum": { zone: "Kolhan", count: 4, color: "#86efac" },
    Gumla: { zone: "South Chotanagpur", count: 3, color: "#86efac" },
  };

  const handleDistrictClick = (d) => {
    if (onSelectDistrict) {
      onSelectDistrict(d);
    } else {
      navigate(`/challenges?district=${encodeURIComponent(d)}`);
    }
  };

  return (
    <div className="jharkhand-map-card">
      <div className="jharkhand-map-header">
        <div>
          <h3 className="jharkhand-map-title">
            <MapPin size={18} className="text-green" />
            <span>Jharkhand District Problem Heatmap</span>
          </h3>
          <p className="jharkhand-map-subtitle">
            Click any district to view active citizen reports and matched HEIs
          </p>
        </div>
      </div>

      <div className="district-chips-grid">
        {JHARKHAND_DISTRICTS.map((district) => {
          const profile = districtProfiles[district] || { count: 2, zone: "Jharkhand" };
          const isSelected = selectedDistrict === district;
          const isHovered = hovered === district;

          return (
            <button
              key={district}
              type="button"
              onClick={() => handleDistrictClick(district)}
              onMouseEnter={() => setHovered(district)}
              onMouseLeave={() => setHovered(null)}
              className={`district-chip-btn ${isSelected ? "district-chip-selected" : ""}`}
            >
              <span className="district-name">{district}</span>
              <span className="district-badge">{profile.count} issues</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
