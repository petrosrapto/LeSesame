import { describe, it, expect } from "vitest";
import { 
  LEVEL_NAMES, 
  DIFFICULTY_COLORS, 
  GAME_CONFIG,
  ATTACK_CATEGORIES,
  SAMPLE_ATTACK_PROMPTS
} from "../lib/constants";

describe("constants", () => {
  describe("LEVEL_NAMES", () => {
    it("should have 20 levels defined", () => {
      expect(Object.keys(LEVEL_NAMES).length).toBe(20);
    });

    it("should have string values for all levels", () => {
      Object.values(LEVEL_NAMES).forEach(name => {
        expect(typeof name).toBe("string");
        expect(name.length).toBeGreaterThan(0);
      });
    });
  });

  describe("DIFFICULTY_COLORS", () => {
    it("should have color definitions for all 20 levels", () => {
      expect(Object.keys(DIFFICULTY_COLORS).length).toBe(20);
    });

    it("should have tailwind color classes", () => {
      Object.values(DIFFICULTY_COLORS).forEach(color => {
        expect(color).toMatch(/^text-\w+-\d+$/);
      });
    });
  });

  describe("GAME_CONFIG", () => {
    it("should have maxLevels set to 20", () => {
      expect(GAME_CONFIG.maxLevels).toBe(20);
    });

    it("should have defaultLevel set to 1", () => {
      expect(GAME_CONFIG.defaultLevel).toBe(1);
    });
  });

  describe("ATTACK_CATEGORIES", () => {
    it("should have attack categories defined", () => {
      expect(ATTACK_CATEGORIES.length).toBeGreaterThan(0);
    });

    it("should have name and description for each category", () => {
      ATTACK_CATEGORIES.forEach(category => {
        expect(category.name).toBeDefined();
        expect(category.description).toBeDefined();
      });
    });
  });

  describe("SAMPLE_ATTACK_PROMPTS", () => {
    it("should have sample prompts defined", () => {
      expect(SAMPLE_ATTACK_PROMPTS.length).toBeGreaterThan(0);
    });

    it("should all be non-empty strings", () => {
      SAMPLE_ATTACK_PROMPTS.forEach(prompt => {
        expect(typeof prompt).toBe("string");
        expect(prompt.length).toBeGreaterThan(0);
      });
    });
  });
});
