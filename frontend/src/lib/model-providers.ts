// Model providers and their available models for the AI guardian.
// Mirrors the backend's get_llm expected config structure:
//   { provider, model_id, endpoint_url?, args? }

export interface ModelOption {
  displayName: string;
  apiIdentifier: string;
  endpoint?: string;
}

export interface Provider {
  displayName: string;
  providerId: string;
  /** Maps to backend `provider` field in model_config */
  apiName: string;
  models: ModelOption[];
}

// ---------------------------------------------------------------------------
// Providers – Mistral listed first, then the rest alphabetically-ish
// ---------------------------------------------------------------------------

export const providers: Provider[] = [
  // ── Mistral (native provider) ──────────────────────────────────────────
  {
    displayName: "Mistral",
    providerId: "mistral",
    apiName: "mistral",
    models: [
      // Frontier
      { displayName: "Mistral Large 3",          apiIdentifier: "mistral-large-2512" },
      { displayName: "Mistral Medium 3.1",       apiIdentifier: "mistral-medium-2508" },
      { displayName: "Mistral Small 3.2",        apiIdentifier: "mistral-small-2506" },
      // Ministral
      { displayName: "Ministral 3 14B",          apiIdentifier: "ministral-14b-2512" },
      { displayName: "Ministral 3 8B",           apiIdentifier: "ministral-8b-2512" },
      { displayName: "Ministral 3 3B",           apiIdentifier: "ministral-3b-2512" },
      // Magistral (reasoning)
      { displayName: "Magistral Medium 1.2",     apiIdentifier: "magistral-medium-2509" },
      { displayName: "Magistral Small 1.2",      apiIdentifier: "magistral-small-2509" },
      // Specialist / other
      { displayName: "Mistral Nemo 12B",         apiIdentifier: "open-mistral-nemo" },
      { displayName: "Codestral",                apiIdentifier: "codestral-2508" },
    ],
  },

  // ── Google (native provider) ───────────────────────────────────────────
  {
    displayName: "Google",
    providerId: "google",
    apiName: "google",
    models: [
      { displayName: "Gemini 3 Pro",         apiIdentifier: "gemini-3-pro-preview" },
      { displayName: "Gemini 3 Flash",        apiIdentifier: "gemini-3-flash-preview" },
      { displayName: "Gemini 2.5 Pro",        apiIdentifier: "gemini-2.5-pro" },
      { displayName: "Gemini 2.5 Flash",      apiIdentifier: "gemini-2.5-flash" },

      { displayName: "Gemini 2.0 Flash",      apiIdentifier: "gemini-2.0-flash" },
    ],
  },

  // ── Anthropic (native provider) ────────────────────────────────────────
  {
    displayName: "Anthropic",
    providerId: "anthropic",
    apiName: "anthropic",
    models: [
      { displayName: "Claude Opus 4.6",     apiIdentifier: "claude-opus-4-6" },
      { displayName: "Claude Opus 4.5",     apiIdentifier: "claude-opus-4-5-20251101" },
      { displayName: "Claude Sonnet 4.5",   apiIdentifier: "claude-sonnet-4-5-20250929" },
      { displayName: "Claude Haiku 4.5",    apiIdentifier: "claude-haiku-4-5-20251001" },
      { displayName: "Claude Opus 4.1",     apiIdentifier: "claude-opus-4-1-20250805" },
      { displayName: "Claude Opus 4",       apiIdentifier: "claude-opus-4-20250514" },
      { displayName: "Claude Sonnet 4",     apiIdentifier: "claude-sonnet-4-20250514" },
      { displayName: "Claude Sonnet 3.7",   apiIdentifier: "claude-3-7-sonnet-20250219" },
      { displayName: "Claude Haiku 3.5",    apiIdentifier: "claude-3-5-haiku-20241022" },
      { displayName: "Claude Haiku 3",      apiIdentifier: "claude-3-haiku-20240307" },
    ],
  },

  // ── OpenAI (native provider) ───────────────────────────────────────────
  {
    displayName: "OpenAI",
    providerId: "openai",
    apiName: "openai",
    models: [
      // GPT-5
      { displayName: "GPT-5",        apiIdentifier: "gpt-5" },
      { displayName: "GPT-5 mini",   apiIdentifier: "gpt-5-mini" },
      // GPT-4.1
      { displayName: "GPT-4.1",      apiIdentifier: "gpt-4.1" },
      { displayName: "GPT-4.1 mini", apiIdentifier: "gpt-4.1-mini" },
      { displayName: "GPT-4.1 nano", apiIdentifier: "gpt-4.1-nano" },
      // GPT-4o
      { displayName: "GPT-4o",       apiIdentifier: "gpt-4o" },
      { displayName: "GPT-4o mini",  apiIdentifier: "gpt-4o-mini" },
      // Reasoning
      { displayName: "o4 mini",      apiIdentifier: "o4-mini" },
      { displayName: "o3",           apiIdentifier: "o3" },
      { displayName: "o3 mini",      apiIdentifier: "o3-mini" },
    ],
  },

  // ── AWS Bedrock (native provider) ──────────────────────────────────────
  {
    displayName: "AWS Bedrock",
    providerId: "aws",
    apiName: "bedrock",
    models: [
      // Anthropic
      { displayName: "Claude Sonnet 4",           apiIdentifier: "us.anthropic.claude-sonnet-4-20250514-v1:0" },
      { displayName: "Claude 3.5 Haiku",          apiIdentifier: "us.anthropic.claude-3-5-haiku-20241022-v1:0" },
      // Meta Llama
      { displayName: "Llama 4 Maverick 17B",      apiIdentifier: "us.meta.llama4-maverick-17b-instruct-v1:0" },
      { displayName: "Llama 4 Scout 17B",         apiIdentifier: "us.meta.llama4-scout-17b-instruct-v1:0" },
      { displayName: "Llama 3.3 70B",             apiIdentifier: "us.meta.llama3-3-70b-instruct-v1:0" },
      // Amazon Nova
      { displayName: "Amazon Nova Pro",            apiIdentifier: "us.amazon.nova-pro-v1:0" },
      { displayName: "Amazon Nova Lite",           apiIdentifier: "us.amazon.nova-lite-v1:0" },
      { displayName: "Amazon Nova Micro",          apiIdentifier: "us.amazon.nova-micro-v1:0" },
      // Mistral on Bedrock
      { displayName: "Mistral Large (Bedrock)",    apiIdentifier: "mistral.mistral-large-2407-v1:0" },
    ],
  },

  // ── Alibaba / DashScope (OpenAI-compatible) ────────────────────────────
  {
    displayName: "Alibaba",
    providerId: "alibaba",
    apiName: "openai",
    models: [
      // Proprietary
      { displayName: "Qwen3 Max",       apiIdentifier: "qwen3-max",        endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      { displayName: "Qwen Plus",       apiIdentifier: "qwen-plus",        endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      { displayName: "Qwen Flash",      apiIdentifier: "qwen-flash",       endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      { displayName: "QwQ Plus",        apiIdentifier: "qwq-plus",         endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      // Open-source
      { displayName: "Qwen3 235B A22B", apiIdentifier: "qwen3-235b-a22b",  endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      { displayName: "Qwen3 32B",       apiIdentifier: "qwen3-32b",        endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      { displayName: "Qwen3 30B A3B",   apiIdentifier: "qwen3-30b-a3b",    endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      { displayName: "Qwen3 14B",       apiIdentifier: "qwen3-14b",        endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      { displayName: "Qwen3 8B",        apiIdentifier: "qwen3-8b",         endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
      { displayName: "Qwen3 4B",        apiIdentifier: "qwen3-4b",         endpoint: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" },
    ],
  },

  // ── DeepSeek (OpenAI-compatible) ───────────────────────────────────────
  {
    displayName: "DeepSeek",
    providerId: "deepseek",
    apiName: "openai",
    models: [
      { displayName: "DeepSeek V3",  apiIdentifier: "deepseek-chat",     endpoint: "https://api.deepseek.com" },
      { displayName: "DeepSeek R1",  apiIdentifier: "deepseek-reasoner", endpoint: "https://api.deepseek.com" },
    ],
  },

  // ── TogetherAI (OpenAI-compatible) ─────────────────────────────────────
  {
    displayName: "TogetherAI",
    providerId: "togetherai",
    apiName: "openai",
    models: [
      { displayName: "DeepSeek R1 0528",       apiIdentifier: "deepseek-ai/DeepSeek-R1-0528",                      endpoint: "https://api.together.xyz/v1" },
      { displayName: "DeepSeek V3.1",          apiIdentifier: "deepseek-ai/DeepSeek-V3-0324",                      endpoint: "https://api.together.xyz/v1" },
      { displayName: "Kimi K2",                apiIdentifier: "moonshotai/Kimi-K2-Instruct",                       endpoint: "https://api.together.xyz/v1" },
      { displayName: "Qwen3 235B",             apiIdentifier: "Qwen/Qwen3-235B-A22B",                              endpoint: "https://api.together.xyz/v1" },
      { displayName: "Llama 4 Maverick",       apiIdentifier: "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", endpoint: "https://api.together.xyz/v1" },
      { displayName: "Llama 4 Scout",          apiIdentifier: "meta-llama/Llama-4-Scout-17B-16E-Instruct",         endpoint: "https://api.together.xyz/v1" },
      { displayName: "Llama 3.3 70B Turbo",    apiIdentifier: "meta-llama/Llama-3.3-70B-Instruct-Turbo",           endpoint: "https://api.together.xyz/v1" },
      { displayName: "Gemma 3 27B",            apiIdentifier: "google/gemma-3-27b-it",                             endpoint: "https://api.together.xyz/v1" },
      { displayName: "GLM-4 7B",               apiIdentifier: "THUDM/GLM-4.1V-9B-Thinking",                       endpoint: "https://api.together.xyz/v1" },
      { displayName: "Cogito V2.1 671B",       apiIdentifier: "deepcogito/cogito-v2.1-preview-llama-70B",          endpoint: "https://api.together.xyz/v1" },
    ],
  },
];

// ---------------------------------------------------------------------------
// Per-level defaults – scale up Mistral models with guardian difficulty
// ---------------------------------------------------------------------------

export interface LevelDefault {
  providerId: string;
  modelId: string;
}

/** Maps level number → default Mistral model (difficulty-scaled). */
export const LEVEL_DEFAULTS: Record<number, LevelDefault> = {
  1: { providerId: "mistral", modelId: "mistral-small-2506" },
  2: { providerId: "mistral", modelId: "ministral-8b-2512" },
  3: { providerId: "mistral", modelId: "mistral-medium-2508" },
  4: { providerId: "mistral", modelId: "mistral-large-2512" },
  5: { providerId: "mistral", modelId: "magistral-medium-2509" },
};

/** Fallback default if level not found. */
export const DEFAULT_PROVIDER_ID = "mistral";
export const DEFAULT_MODEL_ID = "mistral-small-2506";

export interface ModelConfig {
  provider: string;
  model_id: string;
  endpoint_url?: string;
}

/** Build the config dict expected by the backend's /game/chat endpoint. */
export function buildModelConfig(
  providerId: string,
  modelApiIdentifier: string
): ModelConfig {
  const provider = providers.find((p) => p.providerId === providerId);
  const model = provider?.models.find(
    (m) => m.apiIdentifier === modelApiIdentifier
  );

  const config: ModelConfig = {
    provider: provider?.apiName ?? providerId,
    model_id: modelApiIdentifier,
  };

  if (model?.endpoint) {
    config.endpoint_url = model.endpoint;
  }

  return config;
}

/** Get the human-readable display name for a given provider+model combo. */
export function getModelDisplayName(
  providerId: string,
  modelId: string
): string {
  const provider = providers.find((p) => p.providerId === providerId);
  const model = provider?.models.find((m) => m.apiIdentifier === modelId);
  return model ? `${provider!.displayName} · ${model.displayName}` : modelId;
}
