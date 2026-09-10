import { useState, useEffect } from "react";
import { useLanguage } from "../context/LanguageContext";
import { translateBatch } from "../services/translationService";

/**
 * Hook to translate a single text string with loading state.
 */
export function useTranslatedText(text) {
  const { currentLang } = useLanguage();
  const [translated, setTranslated] = useState(text || "");
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (!text || currentLang === "en") {
      setTranslated(text || "");
      setIsTranslating(false);
      return;
    }

    setIsTranslating(true);
    translateBatch([text], currentLang)
      .then(([res]) => {
        if (isMounted) {
          setTranslated(res || text);
        }
      })
      .catch(() => {
        if (isMounted) {
          setTranslated(text);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsTranslating(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [text, currentLang]);

  return { translated: translated || text || "", isTranslating };
}

/**
 * Hook to translate an array of challenges (titles and descriptions).
 */
export function useTranslatedChallenges(challenges = []) {
  const { currentLang } = useLanguage();
  const [translatedChallenges, setTranslatedChallenges] = useState(challenges);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (!challenges || challenges.length === 0 || currentLang === "en") {
      setTranslatedChallenges(challenges);
      setIsTranslating(false);
      return;
    }

    // Collect all titles and descriptions in paired order
    const textsToTranslate = [];
    challenges.forEach((c) => {
      textsToTranslate.push(c.title || "");
      textsToTranslate.push(c.description || "");
    });

    setIsTranslating(true);
    translateBatch(textsToTranslate, currentLang)
      .then((translations) => {
        if (!isMounted) return;
        const result = challenges.map((c, idx) => {
          const titleTrans = translations[idx * 2];
          const descTrans = translations[idx * 2 + 1];
          return {
            ...c,
            title: titleTrans || c.title,
            description: descTrans || c.description,
          };
        });
        setTranslatedChallenges(result);
      })
      .catch(() => {
        if (isMounted) {
          setTranslatedChallenges(challenges);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsTranslating(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [challenges, currentLang]);

  return {
    translatedChallenges: currentLang === "en" ? challenges : translatedChallenges,
    isTranslating,
  };
}

/**
 * Hook to translate a single challenge's detail view (title, description, AI analysis, matches).
 */
export function useTranslatedChallengeDetail(challenge, aiAnalysis = null, matches = []) {
  const { currentLang } = useLanguage();
  const [translatedData, setTranslatedData] = useState({
    challenge,
    aiAnalysis,
    matches,
  });
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (!challenge || currentLang === "en") {
      setTranslatedData({ challenge, aiAnalysis, matches });
      setIsTranslating(false);
      return;
    }

    // Build payload of dynamic fields
    const texts = [];
    // 0: title
    texts.push(challenge.title || "");
    // 1: description
    texts.push(challenge.description || "");
    // 2: AI problem summary
    texts.push(aiAnalysis?.problem_summary || "");

    // Suggested solution directions / required_expertise
    let solutionItems = [];
    if (typeof aiAnalysis?.required_expertise === "string" && aiAnalysis.required_expertise.trim()) {
      solutionItems = aiAnalysis.required_expertise
        .split(";")
        .map((s) => s.trim())
        .filter(Boolean);
    } else if (Array.isArray(aiAnalysis?.suggested_solutions)) {
      solutionItems = aiAnalysis.suggested_solutions;
    } else if (Array.isArray(aiAnalysis?.suggested_solution_directions)) {
      solutionItems = aiAnalysis.suggested_solution_directions;
    }

    const solutionStartIndex = texts.length;
    solutionItems.forEach((sol) => texts.push(sol || ""));
    const solutionEndIndex = texts.length;

    // Matches reasons
    const matchStartIndex = texts.length;
    matches.forEach((m) => texts.push(m.match_reason || ""));
    const matchEndIndex = texts.length;

    setIsTranslating(true);
    translateBatch(texts, currentLang)
      .then((translations) => {
        if (!isMounted) return;

        const transTitle = translations[0] || challenge.title;
        const transDesc = translations[1] || challenge.description;
        const transSummary = translations[2] || aiAnalysis?.problem_summary;

        const transSolutions = solutionItems.map((orig, i) => {
          return translations[solutionStartIndex + i] || orig;
        });

        const transMatches = matches.map((m, i) => {
          return {
            ...m,
            match_reason: translations[matchStartIndex + i] || m.match_reason,
          };
        });

        setTranslatedData({
          challenge: {
            ...challenge,
            title: transTitle,
            description: transDesc,
          },
          aiAnalysis: aiAnalysis
            ? {
                ...aiAnalysis,
                problem_summary: transSummary,
                required_expertise: transSolutions.join("; "),
                suggested_solutions: transSolutions,
                suggested_solution_directions: transSolutions,
              }
            : null,
          matches: transMatches,
        });
      })
      .catch(() => {
        if (isMounted) {
          setTranslatedData({ challenge, aiAnalysis, matches });
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsTranslating(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [challenge, aiAnalysis, matches, currentLang]);

  return {
    translatedChallenge: currentLang === "en" ? challenge : translatedData.challenge,
    translatedAIAnalysis: currentLang === "en" ? aiAnalysis : translatedData.aiAnalysis,
    translatedMatches: currentLang === "en" ? matches : translatedData.matches,
    isTranslating,
  };
}

/**
 * Hook to translate an array of institutions (descriptions and expertise entries).
 */
export function useTranslatedInstitutions(institutions = []) {
  const { currentLang } = useLanguage();
  const [translatedInstitutions, setTranslatedInstitutions] = useState(institutions);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (!institutions || institutions.length === 0 || currentLang === "en") {
      setTranslatedInstitutions(institutions);
      setIsTranslating(false);
      return;
    }

    const texts = [];
    const mapping = [];

    institutions.forEach((inst, instIdx) => {
      // Description
      if (inst.description) {
        texts.push(inst.description);
        mapping.push({ instIdx, field: "description" });
      }

      // Expertise entries
      const expList = inst.expertise_entries || inst.expertise || [];
      if (Array.isArray(expList)) {
        expList.forEach((exp, expIdx) => {
          if (exp.research_areas) {
            texts.push(exp.research_areas);
            mapping.push({ instIdx, expIdx, field: "research_areas" });
          }
          if (exp.facilities) {
            texts.push(exp.facilities);
            mapping.push({ instIdx, expIdx, field: "facilities" });
          }
        });
      }
    });

    if (texts.length === 0) {
      setTranslatedInstitutions(institutions);
      setIsTranslating(false);
      return;
    }

    setIsTranslating(true);
    translateBatch(texts, currentLang)
      .then((translations) => {
        if (!isMounted) return;

        const cloned = JSON.parse(JSON.stringify(institutions));

        mapping.forEach((item, tIdx) => {
          const transVal = translations[tIdx];
          if (!transVal) return;

          const targetInst = cloned[item.instIdx];
          if (!targetInst) return;

          if (item.field === "description") {
            targetInst.description = transVal;
          } else if (item.field === "research_areas") {
            const expList = targetInst.expertise_entries || targetInst.expertise;
            if (expList && expList[item.expIdx]) {
              expList[item.expIdx].research_areas = transVal;
            }
          } else if (item.field === "facilities") {
            const expList = targetInst.expertise_entries || targetInst.expertise;
            if (expList && expList[item.expIdx]) {
              expList[item.expIdx].facilities = transVal;
            }
          }
        });

        setTranslatedInstitutions(cloned);
      })
      .catch(() => {
        if (isMounted) {
          setTranslatedInstitutions(institutions);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsTranslating(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [institutions, currentLang]);

  return {
    translatedInstitutions: currentLang === "en" ? institutions : translatedInstitutions,
    isTranslating,
  };
}

/**
 * Hook to translate a single institution's full detail view (description, research areas, facilities).
 */
export function useTranslatedInstitutionDetail(inst) {
  const { currentLang } = useLanguage();
  const [translatedInst, setTranslatedInst] = useState(inst);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (!inst || currentLang === "en") {
      setTranslatedInst(inst);
      setIsTranslating(false);
      return;
    }

    const texts = [];
    const mapping = [];

    if (inst.description) {
      texts.push(inst.description);
      mapping.push({ field: "description" });
    }

    const expList = inst.expertise_entries || inst.expertise || [];
    if (Array.isArray(expList)) {
      expList.forEach((exp, expIdx) => {
        if (exp.research_areas) {
          texts.push(exp.research_areas);
          mapping.push({ expIdx, field: "research_areas" });
        }
        if (exp.facilities) {
          texts.push(exp.facilities);
          mapping.push({ expIdx, field: "facilities" });
        }
      });
    }

    if (texts.length === 0) {
      setTranslatedInst(inst);
      setIsTranslating(false);
      return;
    }

    setIsTranslating(true);
    translateBatch(texts, currentLang)
      .then((translations) => {
        if (!isMounted) return;

        const cloned = JSON.parse(JSON.stringify(inst));

        mapping.forEach((item, tIdx) => {
          const transVal = translations[tIdx];
          if (!transVal) return;

          if (item.field === "description") {
            cloned.description = transVal;
          } else if (item.field === "research_areas") {
            const expList = cloned.expertise_entries || cloned.expertise;
            if (expList && expList[item.expIdx]) {
              expList[item.expIdx].research_areas = transVal;
            }
          } else if (item.field === "facilities") {
            const expList = cloned.expertise_entries || cloned.expertise;
            if (expList && expList[item.expIdx]) {
              expList[item.expIdx].facilities = transVal;
            }
          }
        });

        setTranslatedInst(cloned);
      })
      .catch(() => {
        if (isMounted) {
          setTranslatedInst(inst);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsTranslating(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [inst, currentLang]);

  return {
    translatedInst: currentLang === "en" ? inst : translatedInst,
    isTranslating,
  };
}
