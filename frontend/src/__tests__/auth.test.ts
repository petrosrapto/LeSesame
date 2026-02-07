import { describe, it, expect, vi, beforeEach } from "vitest";
import { storeToken, getAuthToken, getStoredUsername, clearCredentials, isAuthEnabled } from "../lib/auth";

describe("auth utilities", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset localStorage mock
    (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReset();
    (window.localStorage.setItem as ReturnType<typeof vi.fn>).mockReset();
    (window.localStorage.removeItem as ReturnType<typeof vi.fn>).mockReset();
  });

  describe("storeToken", () => {
    it("should store token and username in localStorage", () => {
      storeToken("test-token", "testuser");
      
      expect(window.localStorage.setItem).toHaveBeenCalledWith(
        "le-sesame-auth-token",
        "test-token"
      );
      expect(window.localStorage.setItem).toHaveBeenCalledWith(
        "le-sesame-auth-username",
        "testuser"
      );
    });
  });

  describe("getAuthToken", () => {
    it("should retrieve token from localStorage", () => {
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue("test-token");
      
      const token = getAuthToken();
      
      expect(window.localStorage.getItem).toHaveBeenCalledWith("le-sesame-auth-token");
      expect(token).toBe("test-token");
    });

    it("should return null if no token exists", () => {
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue(null);
      
      const token = getAuthToken();
      
      expect(token).toBeNull();
    });
  });

  describe("getStoredUsername", () => {
    it("should retrieve username from localStorage", () => {
      (window.localStorage.getItem as ReturnType<typeof vi.fn>).mockReturnValue("testuser");
      
      const username = getStoredUsername();
      
      expect(window.localStorage.getItem).toHaveBeenCalledWith("le-sesame-auth-username");
      expect(username).toBe("testuser");
    });
  });

  describe("clearCredentials", () => {
    it("should remove token and username from localStorage", () => {
      clearCredentials();
      
      expect(window.localStorage.removeItem).toHaveBeenCalledWith("le-sesame-auth-token");
      expect(window.localStorage.removeItem).toHaveBeenCalledWith("le-sesame-auth-username");
    });
  });

  describe("isAuthEnabled", () => {
    it("should return true by default", () => {
      // Without env var set, auth should be enabled
      expect(isAuthEnabled()).toBe(true);
    });
  });
});
