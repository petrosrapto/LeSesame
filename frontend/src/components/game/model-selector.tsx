"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { createPortal } from "react-dom";
import { ChevronDown, Cpu } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  providers,
  LEVEL_DEFAULTS,
  DEFAULT_PROVIDER_ID,
  DEFAULT_MODEL_ID,
  type ModelConfig,
  buildModelConfig,
} from "@/lib/model-providers";

interface ModelSelectorProps {
  level: number;
  onModelChange: (config: ModelConfig, displayLabel: string) => void;
  className?: string;
  dropUp?: boolean;
}

export function ModelSelector({ level, onModelChange, className, dropUp = false }: ModelSelectorProps) {
  const defaults = LEVEL_DEFAULTS[level] ?? { providerId: DEFAULT_PROVIDER_ID, modelId: DEFAULT_MODEL_ID };

  const [isOpen, setIsOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(defaults.providerId);
  const [selectedModel, setSelectedModel] = useState(defaults.modelId);
  const [dropdownPos, setDropdownPos] = useState<{ top: number; left: number } | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Reset selection when level changes
  useEffect(() => {
    const lvlDefaults = LEVEL_DEFAULTS[level] ?? { providerId: DEFAULT_PROVIDER_ID, modelId: DEFAULT_MODEL_ID };
    setSelectedProvider(lvlDefaults.providerId);
    setSelectedModel(lvlDefaults.modelId);
    onModelChange(
      buildModelConfig(lvlDefaults.providerId, lvlDefaults.modelId),
      getLabel(lvlDefaults.providerId, lvlDefaults.modelId)
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level]);

  // Position the dropdown when it opens
  const updatePosition = useCallback(() => {
    if (!triggerRef.current) return;
    const rect = triggerRef.current.getBoundingClientRect();
    if (dropUp) {
      setDropdownPos({ top: rect.top, left: rect.left });
    } else {
      setDropdownPos({ top: rect.bottom + 4, left: rect.left });
    }
  }, [dropUp]);

  useEffect(() => {
    if (!isOpen) return;
    updatePosition();
    function handleScroll(e: Event) {
      // Don't close when scrolling inside the dropdown itself
      if (dropdownRef.current?.contains(e.target as Node)) return;
      setIsOpen(false);
    }
    window.addEventListener("scroll", handleScroll, { capture: true });
    return () => window.removeEventListener("scroll", handleScroll, { capture: true });
  }, [isOpen, updatePosition]);

  // Close dropdown on outside click
  useEffect(() => {
    if (!isOpen) return;
    function handleClick(e: MouseEvent) {
      const target = e.target as Node;
      if (
        wrapperRef.current?.contains(target) ||
        dropdownRef.current?.contains(target)
      ) {
        return;
      }
      setIsOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [isOpen]);

  const currentProvider = providers.find(
    (p) => p.providerId === selectedProvider
  );
  const currentModel = currentProvider?.models.find(
    (m) => m.apiIdentifier === selectedModel
  );

  function getLabel(provId: string, modId: string): string {
    const prov = providers.find((p) => p.providerId === provId);
    const mod = prov?.models.find((m) => m.apiIdentifier === modId);
    return mod ? `${prov?.displayName} · ${mod.displayName}` : "Select model";
  }

  const displayLabel = currentModel
    ? `${currentProvider?.displayName} · ${currentModel.displayName}`
    : "Select model";

  function selectModel(providerId: string, modelId: string) {
    setSelectedProvider(providerId);
    setSelectedModel(modelId);
    setIsOpen(false);
    onModelChange(
      buildModelConfig(providerId, modelId),
      getLabel(providerId, modelId)
    );
  }

  const dropdownContent = isOpen && dropdownPos && createPortal(
    <div
      ref={dropdownRef}
      className={cn(
        "fixed w-64 z-[9999]",
        "bg-card border-2 border-border rounded-none shadow-xl pixel-border",
        "max-h-72 overflow-y-auto custom-scrollbar"
      )}
      style={
        dropUp
          ? { bottom: window.innerHeight - dropdownPos.top + 4, left: dropdownPos.left }
          : { top: dropdownPos.top, left: dropdownPos.left }
      }
    >
      {providers.map((provider) => (
        <div key={provider.providerId}>
          {/* Provider header */}
          <div className="px-3 py-1.5 text-[10px] font-bold text-muted-foreground uppercase tracking-widest bg-secondary/60 border-b border-border/40 font-pixel">
            {provider.displayName}
          </div>
          {/* Models */}
          {provider.models.map((model) => {
            const isSelected =
              provider.providerId === selectedProvider &&
              model.apiIdentifier === selectedModel;
            return (
              <button
                key={`${provider.providerId}-${model.apiIdentifier}`}
                onClick={() =>
                  selectModel(provider.providerId, model.apiIdentifier)
                }
                className={cn(
                  "w-full text-left px-4 py-1.5 text-xs transition-colors font-game",
                  "hover:bg-secondary/80",
                  isSelected
                    ? "bg-orange-500/15 text-orange-500 font-semibold"
                    : "text-foreground/80"
                )}
              >
                {model.displayName}
              </button>
            );
          })}
        </div>
      ))}
    </div>,
    document.body
  );

  return (
    <div ref={wrapperRef} className={cn("relative inline-block", className)}>
      {/* Compact inline trigger – sits next to "Level X" */}
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setIsOpen((v) => !v)}
        className={cn(
          "inline-flex items-center gap-1 px-2 py-0.5 rounded-full",
          "border border-border/60 bg-secondary/40 text-[11px]",
          "hover:bg-secondary/80 hover:border-border transition-colors duration-150",
          "focus:outline-none focus-visible:ring-1 focus-visible:ring-ring",
          "text-muted-foreground hover:text-foreground"
        )}
      >
        <Cpu className="w-3 h-3 text-orange-500 flex-shrink-0" />
        <span className="truncate max-w-[160px]">{displayLabel}</span>
        <ChevronDown
          className={cn(
            "w-3 h-3 text-muted-foreground/60 transition-transform duration-150 flex-shrink-0",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {dropdownContent}
    </div>
  );
}
