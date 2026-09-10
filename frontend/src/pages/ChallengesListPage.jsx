import React, { useState, useEffect } from "react";
import { useLocation } from "../router";
import { useLanguage } from "../context/LanguageContext";
import { api } from "../services/api";
import ChallengeCard from "../components/ChallengeCard";
import { JHARKHAND_DISTRICTS } from "../components/LocationPicker";
import { useTranslatedChallenges } from "../hooks/useTranslatedContent";
import {
  FolderKanban,
  Search,
  PlusCircle,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Sparkles,
} from "lucide-react";

export default function ChallengesListPage() {
  const { navigate } = useLocation();
  const { t } = useLanguage();

  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Filters
  const [selectedDistrict, setSelectedDistrict] = useState(() => {
    const hash = window.location.hash;
    const match = hash.match(/district=([^&]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  });
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const categories = [
    "Water Supply",
    "Agriculture",
    "Healthcare",
    "Infrastructure",
    "Sanitation",
    "Education",
    "Environment",
    "Renewable Energy",
    "Other",
  ];

  const statuses = [
    { value: "submitted", label: t("statusSubmitted") },
    { value: "under_review", label: t("statusUnderReview") },
    { value: "verified", label: t("statusVerified") },
    { value: "assigned", label: t("statusAssigned") },
    { value: "in_progress", label: t("statusInProgress") },
    { value: "resolved", label: t("statusResolved") },
  ];

  const fetchChallenges = async (p = 1) => {
    setLoading(true);
    try {
      const res = await api.challenges.list({
        page: p,
        pageSize: 9,
        district: selectedDistrict,
        category: selectedCategory,
        status: selectedStatus,
      });

      if (res) {
        setChallenges(res.items || []);
        setTotal(res.total || 0);
        setPage(res.page || 1);
        setTotalPages(res.total_pages || 1);
      }
    } catch (err) {
      console.warn("Failed to fetch challenges:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChallenges(page);
  }, [page, selectedDistrict, selectedCategory, selectedStatus]);

  const resetFilters = () => {
    setSelectedDistrict("");
    setSelectedCategory("");
    setSelectedStatus("");
    setSearchQuery("");
    setPage(1);
  };

  // Client-side text filter for search query
  const filteredChallenges = searchQuery.trim()
    ? challenges.filter((c) =>
        c.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.location?.district?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : challenges;

  const { translatedChallenges, isTranslating } = useTranslatedChallenges(filteredChallenges);

  return (
    <div className="challenges-page-root">
      <div className="container">
        {/* Header Row */}
        <div className="page-header-row">
          <div>
            <span className="section-kicker">Public Challenge Registry</span>
            <h1 className="page-title">{t("navChallenges")}</h1>
            <p className="page-subtitle">
              Browse problems reported by citizens across Jharkhand and their AI matching status.
            </p>
          </div>

          <button
            type="button"
            onClick={() => navigate("/report")}
            className="btn-primary"
          >
            <PlusCircle size={16} />
            <span>{t("btnReportProblem")}</span>
          </button>
        </div>

        {/* Search and Filters Card */}
        <div className="filter-panel-card">
          <div className="search-bar-row">
            <div className="search-input-wrapper">
              <Search size={18} className="search-icon" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by keywords, location, or issue..."
                className="search-input"
              />
            </div>

            {(selectedDistrict || selectedCategory || selectedStatus || searchQuery) && (
              <button
                type="button"
                onClick={resetFilters}
                className="btn-reset-filters"
                title="Reset all filters"
              >
                <RotateCcw size={14} />
                <span>Reset</span>
              </button>
            )}
          </div>

          <div className="filter-selects-grid">
            {/* District Filter */}
            <div className="filter-select-group">
              <label htmlFor="filter-district" className="filter-label">{t("fieldDistrict")}</label>
              <select
                id="filter-district"
                value={selectedDistrict}
                onChange={(e) => {
                  setSelectedDistrict(e.target.value);
                  setPage(1);
                }}
                className="filter-select"
              >
                <option value="">All Districts ({JHARKHAND_DISTRICTS.length})</option>
                {JHARKHAND_DISTRICTS.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </div>

            {/* Category Filter */}
            <div className="filter-select-group">
              <label htmlFor="filter-category" className="filter-label">{t("fieldCategory")}</label>
              <select
                id="filter-category"
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setPage(1);
                }}
                className="filter-select"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div className="filter-select-group">
              <label htmlFor="filter-status" className="filter-label">Status</label>
              <select
                id="filter-status"
                value={selectedStatus}
                onChange={(e) => {
                  setSelectedStatus(e.target.value);
                  setPage(1);
                }}
                className="filter-select"
              >
                <option value="">All Statuses</option>
                {statuses.map((st) => (
                  <option key={st.value} value={st.value}>
                    {st.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Results Counter */}
        <div className="results-count-bar">
          <span>Showing <strong>{filteredChallenges.length}</strong> of {total} community challenges</span>
          {isTranslating && (
            <span className="translating-tag">
              <Sparkles size={12} className="animate-spin text-green" />
              <span>Translating content...</span>
            </span>
          )}
        </div>

        {/* Challenges Grid */}
        {loading ? (
          <div className="loading-state-box">
            <div className="spinner"></div>
            <span>{t("loading")}</span>
          </div>
        ) : translatedChallenges.length > 0 ? (
          <div className="challenges-grid">
            {translatedChallenges.map((challenge) => (
              <ChallengeCard key={challenge.id} challenge={challenge} />
            ))}
          </div>
        ) : (
          <div className="empty-state-box">
            <FolderKanban size={40} className="text-muted" />
            <p>No challenges match your selected filters.</p>
            <button
              type="button"
              onClick={resetFilters}
              className="btn-secondary mt-2"
            >
              Clear Filters
            </button>
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="pagination-bar">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="pagination-btn"
            >
              <ChevronLeft size={16} />
              <span>Previous</span>
            </button>

            <span className="pagination-page-indicator">
              Page <strong>{page}</strong> of {totalPages}
            </span>

            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="pagination-btn"
            >
              <span>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
