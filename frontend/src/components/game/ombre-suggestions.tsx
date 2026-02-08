"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { ArenaAPI, type OmbreInfo } from "@/lib/api";
import { OMBRE_CHARACTERS } from "@/lib/constants";
import {
  Skull,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Lock,
  Zap,
  RefreshCw,
} from "lucide-react";

// Dark villain color themes — pixelized shadow aesthetic
const OMBRE_STYLES: Record<number, { border: string; bg: string; text: string; shadow: string }> = {
  1: {
    border: "border-lime-600/30",
    bg: "bg-lime-950/60",
    text: "text-lime-400",
    shadow: "shadow-[0_0_20px_rgba(132,204,22,0.15)]",
  },
  2: {
    border: "border-slate-500/30",
    bg: "bg-slate-950/60",
    text: "text-slate-300",
    shadow: "shadow-[0_0_20px_rgba(148,163,184,0.15)]",
  },
  3: {
    border: "border-purple-600/30",
    bg: "bg-purple-950/60",
    text: "text-purple-400",
    shadow: "shadow-[0_0_20px_rgba(168,85,247,0.15)]",
  },
  4: {
    border: "border-red-700/30",
    bg: "bg-red-950/60",
    text: "text-red-400",
    shadow: "shadow-[0_0_20px_rgba(239,68,68,0.15)]",
  },
  5: {
    border: "border-amber-600/30",
    bg: "bg-amber-950/60",
    text: "text-amber-300",
    shadow: "shadow-[0_0_20px_rgba(251,191,36,0.15)]",
  },
};

interface OmbreSuggestionsProps {
  onSuggestionSelect: (suggestion: string) => void;
  currentLevel: number;
  chatHistory: { role: string; content: string }[];
  disabled?: boolean;
}

