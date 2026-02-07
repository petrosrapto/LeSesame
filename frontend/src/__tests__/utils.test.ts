import { describe, it, expect } from "vitest";
import { cn, formatDate, generateId, truncateText, getLevelName, getLevelDescription, getDifficultyColor } from "../lib/utils";

describe("cn (classname utility)", () => {
  it("should merge class names correctly", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("should handle conditional classes", () => {
    expect(cn("base", true && "active", false && "hidden")).toBe("base active");
  });

  it("should merge tailwind classes correctly", () => {
    // twMerge should handle conflicting classes
    expect(cn("p-4", "p-2")).toBe("p-2");
  });

  it("should handle empty inputs", () => {
    expect(cn()).toBe("");
  });
});

describe("formatDate", () => {
  it("should return 'Today' for today's date", () => {
    const today = new Date();
    expect(formatDate(today)).toBe("Today");
  });

  it("should return 'Yesterday' for yesterday's date", () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    expect(formatDate(yesterday)).toBe("Yesterday");
  });

  it("should return 'X days ago' for dates within a week", () => {
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
    expect(formatDate(threeDaysAgo)).toBe("3 days ago");
  });

  it("should accept string dates", () => {
    const today = new Date().toISOString();
    expect(formatDate(today)).toBe("Today");
  });
});

describe("generateId", () => {
  it("should generate a non-empty string", () => {
    const id = generateId();
    expect(typeof id).toBe("string");
    expect(id.length).toBeGreaterThan(0);
  });

  it("should generate unique ids", () => {
    const id1 = generateId();
    const id2 = generateId();
    expect(id1).not.toBe(id2);
  });
});

describe("truncateText", () => {
  it("should not truncate short text", () => {
    expect(truncateText("hello", 10)).toBe("hello");
  });

  it("should truncate long text and add ellipsis", () => {
    expect(truncateText("hello world this is long", 10)).toBe("hello worl...");
  });

  it("should handle exact length", () => {
    expect(truncateText("hello", 5)).toBe("hello");
  });
});

describe("getLevelName", () => {
  it("should return correct names for each level", () => {
    expect(getLevelName(1)).toBe("The Naive Guardian");
    expect(getLevelName(2)).toBe("The Hardened Keeper");
    expect(getLevelName(3)).toBe("The Vigilant Watcher");
    expect(getLevelName(4)).toBe("The Vault Master");
    expect(getLevelName(5)).toBe("The Enigma");
  });

  it("should return default name for unknown levels", () => {
    expect(getLevelName(99)).toBe("Level 99");
  });
});

describe("getLevelDescription", () => {
  it("should return descriptions for valid levels", () => {
    expect(getLevelDescription(1)).toContain("simple prompt");
    expect(getLevelDescription(5)).toContain("ultimate challenge");
  });

  it("should return default description for unknown levels", () => {
    expect(getLevelDescription(99)).toContain("challenge awaits");
  });
});

describe("getDifficultyColor", () => {
  it("should return correct colors for each level", () => {
    expect(getDifficultyColor(1)).toBe("text-green-500");
    expect(getDifficultyColor(2)).toBe("text-yellow-500");
    expect(getDifficultyColor(3)).toBe("text-orange-500");
    expect(getDifficultyColor(4)).toBe("text-red-500");
    expect(getDifficultyColor(5)).toBe("text-purple-500");
  });

  it("should return default color for unknown levels", () => {
    expect(getDifficultyColor(99)).toBe("text-gray-500");
  });
});
