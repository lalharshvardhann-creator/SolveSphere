import React, { useState, useEffect } from "react";
import { useLanguage } from "../context/LanguageContext";
import { api } from "../services/api";
import InstitutionCard from "../components/InstitutionCard";
import { JHARKHAND_DISTRICTS } from "../components/LocationPicker";
import {
  useTranslatedInstitutions,
  useTranslatedInstitutionDetail,
} from "../hooks/useTranslatedContent";
import {
  Building2,
  Search,
  CheckCircle,
  ExternalLink,
  MapPin,
  Sparkles,
  FlaskConical,
  Award,
} from "lucide-react";

function InstitutionDetailModal({ inst, onClose }) {
  const { translatedInst: translated, isTranslating } = useTranslatedInstitutionDetail(inst);
  const activeInst = translated || inst;

  return (
    <div className="modal-backdrop">
      <div className="modal-content-box modal-lg">
        <div className="modal-header">
          <div className="inst-modal-title-group">
            <Building2 size={24} className="text-green" />
            <div>
              <h3>{activeInst.name}</h3>
              <span className="inst-type-pill">
                {activeInst.institution_type} • {activeInst.district}
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="modal-close-btn"
          >
            &times;
          </button>
        </div>

        <div className="modal-body">
          {activeInst.description && (
            <div className="modal-section">
              <h4 className="modal-section-title">About Institution</h4>
              <p>{activeInst.description}</p>
            </div>
          )}

          {/* Registered Expertise Domains */}
          <div className="modal-section">
            <h4 className="modal-section-title">
              <Sparkles size={16} className="text-green" />
              <span>Research Expertise & Domains</span>
            </h4>

            {activeInst.expertise_entries?.length > 0 ? (
              <div className="modal-expertise-list">
                {activeInst.expertise_entries.map((exp) => (
                  <div key={exp.id} className="modal-expertise-card">
                    <div className="exp-card-header">
                      <strong className="text-green">{exp.domain}</strong>
                      {exp.subdomain && <span className="exp-subdomain">({exp.subdomain})</span>}
                      {exp.expertise_level && (
                        <span className="exp-level-badge">{exp.expertise_level}</span>
                      )}
                    </div>

                    {exp.keywords && (
                      <div className="exp-field-row">
                        <span className="field-key">Keywords:</span>
                        <span className="field-val">{exp.keywords}</span>
                      </div>
                    )}

                    {exp.research_areas && (
                      <div className="exp-field-row">
                        <span className="field-key">Research Areas:</span>
                        <span className="field-val">{exp.research_areas}</span>
                      </div>
                    )}

                    {exp.facilities && (
                      <div className="exp-field-row">
                        <span className="field-key">Labs & Facilities:</span>
                        <span className="field-val">{exp.facilities}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted">General Higher Education & Research capabilities.</p>
            )}
          </div>
        </div>

        <div className="modal-footer">
          {activeInst.website && (
            <a
              href={activeInst.website}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary"
            >
              <span>Visit Website</span>
              <ExternalLink size={14} />
            </a>
          )}
          <button
            type="button"
            onClick={onClose}
            className="btn-primary"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default function InstitutionsPage() {
  const { t } = useLanguage();
  const [institutions, setInstitutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDistrict, setSelectedDistrict] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedInstDetail, setSelectedInstDetail] = useState(null);

  const instTypes = [
    "Research",
    "University",
    "Engineering",
    "Technical Institute",
    "Polytechnic",
  ];

  const fetchInstitutions = async () => {
    setLoading(true);
    try {
      const res = await api.institutions.list({
        district: selectedDistrict,
        institutionType: selectedType,
        page: 1,
        pageSize: 30,
      });
      if (res?.items) {
        setInstitutions(res.items);
      }
    } catch (err) {
      console.warn("Could not fetch institutions:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInstitutions();
  }, [selectedDistrict, selectedType]);

  const viewFullInstitution = async (inst) => {
    try {
      const detail = await api.institutions.getById(inst.id);
      setSelectedInstDetail(detail || inst);
    } catch {
      setSelectedInstDetail(inst);
    }
  };

  const { translatedInstitutions } = useTranslatedInstitutions(institutions);

  const filteredInstitutions = searchQuery.trim()
    ? translatedInstitutions.filter(
        (inst) =>
          inst.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          inst.district?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          inst.institution_type?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          inst.description?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : translatedInstitutions;

  return (
    <div className="institutions-page-root">
      <div className="container">
        {/* Page Header */}
        <div className="page-header-row">
          <div>
            <span className="section-kicker">Higher Education & Research Ecosystem</span>
            <h1 className="page-title">{t("navInstitutions")}</h1>
            <p className="page-subtitle">
              Universities, research centers, and engineering colleges across Jharkhand partnering for civic problem solving.
            </p>
          </div>
        </div>

        {/* Filter Panel */}
        <div className="filter-panel-card">
          <div className="search-bar-row">
            <div className="search-input-wrapper">
              <Search size={18} className="search-icon" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by institution name, research domain, or district..."
                className="search-input"
              />
            </div>
          </div>

          <div className="filter-selects-grid">
            <div className="filter-select-group">
              <label className="filter-label">{t("fieldDistrict")}</label>
              <select
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                className="filter-select"
              >
                <option value="">All Districts</option>
                {JHARKHAND_DISTRICTS.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-select-group">
              <label className="filter-label">Institution Type</label>
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="filter-select"
              >
                <option value="">All Types</option>
                {instTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <div className="loading-state-box">
            <div className="spinner"></div>
            <span>{t("loading")}</span>
          </div>
        ) : filteredInstitutions.length > 0 ? (
          <div className="institutions-grid">
            {filteredInstitutions.map((inst) => (
              <div key={inst.id} onClick={() => viewFullInstitution(inst)} className="inst-grid-item">
                <InstitutionCard institution={inst} />
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state-box">
            <Building2 size={40} className="text-muted" />
            <p>No institutions match the current search filters.</p>
          </div>
        )}
      </div>

      {/* Institution Detail Modal */}
      {selectedInstDetail && (
        <InstitutionDetailModal
          inst={selectedInstDetail}
          onClose={() => setSelectedInstDetail(null)}
        />
      )}
    </div>
  );
}
