from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session, joinedload

from app.models.challenge import Challenge, ChallengeAssignment
from app.models.institution import Institution, InstitutionExpertise


STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its",
    "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "should", "shouldn't", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "were", "weren't", "what", "when", "where", "which", "while",
    "who", "whom", "why", "with", "won't", "would", "wouldn't", "you", "your",
    "yours", "yourself", "yourselves", "etc", "eg", "ie", "also", "using", "based",
}

EXPERTISE_LEVEL_SCORES = {
    "leading": 8.0,
    "expert": 8.0,
    "advanced": 6.0,
    "intermediate": 4.0,
    "beginner": 2.0,
}


def _normalize_text(text: Optional[str]) -> str:
    """Normalize text by lowering case and stripping excess whitespace."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.lower().strip())


def _clean_tokens(text: Optional[str]) -> Set[str]:
    """Extract meaningful token set filtering out common stop words."""
    if not text:
        return set()
    raw_tokens = re.findall(r"\b[a-z0-9_-]{2,}\b", text.lower())
    return {t for t in raw_tokens if t not in STOP_WORDS}


def _extract_phrases(text: Optional[str]) -> List[str]:
    """Split text into distinct keyword / expertise phrases."""
    if not text:
        return []
    parts = re.split(r"[;,\n•\r\t]+", text)
    cleaned = []
    for p in parts:
        c = p.strip()
        if c:
            cleaned.append(c)
    return cleaned


class MatchingService:
    @staticmethod
    def _calculate_domain_score(
        challenge_cat: str,
        expertise_domain: Optional[str],
    ) -> float:
        """Calculate score (0 - 25) for domain / category match."""
        if not challenge_cat or not expertise_domain:
            return 0.0

        cat_norm = _normalize_text(challenge_cat)
        dom_norm = _normalize_text(expertise_domain)

        if cat_norm == dom_norm:
            return 25.0

        if cat_norm in dom_norm or dom_norm in cat_norm:
            return 22.0

        cat_tokens = _clean_tokens(challenge_cat)
        dom_tokens = _clean_tokens(expertise_domain)
        overlap = cat_tokens & dom_tokens

        if overlap:
            ratio = len(overlap) / max(len(cat_tokens), 1)
            return min(20.0, 12.0 + 8.0 * ratio)

        return 0.0

    @staticmethod
    def _calculate_subdomain_score(
        challenge_subcat: Optional[str],
        expertise_subdomain: Optional[str],
    ) -> float:
        """Calculate score (0 - 15) for subdomain match."""
        if not challenge_subcat or not expertise_subdomain:
            return 0.0

        subcat_norm = _normalize_text(challenge_subcat)
        subdom_norm = _normalize_text(expertise_subdomain)

        if subcat_norm == subdom_norm:
            return 15.0

        if subdom_norm in subcat_norm or subcat_norm in subdom_norm:
            return 14.0

        subcat_tokens = _clean_tokens(challenge_subcat)
        subdom_tokens = _clean_tokens(expertise_subdomain)
        overlap = subcat_tokens & subdom_tokens

        if overlap:
            ratio = len(overlap) / max(len(subcat_tokens), 1)
            return min(15.0, 8.0 + 7.0 * ratio)

        return 0.0

    @staticmethod
    def _calculate_expertise_overlap(
        challenge_phrases: List[str],
        challenge_tokens: Set[str],
        expertise_entry: Optional[InstitutionExpertise],
        institution: Institution,
    ) -> Tuple[float, List[str]]:
        """
        Calculate overlap score (0 - 40) between required challenge expertise
        and institution keywords, facilities, research areas, and descriptions.
        """
        inst_text_parts = [
            institution.name or "",
            institution.institution_type or "",
            institution.description or "",
        ]
        inst_phrases: List[str] = []

        if expertise_entry:
            if expertise_entry.keywords:
                inst_text_parts.append(expertise_entry.keywords)
                inst_phrases.extend(_extract_phrases(expertise_entry.keywords))
            if expertise_entry.research_areas:
                inst_text_parts.append(expertise_entry.research_areas)
                inst_phrases.extend(_extract_phrases(expertise_entry.research_areas))
            if expertise_entry.facilities:
                inst_text_parts.append(expertise_entry.facilities)
                inst_phrases.extend(_extract_phrases(expertise_entry.facilities))
            if expertise_entry.subdomain:
                inst_phrases.append(expertise_entry.subdomain)

        combined_inst_text = " ".join(inst_text_parts)
        inst_tokens = _clean_tokens(combined_inst_text)

        matched_terms: List[str] = []
        matched_phrases_set: Set[str] = set()

        # Check phrase matches
        for phrase in inst_phrases:
            phrase_norm = phrase.strip().lower()
            phrase_clean_tokens = _clean_tokens(phrase)
            if not phrase_clean_tokens:
                continue

            # Check if phrase tokens appear in challenge tokens or text
            if phrase_clean_tokens.issubset(challenge_tokens) or any(
                phrase_norm in ch_p.lower() or ch_p.lower() in phrase_norm
                for ch_p in challenge_phrases
            ):
                if phrase_norm not in matched_phrases_set:
                    matched_phrases_set.add(phrase_norm)
                    matched_terms.append(phrase)

        # Check challenge phrases match into institution
        for ch_phrase in challenge_phrases:
            ch_phrase_norm = ch_phrase.strip().lower()
            ch_tokens = _clean_tokens(ch_phrase)
            if not ch_tokens:
                continue

            if ch_tokens.issubset(inst_tokens) or ch_phrase_norm in combined_inst_text.lower():
                if ch_phrase_norm not in matched_phrases_set:
                    matched_phrases_set.add(ch_phrase_norm)
                    matched_terms.append(ch_phrase)

        # Token overlap ratio
        common_tokens = challenge_tokens & inst_tokens
        token_coverage = (
            len(common_tokens) / max(len(challenge_tokens), 1)
            if challenge_tokens
            else 0.0
        )

        phrase_coverage = (
            len(matched_terms) / max(len(challenge_phrases), 1)
            if challenge_phrases
            else 0.0
        )

        if challenge_phrases:
            weighted_metric = (0.65 * phrase_coverage) + (0.35 * token_coverage)
        else:
            weighted_metric = token_coverage

        overlap_score = min(40.0, weighted_metric * 50.0)

        # Deduplicate while preserving order
        seen = set()
        deduped_terms = []
        for t in matched_terms:
            tl = t.lower().strip()
            if tl not in seen:
                seen.add(tl)
                deduped_terms.append(t.strip())

        return overlap_score, deduped_terms

    @classmethod
    def _evaluate_institution(
        cls,
        challenge: Challenge,
        institution: Institution,
    ) -> Tuple[float, str]:
        """
        Evaluate a single institution against a challenge and return (match_score, match_reason).
        Evaluates across all expertise entries and picks the best specialization.
        """
        ai = challenge.ai_analysis
        category = (ai.category if ai and ai.category else challenge.category) or ""
        subcategory = (ai.subcategory if ai and ai.subcategory else challenge.subcategory) or ""

        challenge_phrases: List[str] = []
        if ai:
            if ai.required_expertise:
                challenge_phrases.extend(_extract_phrases(ai.required_expertise))
            if ai.keywords:
                challenge_phrases.extend(_extract_phrases(ai.keywords))

        combined_ch_text = f"{challenge.title} {challenge.description} "
        if ai:
            combined_ch_text += f"{ai.category or ''} {ai.subcategory or ''} {ai.keywords or ''} {ai.required_expertise or ''} {ai.problem_summary or ''}"
        challenge_tokens = _clean_tokens(combined_ch_text)

        # Proximity score (0 or 12)
        ch_district = (
            challenge.location.district.strip().lower()
            if challenge.location and challenge.location.district
            else None
        )
        inst_district = institution.district.strip().lower() if institution.district else None
        district_matched = bool(ch_district and inst_district and ch_district == inst_district)
        district_score = 12.0 if district_matched else 0.0

        best_score = -1.0
        best_exp: Optional[InstitutionExpertise] = None
        best_highlights: List[str] = []
        best_domain_score = 0.0
        best_subdomain_score = 0.0
        best_keyword_score = 0.0
        best_level_score = 0.0

        expertise_list = institution.expertise_entries or []

        if expertise_list:
            for exp in expertise_list:
                d_score = cls._calculate_domain_score(category, exp.domain)
                s_score = cls._calculate_subdomain_score(subcategory, exp.subdomain)
                k_score, highlights = cls._calculate_expertise_overlap(
                    challenge_phrases=challenge_phrases,
                    challenge_tokens=challenge_tokens,
                    expertise_entry=exp,
                    institution=institution,
                )

                level_str = (exp.expertise_level or "").strip().lower()
                l_score = EXPERTISE_LEVEL_SCORES.get(level_str, 1.0)

                total = d_score + s_score + k_score + district_score + l_score

                if total > best_score:
                    best_score = total
                    best_exp = exp
                    best_highlights = highlights
                    best_domain_score = d_score
                    best_subdomain_score = s_score
                    best_keyword_score = k_score
                    best_level_score = l_score
        else:
            # Institution has no explicit expertise entries; evaluate general profile
            k_score, highlights = cls._calculate_expertise_overlap(
                challenge_phrases=challenge_phrases,
                challenge_tokens=challenge_tokens,
                expertise_entry=None,
                institution=institution,
            )
            d_score = cls._calculate_domain_score(category, institution.institution_type)
            l_score = 1.0
            best_score = d_score + k_score + district_score + l_score
            best_highlights = highlights
            best_domain_score = d_score
            best_keyword_score = k_score
            best_level_score = l_score

        # Bound score between 0.0 and 100.0
        final_score = round(min(100.0, max(0.0, best_score)), 1)

        # Generate human-readable explainable match reason
        match_reason = cls._generate_match_reason(
            score=final_score,
            institution=institution,
            best_exp=best_exp,
            highlights=best_highlights,
            district_matched=district_matched,
        )

        return final_score, match_reason

    @staticmethod
    def _generate_match_reason(
        score: float,
        institution: Institution,
        best_exp: Optional[InstitutionExpertise],
        highlights: List[str],
        district_matched: bool,
    ) -> str:
        """Construct a deterministic, human-readable match reason."""
        district_text = f"located in {institution.district}" if institution.district else ""

        if score >= 70.0:
            exp_text = ""
            if best_exp:
                if best_exp.domain and best_exp.subdomain:
                    exp_text = f"the institution specializes in {best_exp.domain} and {best_exp.subdomain}"
                elif best_exp.domain:
                    exp_text = f"the institution specializes in {best_exp.domain}"
            if not exp_text:
                exp_text = f"the institution has strong alignment as a {institution.institution_type} organization"

            reason = f"Strong match because {exp_text}"
            if highlights:
                reason += f", with overlapping expertise in {', '.join(highlights[:5])}"
            if district_matched and institution.district:
                reason += f". It is also located in {institution.district}."
            elif institution.district:
                reason += f". Located in {institution.district}."
            else:
                reason += "."
            return reason

        if score >= 40.0:
            exp_text = ""
            if best_exp and best_exp.domain:
                exp_text = best_exp.domain
                if best_exp.subdomain:
                    exp_text += f" ({best_exp.subdomain})"
            else:
                exp_text = institution.institution_type

            reason = f"Moderate match: The institution possesses relevant expertise in {exp_text}"
            if highlights:
                reason += f", with alignment in {', '.join(highlights[:3])}"
            if district_matched and institution.district:
                reason += f". Located in {institution.district} (local district match)."
            elif institution.district:
                reason += f". Located in {institution.district}."
            else:
                reason += "."
            return reason

        # Low or minimal match
        if highlights:
            reason = f"Limited match: Partial alignment in {', '.join(highlights[:2])}"
            if institution.district:
                reason += f". Located in {institution.district}."
            else:
                reason += "."
            return reason

        if district_matched and institution.district:
            return f"Low match: Limited domain or technical overlap with challenge requirements. Located in {institution.district}."

        if institution.district:
            return f"Low match: Limited domain or technical overlap with challenge requirements. Located in {institution.district}."

        return "Minimal match: No significant domain or expertise overlap identified for this challenge."

    @classmethod
    def match_challenge(
        cls,
        db: Session,
        challenge_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Run explainable matching for a challenge against all registered institutions,
        persist proposed assignments into database, and return ranked matches.
        """
        challenge = (
            db.query(Challenge)
            .options(
                joinedload(Challenge.location),
                joinedload(Challenge.ai_analysis),
            )
            .filter(Challenge.id == challenge_id)
            .first()
        )

        if not challenge:
            raise ValueError(f"Challenge with ID {challenge_id} not found.")

        if not challenge.ai_analysis:
            raise ValueError("Challenge must be analyzed by Gemini before institution matching.")

        institutions = (
            db.query(Institution)
            .options(joinedload(Institution.expertise_entries))
            .all()
        )

        if not institutions:
            return []

        ranked_matches: List[Dict[str, Any]] = []
        for inst in institutions:
            score, reason = cls._evaluate_institution(challenge, inst)
            ranked_matches.append({
                "institution_id": inst.id,
                "institution_name": inst.name,
                "institution_type": inst.institution_type,
                "district": inst.district,
                "match_score": score,
                "match_reason": reason,
            })

        # Sort from highest match_score to lowest (tie-breaking with institution_id)
        ranked_matches.sort(key=lambda x: (-x["match_score"], x["institution_id"]))

        # Handle ChallengeAssignment records
        # 1. Fetch existing assignments for this challenge
        existing_assignments = (
            db.query(ChallengeAssignment)
            .filter(ChallengeAssignment.challenge_id == challenge_id)
            .all()
        )

        # 2. Preserve non-proposed assignments and remove existing proposed assignments
        preserved_institution_ids: Set[int] = set()
        for assignment in existing_assignments:
            if assignment.status != "proposed":
                preserved_institution_ids.add(assignment.institution_id)
            else:
                db.delete(assignment)

        db.flush()

        # 3. Insert ranked proposed matches (preventing duplicate rows for non-proposed ones)
        now = datetime.now(timezone.utc)
        for match_item in ranked_matches:
            if match_item["institution_id"] not in preserved_institution_ids:
                new_assignment = ChallengeAssignment(
                    challenge_id=challenge_id,
                    institution_id=match_item["institution_id"],
                    match_score=match_item["match_score"],
                    match_reason=match_item["match_reason"],
                    status="proposed",
                    assigned_at=now,
                )
                db.add(new_assignment)

        db.commit()

        return ranked_matches

    @staticmethod
    def get_stored_matches(
        db: Session,
        challenge_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve previously stored proposed matches for a specific challenge.
        """
        challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if not challenge:
            raise ValueError(f"Challenge with ID {challenge_id} not found.")

        assignments = (
            db.query(ChallengeAssignment)
            .options(joinedload(ChallengeAssignment.institution))
            .filter(
                ChallengeAssignment.challenge_id == challenge_id,
                ChallengeAssignment.status == "proposed",
            )
            .order_by(ChallengeAssignment.match_score.desc(), ChallengeAssignment.id.asc())
            .all()
        )

        stored_matches: List[Dict[str, Any]] = []
        for a in assignments:
            if a.institution:
                stored_matches.append({
                    "institution_id": a.institution.id,
                    "institution_name": a.institution.name,
                    "institution_type": a.institution.institution_type,
                    "district": a.institution.district,
                    "match_score": a.match_score if a.match_score is not None else 0.0,
                    "match_reason": a.match_reason or "",
                })

        return stored_matches
