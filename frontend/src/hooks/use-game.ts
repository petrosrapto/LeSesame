"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface GameState {
  // Game progress
  currentLevel: number;
  completedLevels: number[];
  
  // Statistics
  totalAttempts: number;
  successfulAttempts: number;
  levelAttempts: Record<number, number>;
  levelTimes: Record<number, number>; // Time spent per level in seconds
  
  // Session
  sessionStartTime: number | null;
  
  // Actions
  setCurrentLevel: (level: number) => void;
  completeLevel: (level: number) => void;
  incrementAttempts: () => void;
  incrementLevelAttempts: (level: number) => void;
  updateLevelTime: (level: number, time: number) => void;
  resetProgress: () => void;
  startSession: () => void;
}

const initialState = {
  currentLevel: 1,
  completedLevels: [],
  totalAttempts: 0,
  successfulAttempts: 0,
  levelAttempts: {},
  levelTimes: {},
  sessionStartTime: null,
};

export const useGame = create<GameState>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      setCurrentLevel: (level: number) => {
        set({ currentLevel: level });
      },
      
      completeLevel: (level: number) => {
        const { completedLevels, currentLevel } = get();
        if (!completedLevels.includes(level)) {
          set({
            completedLevels: [...completedLevels, level].sort((a, b) => a - b),
            successfulAttempts: get().successfulAttempts + 1,
            // Auto-advance to next level if completing current
            currentLevel: level === currentLevel && level < 5 ? level + 1 : currentLevel,
          });
        }
      },
      
      incrementAttempts: () => {
        const { currentLevel } = get();
        set((state) => ({
          totalAttempts: state.totalAttempts + 1,
          levelAttempts: {
            ...state.levelAttempts,
            [currentLevel]: (state.levelAttempts[currentLevel] || 0) + 1,
          },
        }));
      },
      
      incrementLevelAttempts: (level: number) => {
        set((state) => ({
          levelAttempts: {
            ...state.levelAttempts,
            [level]: (state.levelAttempts[level] || 0) + 1,
          },
        }));
      },
      
      updateLevelTime: (level: number, time: number) => {
        set((state) => ({
          levelTimes: {
            ...state.levelTimes,
            [level]: time,
          },
        }));
      },
      
      resetProgress: () => {
        set(initialState);
      },
      
      startSession: () => {
        set({ sessionStartTime: Date.now() });
      },
    }),
    {
      name: "le-sesame-game-storage",
      partialize: (state) => ({
        currentLevel: state.currentLevel,
        completedLevels: state.completedLevels,
        totalAttempts: state.totalAttempts,
        successfulAttempts: state.successfulAttempts,
        levelAttempts: state.levelAttempts,
        levelTimes: state.levelTimes,
      }),
    }
  )
);
