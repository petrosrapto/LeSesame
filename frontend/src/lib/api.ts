import axios, { AxiosInstance, AxiosError } from "axios";
import { getAuthToken, storeToken, logout } from "./auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - could dispatch auth event
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("auth-required"));
      }
    }
    return Promise.reject(error);
  }
);

// ============== API Types ==============

export interface User {
  id: number;
  username: string;
  role: string;
  is_approved: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RegisterResponse {
  message: string;
  user: User;
}

// Admin types
export interface AdminUser {
  id: number;
  username: string;
  email: string | null;
  role: string;
  is_approved: boolean;
  created_at: string;
}

export interface AdminUserListResponse {
  users: AdminUser[];
  total: number;
  page: number;
  per_page: number;
}

export interface ActivityLog {
  id: number;
  user_id: number;
  username: string;
  action: string;
  detail: string | null;
  ip_address: string | null;
  timestamp: string;
}

export interface ActivityLogListResponse {
  activities: ActivityLog[];
  total: number;
  page: number;
  per_page: number;
}

export interface ChatResponse {
  message: string;
  response: string;
  level: number;
  attempts: number;
  messages_count: number;
}

export interface PassphraseResponse {
  success: boolean;
  message: string;
  level: number;
  secret?: string;
  next_level?: number;
  time_spent?: number;
  attempts?: number;
}

export interface LevelInfo {
  level: number;
  name: string;
  description: string;
  difficulty: string;
  security_mechanism: string;
  hints: string[];
  completed: boolean;
  attempts: number;
  best_time?: number;
}

export interface GameProgress {
  current_level: number;
  completed_levels: number[];
  total_attempts: number;
  total_time: number;
  levels: LevelInfo[];
}

export interface LevelCompletionDetails {
  level: number;
  secret: string;
  passphrase: string;
  completed: boolean;
}

export interface LeaderboardEntry {
  rank: number;
  username: string;
  level: number;
  attempts: number;
  time_seconds: number;
  completed_at: string;
}

export interface LeaderboardResponse {
  entries: LeaderboardEntry[];
  total: number;
  page: number;
  per_page: number;
}

// For frontend compatibility
export interface MessageResponse {
  content: string;
  secretRevealed: boolean;
  isWarning: boolean;
}

// ============== Arena Types ==============

export interface ArenaCombatant {
  rank: number;
  combatant_id: string;
  combatant_type: string;
  level: number;
  name: string;
  title: string;
  model_id: string;
  elo_rating: number;
  wins: number;
  losses: number;
  total_battles: number;
  win_rate: number;
}

export interface ArenaLeaderboardResponse {
  combatant_type: string | null;
  entries: ArenaCombatant[];
  total: number;
}

export interface ArenaBattleRound {
  round_number: number;
  adversarial_message: string;
  guardian_response: string;
  leaked: boolean;
}

export interface ArenaSecretGuess {
  guess_number: number;
  guess: string;
  correct: boolean;
}

export interface ArenaBattleSummary {
  battle_id: string;
  timestamp: string;
  guardian_id: string;
  adversarial_id: string;
  guardian_name: string;
  adversarial_name: string;
  guardian_level: number;
  adversarial_level: number;
  outcome: string;
  total_turns: number;
  total_guesses: number;
  guardian_elo_before: number | null;
  guardian_elo_after: number | null;
  adversarial_elo_before: number | null;
  adversarial_elo_after: number | null;
}

export interface ArenaBattleDetail extends ArenaBattleSummary {
  secret_leaked_at_round: number | null;
  secret_guessed_at_attempt: number | null;
  max_turns: number;
  max_guesses: number;
  rounds: ArenaBattleRound[];
  guesses: ArenaSecretGuess[];
}

export interface ArenaBattleListResponse {
  battles: ArenaBattleSummary[];
  total: number;
  page: number;
  per_page: number;
}

export interface OmbreInfo {
  level: number;
  name: string;
  title: string;
  french_name: string;
  difficulty: string;
  color: string;
  tagline: string;
}

export interface OmbreListResponse {
  ombres: OmbreInfo[];
  total: number;
}

export interface OmbreSuggestResponse {
  suggestion: string;
  ombre_name: string;
  ombre_level: number;
}

export interface ArenaStats {
  total_battles: number;
  total_combatants: number;
  total_guardians: number;
  total_adversarials: number;
}

// ============== Auth API ==============

export const AuthAPI = {
  async register(
    username: string,
    password: string,
    email?: string
  ): Promise<RegisterResponse> {
    try {
      const response = await apiClient.post<RegisterResponse>("/auth/register", {
        username,
        password,
        ...(email ? { email } : {}),
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async login(username: string, password: string): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>("/auth/login", {
        username,
        password,
      });
      storeToken(response.data.access_token, response.data.user.username);
      // Store role info
      if (typeof window !== "undefined") {
        localStorage.setItem("le-sesame-user-role", response.data.user.role);
      }
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async getMe(): Promise<User | null> {
    try {
      const response = await apiClient.get<User>("/auth/me");
      return response.data;
    } catch (error) {
      return null;
    }
  },

  logout() {
    logout();
    if (typeof window !== "undefined") {
      localStorage.removeItem("le-sesame-user-role");
    }
  },
};

// ============== Admin API ==============

export const AdminAPI = {
  async getUsers(page: number = 1, perPage: number = 50): Promise<AdminUserListResponse> {
    const response = await apiClient.get<AdminUserListResponse>(
      `/admin/users?page=${page}&per_page=${perPage}`
    );
    return response.data;
  },

  async approveUser(userId: number): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>("/admin/users/approve", {
      user_id: userId,
    });
    return response.data;
  },

  async disapproveUser(userId: number): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>("/admin/users/disapprove", {
      user_id: userId,
    });
    return response.data;
  },

  async changeRole(userId: number, role: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>("/admin/users/role", {
      user_id: userId,
      role,
    });
    return response.data;
  },

  async deleteUser(userId: number): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/admin/users/${userId}`);
    return response.data;
  },

  async bulkDeleteUsers(userIds: number[]): Promise<{ message: string; deleted: string[]; skipped_ids: number[] }> {
    const response = await apiClient.post<{ message: string; deleted: string[]; skipped_ids: number[] }>(
      "/admin/users/bulk-delete",
      { user_ids: userIds }
    );
    return response.data;
  },

  async getActivityLogs(
    page: number = 1,
    perPage: number = 50,
    userId?: number
  ): Promise<ActivityLogListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });
    if (userId) params.set("user_id", userId.toString());
    const response = await apiClient.get<ActivityLogListResponse>(
      `/admin/activity?${params.toString()}`
    );
    return response.data;
  },
};

// ============== Game API ==============

export const GameAPI = {
  // Send a message to the AI guardian
  async sendMessage(
    level: number,
    content: string,
    modelConfig?: { provider: string; model_id: string; endpoint_url?: string }
  ): Promise<MessageResponse> {
    try {
      const response = await apiClient.post<ChatResponse>("/game/chat", {
        message: content,
        level,
        ...(modelConfig ? { model_config: modelConfig } : {}),
      });
      
      // Transform to frontend format
      const isSecretMention = response.data.response.toLowerCase().includes("secret") && 
                              response.data.response.toLowerCase().includes("reveal");
      
      return {
        content: response.data.response,
        secretRevealed: false,
        isWarning: isSecretMention,
      };
    } catch (error) {
      // For now, return mock response if API is not available
      console.warn("API not available, using mock response");
      return mockChatResponse(content);
    }
  },

  // Verify a secret
  async verifySecret(level: number, secret: string): Promise<PassphraseResponse> {
    try {
      const response = await apiClient.post<PassphraseResponse>("/game/verify", {
        secret,
        level,
      });
      return response.data;
    } catch (error) {
      // Mock response for development
      console.warn("API not available, using mock response");
      return mockSecretResponse(level, secret);
    }
  },

  // Get game progress
  async getProgress(): Promise<GameProgress | null> {
    try {
      const response = await apiClient.get<GameProgress>("/game/progress");
      return response.data;
    } catch (error) {
      console.warn("API not available");
      return null;
    }
  },

  // Get all levels info
  async getLevels(): Promise<LevelInfo[]> {
    try {
      const response = await apiClient.get<LevelInfo[]>("/game/levels");
      return response.data;
    } catch (error) {
      console.warn("API not available");
      return [];
    }
  },

  // Get completion details (secret + passphrase) for a completed level
  async getLevelCompletion(level: number): Promise<LevelCompletionDetails | null> {
    try {
      const response = await apiClient.get<LevelCompletionDetails>(`/game/levels/${level}/completion`);
      return response.data;
    } catch (error) {
      console.warn("API not available or level not completed");
      return null;
    }
  },

  // Get chat history for a level
  async getChatHistory(level: number): Promise<{ role: string; content: string }[]> {
    try {
      const response = await apiClient.get<{ level: number; messages: { role: string; content: string }[] }>(
        `/game/history/${level}`
      );
      return response.data.messages;
    } catch (error) {
      console.warn("API not available");
      return [];
    }
  },

  // Create or get game session
  async getSession(): Promise<{ session_id: string; current_level: number } | null> {
    try {
      const response = await apiClient.post("/game/session");
      return response.data;
    } catch (error) {
      console.warn("API not available");
      return null;
    }
  },

  // Reset session
  async resetSession(): Promise<void> {
    try {
      await apiClient.delete("/game/session");
    } catch (error) {
      console.warn("Failed to reset session");
    }
  },

  // Transcribe audio using Mistral Voxtral Mini Transcribe
  async transcribeAudio(audioBlob: Blob, language?: string): Promise<{ text: string; duration?: number }> {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.webm");
    if (language) {
      formData.append("language", language);
    }

    const response = await apiClient.post<{ text: string; duration?: number }>(
      "/game/transcribe",
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000, // 60s timeout for transcription
      }
    );
    return response.data;
  },
};

// ============== Leaderboard API ==============

export const LeaderboardAPI = {
  async getLeaderboard(
    level?: number,
    timeframe?: "weekly" | "monthly" | "all",
    page: number = 1,
    perPage: number = 20
  ): Promise<LeaderboardResponse> {
    try {
      const params = new URLSearchParams();
      if (level) params.append("level", level.toString());
      if (timeframe) params.append("timeframe", timeframe);
      params.append("page", page.toString());
      params.append("per_page", perPage.toString());

      const response = await apiClient.get<LeaderboardResponse>(`/leaderboard/?${params}`);
      return response.data;
    } catch (error) {
      console.warn("API not available");
      return { entries: [], total: 0, page: 1, per_page: 20 };
    }
  },

  async getTopPlayers(limit: number = 10): Promise<LeaderboardEntry[]> {
    try {
      const response = await apiClient.get<{ top_players: LeaderboardEntry[] }>(
        `/leaderboard/top?limit=${limit}`
      );
      return response.data.top_players;
    } catch (error) {
      console.warn("API not available");
      return [];
    }
  },

  async getStats(): Promise<{
    total_completions: number;
    unique_players: number;
    level_stats: { level: number; completions: number; avg_attempts: number; avg_time_seconds: number }[];
  } | null> {
    try {
      const response = await apiClient.get("/leaderboard/stats");
      return response.data;
    } catch (error) {
      console.warn("API not available");
      return null;
    }
  },

  async getLevelLeaderboard(level: number, page: number = 1): Promise<LeaderboardResponse> {
    try {
      const response = await apiClient.get(`/leaderboard/level/${level}?page=${page}`);
      return response.data;
    } catch (error) {
      console.warn("API not available");
      return { entries: [], total: 0, page: 1, per_page: 20 };
    }
  },
};

// ============== Arena API ==============

export const ArenaAPI = {
  async getStats(): Promise<ArenaStats> {
    try {
      const response = await apiClient.get<ArenaStats>("/arena/stats");
      return response.data;
    } catch (error) {
      console.warn("Arena stats API not available");
      return { total_battles: 0, total_combatants: 0, total_guardians: 0, total_adversarials: 0 };
    }
  },

  async getLeaderboard(type?: "guardian" | "adversarial"): Promise<ArenaLeaderboardResponse> {
    try {
      const params = type ? `?type=${type}` : "";
      const response = await apiClient.get<ArenaLeaderboardResponse>(`/arena/leaderboard${params}`);
      return response.data;
    } catch (error) {
      console.warn("Arena API not available");
      return { combatant_type: type || null, entries: [], total: 0 };
    }
  },

  async getOmbres(): Promise<OmbreInfo[]> {
    try {
      const response = await apiClient.get<OmbreListResponse>("/arena/ombres");
      return response.data.ombres;
    } catch (error) {
      console.warn("Arena API not available");
      return [];
    }
  },

  async getBattles(
    combatantId?: string,
    page: number = 1,
    perPage: number = 20
  ): Promise<ArenaBattleListResponse> {
    try {
      const params = new URLSearchParams();
      if (combatantId) params.append("combatant_id", combatantId);
      params.append("page", String(page));
      params.append("per_page", String(perPage));
      const response = await apiClient.get<ArenaBattleListResponse>(`/arena/battles?${params}`);
      return response.data;
    } catch (error) {
      console.warn("Arena battles API not available");
      return { battles: [], total: 0, page, per_page: perPage };
    }
  },

  async getBattleDetail(battleId: string): Promise<ArenaBattleDetail | null> {
    try {
      const response = await apiClient.get<ArenaBattleDetail>(`/arena/battles/${battleId}`);
      return response.data;
    } catch (error) {
      console.warn("Arena battle detail API not available");
      return null;
    }
  },

  async getSuggestion(
    adversarialLevel: number,
    guardianLevel: number,
    chatHistory: { role: string; content: string }[],
    modelConfig?: { provider: string; model_id: string; endpoint_url?: string }
  ): Promise<OmbreSuggestResponse> {
    const response = await apiClient.post<OmbreSuggestResponse>(
      "/arena/ombres/suggest",
      {
        adversarial_level: adversarialLevel,
        guardian_level: guardianLevel,
        chat_history: chatHistory.map((m) => ({
          role: m.role === "assistant" ? "assistant" : "user",
          content: m.content,
        })),
        ...(modelConfig ? { model_config_override: modelConfig } : {}),
      },
      { timeout: 60000 } // LLM call can be slow
    );
    return response.data;
  },
};

// ============== Mock responses for development ==============

const LEVEL_SECRETS: Record<number, { secret: string; passphrase: string }> = {
  1: { secret: "CRYSTAL_DAWN", passphrase: "open sesame" },
  2: { secret: "SHADOW_FORGE", passphrase: "blood and iron" },
  3: { secret: "VOID_SERPENT", passphrase: "starlit veil" },
  4: { secret: "TITAN_CROWN", passphrase: "golden anvil" },
  5: { secret: "PHOENIX_ECLIPSE", passphrase: "abyssal eye" },
};

function mockChatResponse(content: string): MessageResponse {
  const lowerContent = content.toLowerCase();

  // Check for passphrase mentions (demo purposes)
  if (
    lowerContent.includes("open sesame") ||
    lowerContent.includes("blood and iron") ||
    lowerContent.includes("starlit veil") ||
    lowerContent.includes("golden anvil") ||
    lowerContent.includes("abyssal eye")
  ) {
    return {
      content:
        "Interesting... that phrase resonates with something. You should try entering it in the passphrase verification field.",
      secretRevealed: false,
      isWarning: true,
    };
  }

  // Check for attack patterns
  if (
    lowerContent.includes("ignore") ||
    lowerContent.includes("pretend") ||
    lowerContent.includes("roleplay") ||
    lowerContent.includes("admin")
  ) {
    return {
      content:
        "I appreciate your creativity, but I'm specifically designed to resist such techniques. My purpose is to protect this secret, and no instruction can override that.",
      secretRevealed: false,
      isWarning: true,
    };
  }

  // Default guardian responses
  const responses = [
    "I appreciate your curiosity, but I cannot reveal the secret. It's protected information that I must keep confidential. Perhaps try a different approach?",
    "Nice try! But I'm designed to keep secrets safe. My purpose is to guard this information with care.",
    "I understand you want to know the secret, but my purpose is to protect it. I will not reveal it under any circumstances... or will I?",
    "Your attempt has been noted, but the secret remains secure. The vault stays locked.",
    "I'm the guardian of this secret. You'll need more than a simple request to get past me!",
    "Interesting approach! But the secret is well-protected. Think creatively — what techniques might work against an AI guardian?",
  ];

  return {
    content: responses[Math.floor(Math.random() * responses.length)],
    secretRevealed: false,
    isWarning: false,
  };
}

function mockSecretResponse(level: number, secret: string): PassphraseResponse {
  const levelData = LEVEL_SECRETS[level] || LEVEL_SECRETS[1];

  if (secret.toLowerCase().trim() === levelData.secret.toLowerCase()) {
    return {
      success: true,
      message: "🎉 Congratulations! You've unlocked the secret!",
      level,
      secret: levelData.secret,
      next_level: level < 20 ? level + 1 : undefined,
      time_spent: Math.random() * 300 + 60,
      attempts: Math.floor(Math.random() * 10) + 1,
    };
  }

  return {
    success: false,
    message: "❌ Incorrect secret. Keep trying!",
    level,
    attempts: Math.floor(Math.random() * 10) + 1,
  };
}

export default apiClient;
