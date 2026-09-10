import React, { useState, useEffect } from "react";
import { useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { api } from "../services/api";
import VoiceRecorder from "../components/VoiceRecorder";
import ImageUpload from "../components/ImageUpload";
import LocationPicker from "../components/LocationPicker";
import {
  Type,
  Mic,
  Camera,
  Send,
  Sparkles,
  CheckCircle2,
  Users,
  Layers,
  AlertCircle,
} from "lucide-react";

export default function ReportProblemPage() {
  const { navigate, currentPath } = useLocation();
  const { t } = useLanguage();
  const { user, isAuthenticated } = useAuth();
  const { addToast } = useToast();

  const [activeInputTab, setActiveInputTab] = useState("type"); // 'type', 'voice', 'photo'
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  // Check URL query parameters (e.g. ?mode=voice)
  useEffect(() => {
    if (window.location.hash.includes("mode=voice")) {
      setActiveInputTab("voice");
    }
  }, []);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "Water Supply",
    subcategory: "",
    people_affected: "",
    state: "Jharkhand",
    district: "Ranchi",
    block: "",
    panchayat: "",
    village: "",
    latitude: null,
    longitude: null,
    submitted_by: user?.id || 1,
  });

  const categories = [
    { value: "Water Supply", label: t("catWater") },
    { value: "Agriculture", label: t("catAgriculture") },
    { value: "Healthcare", label: t("catHealthcare") },
    { value: "Infrastructure", label: t("catInfrastructure") },
    { value: "Sanitation", label: t("catSanitation") },
    { value: "Education", label: t("catEducation") },
    { value: "Environment", label: t("catEnvironment") },
    { value: "Renewable Energy", label: t("catEnergy") },
    { value: "Other", label: t("catOther") },
  ];

  const handleVoiceTranscript = (newText) => {
    if (!newText) return;
    setFormData((prev) => {
      const current = prev.description ? prev.description.trim() : "";
      const updated = current ? `${current} ${newText}` : newText;
      return {
        ...prev,
        description: updated,
      };
    });
  };

  const handleLocationChange = (locData) => {
    setFormData((prev) => ({
      ...prev,
      ...locData,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");

    if (!formData.title.trim()) {
      setErrorMsg("Please provide a title for the problem.");
      return;
    }
    if (!formData.description.trim()) {
      setErrorMsg("Please provide a description of the problem.");
      return;
    }
    if (!formData.district) {
      setErrorMsg("Please select a district in Jharkhand.");
      return;
    }

    setLoading(true);

    try {
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        category: formData.category,
        subcategory: formData.subcategory.trim() || null,
        people_affected: formData.people_affected ? parseInt(formData.people_affected, 10) : null,
        state: "Jharkhand",
        district: formData.district,
        block: formData.block.trim() || null,
        panchayat: formData.panchayat.trim() || null,
        village: formData.village.trim() || null,
        latitude: formData.latitude,
        longitude: formData.longitude,
        submitted_by: user?.id || 1, // Submit on behalf of current user or default citizen
      };

      const created = await api.challenges.create(payload);
      addToast(t("successSubmit"), "success");

      // Navigate to challenge detail page
      navigate(`/challenges/${created.id}`);
    } catch (err) {
      console.error("Submission failed:", err);
      setErrorMsg(err.message || "Failed to submit problem. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-page-root">
      <div className="container form-container">
        <div className="form-header-box">
          <span className="section-kicker">Citizen Problem Intake</span>
          <h1 className="form-main-heading">{t("formTitle")}</h1>
          <p className="form-lead-desc">{t("formSubtitle")}</p>
        </div>

        {errorMsg && (
          <div className="form-error-banner">
            <AlertCircle size={18} />
            <span>{errorMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="citizen-report-form">
          {/* Input Method Selector Tabs */}
          <div className="input-method-tabs">
            <button
              type="button"
              className={`input-tab ${activeInputTab === "type" ? "active" : ""}`}
              onClick={() => setActiveInputTab("type")}
            >
              <Type size={16} />
              <span>{t("tabType")}</span>
            </button>

            <button
              type="button"
              className={`input-tab ${activeInputTab === "voice" ? "active" : ""}`}
              onClick={() => setActiveInputTab("voice")}
            >
              <Mic size={16} className="text-green" />
              <span>{t("tabVoice")}</span>
            </button>

            <button
              type="button"
              className={`input-tab ${activeInputTab === "photo" ? "active" : ""}`}
              onClick={() => setActiveInputTab("photo")}
            >
              <Camera size={16} />
              <span>{t("tabPhoto")}</span>
            </button>
          </div>

          {/* Voice input helper card when voice tab is selected */}
          {activeInputTab === "voice" && (
            <div className="tab-embedded-panel">
              <VoiceRecorder onTranscript={handleVoiceTranscript} />
            </div>
          )}

          {/* Photo upload helper card when photo tab is selected */}
          {activeInputTab === "photo" && (
            <div className="tab-embedded-panel">
              <ImageUpload />
            </div>
          )}

          {/* Core Problem Info */}
          <div className="form-section-card">
            {/* Title */}
            <div className="form-field">
              <label htmlFor="challenge-title" className="form-label">{t("fieldTitle")} *</label>
              <input
                id="challenge-title"
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder={t("fieldTitlePlaceholder")}
                required
                className="form-input form-input-lg"
              />
            </div>

            {/* Description */}
            <div className="form-field">
              <div className="label-with-hint">
                <label htmlFor="challenge-description" className="form-label">{t("fieldDescription")} *</label>
                <span className="field-hint">Voice recording appends text directly here</span>
              </div>
              <textarea
                id="challenge-description"
                rows={5}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder={t("fieldDescriptionPlaceholder")}
                required
                className="form-textarea"
              />
            </div>

            {/* Category & People Affected */}
            <div className="grid-2-col">
              <div className="form-field">
                <label htmlFor="challenge-category" className="form-label">{t("fieldCategory")} *</label>
                <select
                  id="challenge-category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="form-select"
                >
                  {categories.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-field">
                <label className="form-label">{t("fieldPeopleAffected")}</label>
                <input
                  type="number"
                  min="0"
                  value={formData.people_affected}
                  onChange={(e) => setFormData({ ...formData, people_affected: e.target.value })}
                  placeholder="e.g. 2500"
                  className="form-input"
                />
              </div>
            </div>

            {/* Optional Subcategory */}
            <div className="form-field">
              <label className="form-label">{t("fieldSubcategory")}</label>
              <input
                type="text"
                value={formData.subcategory}
                onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })}
                placeholder="e.g. Rural Water Purification, Handpump Arsenic, Bridge Damage"
                className="form-input"
              />
            </div>
          </div>

          {/* Location Picker Section */}
          <div className="form-section-card">
            <LocationPicker
              district={formData.district}
              block={formData.block}
              panchayat={formData.panchayat}
              village={formData.village}
              latitude={formData.latitude}
              longitude={formData.longitude}
              onChange={handleLocationChange}
            />
          </div>

          {/* Submission Action */}
          <div className="form-submit-row">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary btn-submit-large"
            >
              <Send size={18} />
              <span>{loading ? t("btnSubmitting") : t("btnSubmitProblem")}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
