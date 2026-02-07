"use client";

import { useState, useRef, useEffect } from "react";
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
}

export function ModelSelector({ level, onModelChange, className }: ModelSelectorProps) {
  const defaults = LEVEL_DEFAULTS[level] ?? { providerId: DEFAULT_PROVIDER_ID, modelId: DEFAULT_MODEL_ID };

  const [isOpen, setIsOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState(defaults.providerId);
  const [selectedModel, setSelectedModel] = useState(defaults.modelId);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

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

  return (
    <div ref={dropdownRef} className={cn("relative inline-block", className)}>
      {/* Compact inline trigger – sits next to "Level X" */}
      <button
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

      {/* Dropdown */}
      {isOpen && (
        <div
          className={cn(
            "absolute left-0 mt-2 w-64 z-50",
            "bg-card border-2 border-border rounded-none shadow-xl pixel-border",
            "max-h-72 overflow-y-auto custom-scrollbar"
          )}
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
        </div>
      )}
    </div>
  );
}