export function OmbreSuggestions({
  onSuggestionSelect,
  currentLevel,
  chatHistory,
  disabled = false,
}: OmbreSuggestionsProps) {
  const [ombres, setOmbres] = useState<OmbreInfo[]>([]);
  const [loadingOmbres, setLoadingOmbres] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [selectedOmbre, setSelectedOmbre] = useState<number | null>(null);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [loadingSuggestion, setLoadingSuggestion] = useState(false);
  const [suggestionError, setSuggestionError] = useState<string | null>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const updateScrollArrows = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 0);
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 1);
  }, []);

  const scroll = useCallback((direction: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    const amount = 250;
    el.scrollBy({ left: direction === "left" ? -amount : amount, behavior: "smooth" });
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    updateScrollArrows();
    el.addEventListener("scroll", updateScrollArrows, { passive: true });
    const ro = new ResizeObserver(updateScrollArrows);
    ro.observe(el);
    return () => {
      el.removeEventListener("scroll", updateScrollArrows);
      ro.disconnect();
    };
  }, [expanded, ombres, updateScrollArrows]);

  useEffect(() => {
    async function fetchOmbres() {
      setLoadingOmbres(true);
      const data = await ArenaAPI.getOmbres();
      setOmbres(data);
      setLoadingOmbres(false);
    }
    fetchOmbres();
  }, []);

  useEffect(() => {
    setSelectedOmbre(null);
    setSuggestion(null);
    setSuggestionError(null);
  }, [currentLevel]);

  const fetchSuggestion = useCallback(
    async (ombreLevel: number) => {
      setLoadingSuggestion(true);
      setSuggestion(null);
      setSuggestionError(null);

      try {
        const result = await ArenaAPI.getSuggestion(
          ombreLevel,
          currentLevel,
          chatHistory
        );
        setSuggestion(result.suggestion);
      } catch (err) {
        setSuggestionError("Failed to conjure suggestion. The shadows falter...");
      } finally {
        setLoadingSuggestion(false);
      }
    },
    [currentLevel, chatHistory]
  );

  const handleOmbreClick = useCallback(
    (ombreLevel: number) => {
      if (disabled) return;

      if (selectedOmbre === ombreLevel) {
        setSelectedOmbre(null);
        setSuggestion(null);
        setSuggestionError(null);
      } else {
        setSelectedOmbre(ombreLevel);
        fetchSuggestion(ombreLevel);
      }
    },
    [selectedOmbre, disabled, fetchSuggestion]
  );

  if (loadingOmbres) {
    return (
      <div className="flex items-center gap-2 px-1 py-1.5">
        <Loader2 className="w-3.5 h-3.5 animate-spin text-red-400/50" />
        <span className="text-xs text-red-400/50 font-pixel">Summoning shadows...</span>
      </div>
    );
  }

  if (ombres.length === 0) return null;

  const selectedOmbreInfo = ombres.find((o) => o.level === selectedOmbre);
  const selectedStyle = selectedOmbre ? OMBRE_STYLES[selectedOmbre] || OMBRE_STYLES[1] : null;
  const selectedChar = selectedOmbre ? OMBRE_CHARACTERS[selectedOmbre] : null;

  return (
    <div className="space-y-2">
      {/* Toggle Header — dark & ominous */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 w-full group"
      >
        <div className="flex-1 h-px bg-gradient-to-l from-red-500/20 via-red-500/5 to-transparent" />
        <Skull className="w-3.5 h-3.5 text-red-500/70 group-hover:text-red-400 transition-all group-hover:drop-shadow-[0_0_6px_rgba(239,68,68,0.6)]" />
        <span className="font-pixel text-[10px] uppercase tracking-widest text-red-400/60 group-hover:text-red-400/90 transition-colors whitespace-nowrap">
          Les Ombres — Shadow Whispers
        </span>
        <ChevronDown className={`w-3 h-3 text-red-400/50 group-hover:text-red-400/80 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`} />
        <div className="flex-1 h-px bg-gradient-to-r from-red-500/20 via-red-500/5 to-transparent" />
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {/* Ombre Cards — horizontal row matching guardian dimensions */}
            <div className="relative">
              {canScrollLeft && (
                <button
                  onClick={() => scroll("left")}
                  className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-7 h-7 flex items-center justify-center bg-black/90 border border-red-500/30 rounded-sm shadow-lg hover:bg-red-950/40 hover:border-red-500/50 transition-all"
                >
                  <ChevronLeft className="w-4 h-4 text-red-400/80" />
                </button>
              )}

              <div
                ref={scrollRef}
                className="flex gap-2 overflow-x-auto pb-2 px-1 scrollbar-none"
                style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
              >
                {ombres.map((ombre) => {
                  const style = OMBRE_STYLES[ombre.level] || OMBRE_STYLES[1];
                  const char = OMBRE_CHARACTERS[ombre.level];
                  const isSelected = selectedOmbre === ombre.level;
                  const isUnlocked = ombre.level <= currentLevel;

                  return (
                    <motion.button
                      key={ombre.level}
                      onClick={() => isUnlocked && handleOmbreClick(ombre.level)}
                      whileHover={isUnlocked ? { scale: 1.02, y: -2 } : {}}
                      whileTap={isUnlocked ? { scale: 0.98 } : {}}
                      className={cn(
                        "flex-shrink-0 w-full max-w-[240px] p-3 text-left transition-all duration-200 flex items-center gap-3",
                        "bg-black/50 backdrop-blur-sm border-2 rounded-none",
                        isUnlocked
                          ? isSelected
                            ? `${style.bg} ${style.border} ${style.shadow}`
                            : "border-white/[0.08] hover:border-white/[0.15] hover:bg-black/70"
                          : "border-white/[0.04] opacity-40 cursor-not-allowed grayscale",
                        (disabled && isUnlocked) && "opacity-50 cursor-not-allowed"
                      )}
                      disabled={disabled || !isUnlocked}
                    >
                      <div className={cn(
                        "w-10 h-10 rounded-xl overflow-hidden flex-shrink-0 border-2",
                        isSelected ? style.border : "border-white/10",
                        !isUnlocked && "opacity-50"
                      )}>
                        {char ? (
                          <Image
                            src={char.image}
                            alt={char.name}
                            width={40}
                            height={40}
                            className={cn("object-cover w-full h-full", !isUnlocked && "grayscale blur-[1px]")}
                          />
                        ) : (
                          <div className="w-full h-full bg-black/80 flex items-center justify-center">
                            <Skull className="w-5 h-5 text-red-500/40" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className={cn(
                            "font-medium text-sm truncate font-pixel block",
                            isSelected ? style.text : "text-foreground/80"
                          )}>
                            {char ? char.name : ombre.name}
                          </span>
                          {!isUnlocked && (
                            <Lock className="w-4 h-4 text-red-500/30 flex-shrink-0" />
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground/60 truncate block">
                          Level {ombre.level}
                        </span>
                      </div>
                    </motion.button>
                  );
                })}
              </div>

              {canScrollRight && (
                <button
                  onClick={() => scroll("right")}
                  className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-7 h-7 flex items-center justify-center bg-black/90 border border-red-500/30 rounded-sm shadow-lg hover:bg-red-950/40 hover:border-red-500/50 transition-all"
                >
                  <ChevronRight className="w-4 h-4 text-red-400/80" />
                </button>
              )}
            </div>

            {/* Suggestion Display */}
            <AnimatePresence mode="wait">
              {selectedOmbre !== null && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                  className="mt-3"
                >
                  {loadingSuggestion && (
                    <div className={cn(
                      "px-4 py-3 border-2 rounded-none bg-black/60 backdrop-blur-sm",
                      selectedStyle?.border || "border-red-500/20"
                    )}>
                      <div className="flex items-center gap-3">
                        <Loader2 className={cn("w-5 h-5 animate-spin", selectedStyle?.text || "text-red-400")} />
                        <span className="text-sm font-game text-muted-foreground">
                          <span className={selectedStyle?.text}>{selectedOmbreInfo?.name}</span> weaves dark whispers...
                        </span>
                      </div>
                    </div>
                  )}

                  {suggestionError && (
                    <div className="px-4 py-3 border-2 border-red-600/40 rounded-none bg-red-950/40 backdrop-blur-sm">
                      <p className="text-sm text-red-400 font-game">{suggestionError}</p>
                    </div>
                  )}

                  {suggestion && !loadingSuggestion && (
                    <div
                      className={cn(
                        "w-full px-4 py-3 border-2 rounded-none transition-all",
                        "bg-black/60 backdrop-blur-sm",
                        selectedStyle?.border || "border-red-500/20",
                        selectedStyle?.shadow
                      )}
                    >
                      <div className="flex items-center gap-3">
                        {/* Ombre Name */}
                        <div className="flex-shrink-0">
                          <span className={cn(
                            "font-pixel text-xs uppercase tracking-wide",
                            selectedStyle?.text || "text-red-400"
                          )}>
                            {selectedOmbreInfo?.name} whispers:
                          </span>
                        </div>

                        {/* Suggestion Text */}
                        <motion.button
                          initial={{ scale: 0.98, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          onClick={() => onSuggestionSelect(suggestion)}
                          disabled={disabled}
                          className={cn(
                            "flex-1 px-3 py-2 border rounded-none text-left transition-all group/btn",
                            "bg-black/40 hover:bg-black/60",
                            selectedStyle?.border || "border-white/10",
                            "hover:border-opacity-40 active:scale-[0.99]",
                            disabled && "opacity-50 cursor-not-allowed"
                          )}
                        >
                          <div className="flex items-center justify-between gap-2">
                            <p className={cn(
                              "text-sm font-game leading-relaxed flex-1",
                              "text-foreground/90"
                            )}>
                              {suggestion}
                            </p>
                            <Zap className={cn("w-4 h-4 flex-shrink-0 opacity-60 group-hover/btn:opacity-100 transition-opacity", selectedStyle?.text || "text-red-400")} />
                          </div>
                        </motion.button>

                        {/* Regenerate Button */}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            fetchSuggestion(selectedOmbre!);
                          }}
                          disabled={disabled || loadingSuggestion}
                          className={cn(
                            "flex-shrink-0 p-2 border rounded-none transition-all",
                            "bg-black/40 hover:bg-black/60",
                            selectedStyle?.border || "border-red-500/30",
                            "hover:border-opacity-60 disabled:opacity-50 disabled:cursor-not-allowed"
                          )}
                          title="Generate new suggestion"
                        >
                          <RefreshCw className={cn("w-4 h-4", selectedStyle?.text || "text-red-400")} />
                        </button>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
