import React, { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Volume2, AlertCircle, RotateCcw, Check, Globe } from "lucide-react";
import { useLanguage } from "../context/LanguageContext";

// Browser capability detection helper
function checkSpeechSupport() {
  return (
    typeof window !== "undefined" &&
    !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  );
}

// Map speech recognition error codes to friendly messages
function getErrorMessage(errCode) {
  switch (errCode) {
    case "network":
      return "Voice recognition is temporarily unavailable. You can type your problem instead.";
    case "not-allowed":
    case "permission-denied":
      return "Microphone access is blocked. Allow microphone access in browser settings.";
    case "no-speech":
      return "No speech detected. Click Try Again and speak clearly into your microphone.";
    case "audio-capture":
      return "No microphone found. Please connect an audio input device.";
    case "service-not-allowed":
      return "Voice recognition service is blocked by your browser (e.g. Brave shields). You can type your problem instead.";
    case "language-not-supported":
      return "The selected language is not supported by your browser speech engine. You can type your problem instead.";
    case "unsupported":
      return "Voice input is not supported in this browser. Please use Chrome or Edge, or type your problem.";
    default:
      return "Voice recognition encountered an issue. You can type your problem instead.";
  }
}

// Map language codes to Web Speech API speech recognition locales
function getSpeechLocale(langCode) {
  switch (langCode) {
    case "en":
      return "en-IN";
    case "hi":
      return "hi-IN";
    case "nag":
      return "hi-IN"; // Nagpuri / Sadri phonetics align with Hindi acoustic model
    case "sat":
      return "hi-IN"; // Santali regional acoustic fallback for browser speech engine
    default:
      return "en-IN";
  }
}

export default function VoiceRecorder({ onTranscript }) {
  const { t, currentLang, languages } = useLanguage();
  const isSupported = checkSpeechSupport();

  const [isRecording, setIsRecording] = useState(false);
  const [interimText, setInterimText] = useState("");
  const [selectedVoiceLang, setSelectedVoiceLang] = useState(currentLang);
  const [prevLang, setPrevLang] = useState(currentLang);
  const [errorMsg, setErrorMsg] = useState(
    !isSupported
      ? "Voice input is not supported in this browser. Please use Chrome or Edge, or type your problem."
      : ""
  );
  const [appendedNotice, setAppendedNotice] = useState(false);

  const recognitionRef = useRef(null);
  const isStoppingRef = useRef(false);

  // Sync selected voice language when UI language changes
  if (prevLang !== currentLang) {
    setPrevLang(currentLang);
    setSelectedVoiceLang(currentLang);
  }

  const startRecognition = () => {
    const SpeechRecognition =
      typeof window !== "undefined" &&
      (window.SpeechRecognition || window.webkitSpeechRecognition);

    if (!SpeechRecognition) {
      setErrorMsg(getErrorMessage("unsupported"));
      return;
    }

    setErrorMsg("");
    setInterimText("");
    isStoppingRef.current = false;

    try {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore previous abort
        }
      }

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = getSpeechLocale(selectedVoiceLang);
      recognition.maxAlternatives = 1;

      recognition.onstart = () => {
        setIsRecording(true);
        setErrorMsg("");
      };

      recognition.onresult = (event) => {
        let interim = "";
        let finalChunk = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const res = event.results[i];
          if (res.isFinal) {
            finalChunk += res[0].transcript + " ";
          } else {
            interim += res[0].transcript;
          }
        }

        setInterimText(interim);

        if (finalChunk.trim()) {
          const textToAppend = finalChunk.trim();
          if (onTranscript) {
            onTranscript(textToAppend);
          }
          setAppendedNotice(true);
          setTimeout(() => setAppendedNotice(false), 3500);
        }
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        const err = event.error || "unknown";
        if (err === "no-speech" && isStoppingRef.current) {
          return;
        }
        setErrorMsg(getErrorMessage(err));
        setIsRecording(false);
        setInterimText("");
      };

      recognition.onend = () => {
        setIsRecording(false);
        setInterimText("");
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error("Failed to start speech recognition:", err);
      setErrorMsg(getErrorMessage("audio-capture"));
      setIsRecording(false);
    }
  };

  const stopRecognition = () => {
    isStoppingRef.current = true;
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {
        setIsRecording(false);
      }
    } else {
      setIsRecording(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecognition();
    } else {
      startRecognition();
    }
  };

  const handleTryAgain = () => {
    setErrorMsg("");
    startRecognition();
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  const currentLangObj = languages.find((l) => l.code === selectedVoiceLang) || languages[0];

  return (
    <div className="voice-recorder-card">
      <div className="voice-header">
        <div className="voice-title-group">
          <div className="voice-icon-pill">
            <Mic size={18} className="text-green" />
          </div>
          <div>
            <h4 className="voice-title">{t("voiceTitle") || "Speak Your Problem"}</h4>
            <p className="voice-subtitle">{t("voiceInstruction") || "Speak in your language"}</p>
          </div>
        </div>

        {/* Voice Language Selector */}
        <div className="voice-lang-picker">
          <Globe size={14} className="text-muted" />
          <label htmlFor="voice-lang-select" className="sr-only">Voice Language</label>
          <select
            id="voice-lang-select"
            value={selectedVoiceLang}
            onChange={(e) => setSelectedVoiceLang(e.target.value)}
            disabled={isRecording}
            className="voice-lang-select"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.nativeName} ({lang.name})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Microphone Action Area */}
      <div className="voice-action-area">
        <button
          type="button"
          onClick={toggleRecording}
          disabled={!isSupported}
          className={`mic-btn ${isRecording ? "mic-btn-recording" : ""}`}
          aria-label={isRecording ? t("voiceStop") : t("voiceStart")}
        >
          {isRecording ? <MicOff size={28} /> : <Mic size={28} />}
        </button>

        <div className="voice-status-text">
          {isRecording ? (
            <div className="voice-recording-indicator">
              <span className="live-dot"></span>
              <strong>{t("voiceListening") || "Listening..."}</strong>
              <span className="speaking-lang">({currentLangObj.nativeName})</span>
            </div>
          ) : (
            <div className="voice-idle-indicator">
              <span>{t("voiceStart") || "Click to Speak"}</span>
              <small className="text-muted">Click microphone and speak into your device</small>
            </div>
          )}
        </div>
      </div>

      {/* Live Interim Transcript */}
      {(isRecording || interimText) && (
        <div className="interim-transcript-box">
          <Volume2 size={16} className="text-green animate-pulse" />
          <p className="interim-text">
            {interimText || "Listening for speech..."}
          </p>
        </div>
      )}

      {/* Appended to Description Badge */}
      {appendedNotice && (
        <div className="voice-appended-badge">
          <Check size={14} />
          <span>Added to problem description below!</span>
        </div>
      )}

      {/* Specific Error & Try Again Action */}
      {errorMsg && (
        <div className="voice-error-notice">
          <div className="voice-error-header">
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
          <div className="voice-error-actions">
            {isSupported && (
              <button
                type="button"
                onClick={handleTryAgain}
                className="btn-try-again"
              >
                <RotateCcw size={13} />
                <span>Try Again</span>
              </button>
            )}
            <span className="voice-fallback-hint">You can type your problem directly in the box below.</span>
          </div>
        </div>
      )}
    </div>
  );
}
