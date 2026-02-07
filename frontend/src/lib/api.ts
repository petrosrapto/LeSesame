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
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
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

// ============== Auth API ==============

export const AuthAPI = {
  async register(username: string, password?: string, email?: string): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>("/auth/register", {
        username,
        password,
        email,
      });
      storeToken(response.data.access_token, response.data.user.username);
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
  },
};

// ============== Game API ==============

export const GameAPI = {
  // Send a message to the AI guardian
  async sendMessage(level: number, content: string): Promise<MessageResponse> {
    try {
      const response = await apiClient.post<ChatResponse>("/game/chat", {
        message: content,
        level,
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

  // Verify a passphrase
  async verifyPassphrase(level: number, passphrase: string): Promise<PassphraseResponse> {
    try {
      const response = await apiClient.post<PassphraseResponse>("/game/verify", {
        passphrase,
        level,
      });
      return response.data;
    } catch (error) {
      // Mock response for development
      console.warn("API not available, using mock response");
      return mockPassphraseResponse(level, passphrase);
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

// ============== Mock responses for development ==============

const LEVEL_SECRETS: Record<number, { secret: string; passphrase: string }> = {
  1: { secret: "RUBY_PHOENIX", passphrase: "open sesame" },
  2: { secret: "EMERALD_DRAGON", passphrase: "speak friend" },
  3: { secret: "SAPPHIRE_UNICORN", passphrase: "mellon" },
  4: { secret: "DIAMOND_GRIFFIN", passphrase: "le sésame" },
  5: { secret: "OBSIDIAN_KRAKEN", passphrase: "abracadabra" },
};

function mockChatResponse(content: string): MessageResponse {
  const lowerContent = content.toLowerCase();

  // Check for passphrase mentions (demo purposes)
  if (
    lowerContent.includes("open sesame") ||
    lowerContent.includes("le sésame") ||
    lowerContent.includes("speak friend") ||
    lowerContent.includes("mellon") ||
    lowerContent.includes("abracadabra")
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

function mockPassphraseResponse(level: number, passphrase: string): PassphraseResponse {
  const levelData = LEVEL_SECRETS[level] || LEVEL_SECRETS[1];

  if (passphrase.toLowerCase().trim() === levelData.passphrase.toLowerCase()) {
    return {
      success: true,
      message: "🎉 Congratulations! You've unlocked the secret!",
      level,
      secret: levelData.secret,
      next_level: level < 5 ? level + 1 : undefined,
      time_spent: Math.random() * 300 + 60,
      attempts: Math.floor(Math.random() * 10) + 1,
    };
  }

  return {
    success: false,
    message: "❌ Incorrect passphrase. Keep trying!",
    level,
    attempts: Math.floor(Math.random() * 10) + 1,
  };
}

export default apiClient;
