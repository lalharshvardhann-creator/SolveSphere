import { api } from "./api";

// In-memory translation cache: Map<targetLang, Map<sourceText, translatedText>>
const memoryCache = new Map();

// In-flight promises to deduplicate simultaneous requests: Map<`${targetLang}:${text}`, Promise<string>>
const inFlightRequests = new Map();

// Helper to get cache for a specific language
function getLangCache(lang) {
  if (!memoryCache.has(lang)) {
    memoryCache.set(lang, new Map());
    // Load from sessionStorage if available
    try {
      const stored = sessionStorage.getItem(`solvesphere_trans_${lang}`);
      if (stored) {
        const parsed = JSON.parse(stored);
        for (const [k, v] of Object.entries(parsed)) {
          memoryCache.get(lang).set(k, v);
        }
      }
    } catch {
      // sessionStorage unavailable or restricted
    }
  }
  return memoryCache.get(lang);
}

// Persist lang cache to sessionStorage
function persistLangCache(lang) {
  try {
    const langMap = memoryCache.get(lang);
    if (langMap && langMap.size > 0) {
      const obj = Object.fromEntries(langMap.entries());
      sessionStorage.setItem(`solvesphere_trans_${lang}`, JSON.stringify(obj));
    }
  } catch {
    // ignore storage quota errors
  }
}

/**
 * Translate a batch of text strings into the target language.
 * Uses in-memory and session cache, deduplicating in-flight network requests.
 * Always returns original text for English or if translation fails.
 */
export async function translateBatch(texts, targetLang = "en") {
  if (!Array.isArray(texts) || texts.length === 0) {
    return [];
  }

  const cleanLang = (targetLang || "en").toLowerCase().trim();

  // English always uses the original text directly without network calls
  if (cleanLang === "en") {
    return texts;
  }

  const langCache = getLangCache(cleanLang);
  const results = new Array(texts.length);
  const uncachedIndices = [];
  const uncachedTexts = [];

  for (let i = 0; i < texts.length; i++) {
    const orig = texts[i];
    if (!orig || typeof orig !== "string" || !orig.trim()) {
      results[i] = orig || "";
      continue;
    }

    const trimmed = orig.trim();
    if (langCache.has(trimmed)) {
      results[i] = langCache.get(trimmed);
    } else {
      uncachedIndices.push(i);
      uncachedTexts.push(trimmed);
    }
  }

  // If all texts were cached or empty, return immediately
  if (uncachedTexts.length === 0) {
    return results;
  }

  // Deduplicate uncached strings for the API payload
  const uniqueUncached = Array.from(new Set(uncachedTexts));

  try {
    const response = await api.translate.batch(uniqueUncached, cleanLang);
    const translations = response?.translations || [];

    // Map unique translations back to langCache
    for (let i = 0; i < uniqueUncached.length; i++) {
      const key = uniqueUncached[i];
      const translatedVal = translations[i] || key;
      langCache.set(key, translatedVal);
    }
    persistLangCache(cleanLang);

    // Populate results array
    for (let j = 0; j < uncachedIndices.length; j++) {
      const origIndex = uncachedIndices[j];
      const trimmedKey = uncachedTexts[j];
      results[origIndex] = langCache.get(trimmedKey) || texts[origIndex];
    }
  } catch (err) {
    console.warn(`Dynamic translation failed for lang "${cleanLang}":`, err);
    // Graceful fallback to original text
    for (let j = 0; j < uncachedIndices.length; j++) {
      const origIndex = uncachedIndices[j];
      results[origIndex] = texts[origIndex];
    }
  }

  return results;
}

/**
 * Translate a single text string.
 */
export async function translateSingle(text, targetLang = "en") {
  if (!text || typeof text !== "string" || !text.trim() || targetLang === "en") {
    return text || "";
  }
  const [res] = await translateBatch([text], targetLang);
  return res || text;
}
