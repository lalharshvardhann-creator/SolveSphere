import React, { useState } from "react";
import { MapPin, Navigation, CheckCircle2, AlertCircle } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

export const JHARKHAND_DISTRICTS = [
  "Bokaro",
  "Chatra",
  "Deoghar",
  "Dhanbad",
  "Dumka",
  "East Singhbhum",
  "Garhwa",
  "Giridih",
  "Godda",
  "Gumla",
  "Hazaribagh",
  "Jamtara",
  "Khunti",
  "Koderma",
  "Latehar",
  "Lohardaga",
  "Pakur",
  "Palamu",
  "Ramgarh",
  "Ranchi",
  "Sahibganj",
  "Saraikela Kharsawan",
  "Simdega",
  "West Singhbhum",
];

export default function LocationPicker({
  district,
  block,
  panchayat,
  village,
  latitude,
  longitude,
  onChange,
}) {
  const { t } = useLanguage();
  const [geoStatus, setGeoStatus] = useState(null); // 'loading', 'success', 'error'
  const [geoMsg, setGeoMsg] = useState("");

  const handleUseLocation = () => {
    if (!navigator.geolocation) {
      setGeoStatus("error");
      setGeoMsg("Geolocation is not supported by your browser.");
      return;
    }

    setGeoStatus("loading");
    setGeoMsg("Acquiring GPS coordinates in Jharkhand...");

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = parseFloat(pos.coords.latitude.toFixed(6));
        const lon = parseFloat(pos.coords.longitude.toFixed(6));

        onChange({
          latitude: lat,
          longitude: lon,
          state: "Jharkhand",
        });

        setGeoStatus("success");
        setGeoMsg(`GPS Acquired: ${lat}, ${lon}`);
      },
      (err) => {
        setGeoStatus("error");
        setGeoMsg(`Could not get GPS: ${err.message}. You can manually select district.`);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  return (
    <div className="location-picker-group">
      <div className="location-header-row">
        <label className="form-section-title">
          <MapPin size={18} className="text-green" />
          <span>Location in Jharkhand</span>
        </label>
        <button
          type="button"
          onClick={handleUseLocation}
          className="btn-use-location"
          disabled={geoStatus === "loading"}
        >
          <Navigation size={14} className={geoStatus === "loading" ? "animate-spin" : ""} />
          <span>{geoStatus === "loading" ? "Locating..." : t("btnUseLocation")}</span>
        </button>
      </div>

      {geoStatus && (
        <div className={`geo-notice geo-${geoStatus}`}>
          {geoStatus === "success" && <CheckCircle2 size={14} />}
          {geoStatus === "error" && <AlertCircle size={14} />}
          <span>{geoMsg}</span>
        </div>
      )}

      <div className="grid-2-col">
        {/* State (Fixed Jharkhand) */}
        <div className="form-field">
          <label className="form-label">{t("fieldState")} *</label>
          <input
            type="text"
            value="Jharkhand"
            disabled
            className="form-input form-input-disabled"
          />
        </div>

        {/* District */}
        <div className="form-field">
          <label htmlFor="district-select" className="form-label">{t("fieldDistrict")} *</label>
          <select
            id="district-select"
            value={district || ""}
            onChange={(e) => onChange({ district: e.target.value })}
            required
            className="form-select"
          >
            <option value="">-- Select Jharkhand District --</option>
            {JHARKHAND_DISTRICTS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid-3-col">
        {/* Block */}
        <div className="form-field">
          <label className="form-label">{t("fieldBlock")}</label>
          <input
            type="text"
            value={block || ""}
            onChange={(e) => onChange({ block: e.target.value })}
            placeholder="e.g. Kanke / Namkum"
            className="form-input"
          />
        </div>

        {/* Panchayat */}
        <div className="form-field">
          <label className="form-label">{t("fieldPanchayat")}</label>
          <input
            type="text"
            value={panchayat || ""}
            onChange={(e) => onChange({ panchayat: e.target.value })}
            placeholder="e.g. Pithoria"
            className="form-input"
          />
        </div>

        {/* Village */}
        <div className="form-field">
          <label className="form-label">{t("fieldVillage")}</label>
          <input
            type="text"
            value={village || ""}
            onChange={(e) => onChange({ village: e.target.value })}
            placeholder="e.g. Boriya Village"
            className="form-input"
          />
        </div>
      </div>

      {/* GPS Coordinates Readout */}
      {(latitude || longitude) && (
        <div className="coords-row">
          <span className="coord-chip">
            <strong>Lat:</strong> {latitude}
          </span>
          <span className="coord-chip">
            <strong>Lon:</strong> {longitude}
          </span>
        </div>
      )}
    </div>
  );
}
