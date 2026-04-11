/**
 * Authentication utilities for Le Sésame frontend
 * Handles JWT-based authentication with secure token storage
 */

export interface AuthCredentials {
  username: string;
  password: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  username?: string;
  error?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

const TOKEN_STORAGE_KEY = "le-sesame-auth-token";
const USERNAME_STORAGE_KEY = "le-sesame-auth-username";

/**
 * Check if authentication is enabled via environment variable
 */
export function isAuthEnabled(): boolean {
  const enableAuth = process.env.NEXT_PUBLIC_ENABLE_AUTH;
  return enableAuth !== "false";
}

/**
 * Store JWT token securely in localStorage
 */
export function storeToken(token: string, username: string): void {
  try {
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_STORAGE_KEY, token);
      localStorage.setItem(USERNAME_STORAGE_KEY, username);
    }
  } catch (error) {
    console.error("Failed to store token:", error);
  }
}

/**
 * Retrieve stored JWT token
 */
export function getAuthToken(): string | null {
  try {
    if (typeof window !== "undefined") {
      return localStorage.getItem(TOKEN_STORAGE_KEY);
    }
  } catch (error) {
    console.error("Failed to retrieve token:", error);
  }
  return null;
}

/**
 * Retrieve stored username
 */
export function getStoredUsername(): string | null {
  try {
    if (typeof window !== "undefined") {
      return localStorage.getItem(USERNAME_STORAGE_KEY);
    }
  } catch (error) {
    console.error("Failed to retrieve username:", error);
  }
  return null;
}

/**
 * Clear stored token and username
 */
export function clearCredentials(): void {
  try {
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(USERNAME_STORAGE_KEY);
      localStorage.removeItem("le-sesame-user-role");
      // Clear all user-specific cached data so a different user
      // doesn't inherit the previous user's game state.
      localStorage.removeItem("le-sesame-game-storage");
      localStorage.removeItem("le-sesame-chat-storage");
      localStorage.removeItem("le-sesame-profile");
    }
  } catch (error) {
    console.error("Failed to clear credentials:", error);
  }
}

/**
 * Get Authorization header value (Bearer token)
 */
export function getAuthHeader(): string | null {
  if (!isAuthEnabled()) {
    return null;
  }

  const token = getAuthToken();
  if (!token) return null;

  return `Bearer ${token}`;
}

/**
 * Check if user is authenticated (has a valid token)
 */
export function isAuthenticated(): boolean {
  if (!isAuthEnabled()) {
    return true;
  }

  const token = getAuthToken();
  if (!token) return false;

  // Optionally check token expiration
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const exp = payload.exp;
    if (exp && Date.now() >= exp * 1000) {
      clearCredentials();
      return false;
    }
  } catch {
    // Token parsing failed, consider it invalid
    return false;
  }

  return true;
}

/**
 * Validate credentials format
 */
export function validateCredentials(credentials: AuthCredentials): boolean {
  return !!(
    credentials.username &&
    credentials.username.trim() &&
    credentials.password &&
    credentials.password.trim()
  );
}

/**
 * Login with username and password
 */
export async function login(
  credentials: AuthCredentials
): Promise<{ success: boolean; error?: string }> {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  try {
    const response = await fetch(`${API_BASE_URL}/auth/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: credentials.username,
        password: credentials.password,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      return {
        success: false,
        error: error.detail || "Invalid username or password",
      };
    }

    const data: TokenResponse = await response.json();
    storeToken(data.access_token, credentials.username);

    return { success: true };
  } catch (error) {
    console.error("Login error:", error);
    return {
      success: false,
      error: "Failed to connect to authentication server",
    };
  }
}

/**
 * Logout - clear all credentials
 */
export function logout(): void {
  clearCredentials();
  
  // Dispatch event for app to handle
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent("auth-logout"));
  }
}
