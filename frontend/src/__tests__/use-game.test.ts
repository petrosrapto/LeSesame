import { describe, it, expect, beforeEach } from "vitest";
import { act, renderHook } from "@testing-library/react";
import { useGame } from "../hooks/use-game";

describe("useGame hook", () => {
  beforeEach(() => {
    // Reset the store state
    const { result } = renderHook(() => useGame());
    act(() => {
      result.current.resetProgress();
    });
  });

  describe("initial state", () => {
    it("should have correct initial values", () => {
      const { result } = renderHook(() => useGame());
      
      expect(result.current.currentLevel).toBe(1);
      expect(result.current.completedLevels).toEqual([]);
      expect(result.current.totalAttempts).toBe(0);
      expect(result.current.successfulAttempts).toBe(0);
    });
  });

  describe("setCurrentLevel", () => {
    it("should update current level", () => {
      const { result } = renderHook(() => useGame());
      
      act(() => {
        result.current.setCurrentLevel(3);
      });
      
      expect(result.current.currentLevel).toBe(3);
    });
  });

  describe("completeLevel", () => {
    it("should add level to completed levels", () => {
      const { result } = renderHook(() => useGame());
      
      act(() => {
        result.current.completeLevel(1);
      });
      
      expect(result.current.completedLevels).toContain(1);
    });

    it("should increment successful attempts", () => {
      const { result } = renderHook(() => useGame());
      
      act(() => {
        result.current.completeLevel(1);
      });
      
      expect(result.current.successfulAttempts).toBe(1);
    });

    it("should auto-advance to next level", () => {
      const { result } = renderHook(() => useGame());
      
      act(() => {
        result.current.setCurrentLevel(1);
        result.current.completeLevel(1);
      });
      
      expect(result.current.currentLevel).toBe(2);
    });

    it("should not add duplicate completed levels", () => {
      const { result } = renderHook(() => useGame());
      
      act(() => {
        result.current.completeLevel(1);
        result.current.completeLevel(1);
      });
      
      expect(result.current.completedLevels).toEqual([1]);
      expect(result.current.successfulAttempts).toBe(1);
    });
  });

  describe("incrementAttempts", () => {
    it("should increment total attempts", () => {
      const { result } = renderHook(() => useGame());
      
      act(() => {
        result.current.incrementAttempts();
      });
      
      expect(result.current.totalAttempts).toBe(1);
    });

    it("should increment level attempts for current level", () => {
      const { result } = renderHook(() => useGame());
      
      act(() => {
        result.current.setCurrentLevel(2);
        result.current.incrementAttempts();
      });
      
      expect(result.current.levelAttempts[2]).toBe(1);
    });
  });

  describe("updateLevelTime", () => {
    it("should update time for a level", () => {
      const { result } = renderHook(() => useGame());
      
      act(() => {
        result.current.updateLevelTime(1, 120);
      });
      
      expect(result.current.levelTimes[1]).toBe(120);
    });
  });

  describe("resetProgress", () => {
    it("should reset all state to initial values", () => {
      const { result } = renderHook(() => useGame());
      
      // Make some changes
      act(() => {
        result.current.setCurrentLevel(3);
        result.current.completeLevel(1);
        result.current.incrementAttempts();
      });
      
      // Reset
      act(() => {
        result.current.resetProgress();
      });
      
      expect(result.current.currentLevel).toBe(1);
      expect(result.current.completedLevels).toEqual([]);
      expect(result.current.totalAttempts).toBe(0);
    });
  });

  describe("startSession", () => {
    it("should set session start time", () => {
      const { result } = renderHook(() => useGame());
      
      expect(result.current.sessionStartTime).toBeNull();
      
      act(() => {
        result.current.startSession();
      });
      
      expect(result.current.sessionStartTime).toBeDefined();
      expect(typeof result.current.sessionStartTime).toBe("number");
    });
  });
});
