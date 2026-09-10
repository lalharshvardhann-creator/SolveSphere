import React, { useState, useRef } from "react";
import { Camera, Upload, X, Image as ImageIcon } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

export default function ImageUpload({ onImageSelect, previewUrl: initialPreview = null }) {
  const { t } = useLanguage();
  const [preview, setPreview] = useState(initialPreview);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.type.startsWith("image/")) {
        alert("Please select a valid image file.");
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
        if (onImageSelect) onImageSelect(reader.result, file);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemove = () => {
    setPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (onImageSelect) onImageSelect(null, null);
  };

  return (
    <div className="image-upload-card">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/*"
        className="sr-only"
        id="problem-photo-input"
      />

      {!preview ? (
        <label htmlFor="problem-photo-input" className="image-drop-area">
          <div className="upload-icon-circle">
            <Camera size={24} className="text-green" />
          </div>
          <div className="upload-text-group">
            <span className="upload-main-text">{t("photoTitle")}</span>
            <span className="upload-sub-text">{t("photoSubtitle")}</span>
          </div>
          <div className="upload-badge">
            <Upload size={14} />
            <span>Browse or Take Photo</span>
          </div>
        </label>
      ) : (
        <div className="image-preview-wrapper">
          <img src={preview} alt="Problem evidence preview" className="evidence-preview-img" />
          <div className="preview-overlay">
            <button
              type="button"
              onClick={handleRemove}
              className="remove-photo-btn"
              title={t("photoRemove")}
            >
              <X size={16} />
              <span>{t("photoRemove")}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
