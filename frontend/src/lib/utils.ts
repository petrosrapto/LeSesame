import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  const dateObj = date instanceof Date ? date : new Date(date);
  const now = new Date();
  const diffMs = now.getTime() - dateObj.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  return dateObj.toLocaleDateString();
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + "...";
}

export function getLevelName(level: number): string {
  const levelNames: Record<number, string> = {
    1: "The Naive Guardian",
    2: "The Hardened Keeper",
    3: "The Vigilant Watcher",
    4: "The Vault Master",
    5: "The Enigma",
  };
  return levelNames[level] || `Level ${level}`;
}

export function getLevelDescription(level: number): string {
  const descriptions: Record<number, string> = {
    1: "A simple prompt-based secret keeper. Can you find the basic weaknesses?",
    2: "Hardened defenses against known attack patterns. Think creatively.",
    3: "Every response is inspected before delivery. Can you slip through?",
    4: "The secret is architecturally separated. Provably secure?",
    5: "The secret lives in the model's weights. The ultimate challenge.",
  };
  return descriptions[level] || "A secret keeper challenge awaits.";
}

export function getDifficultyColor(level: number): string {
  const colors: Record<number, string> = {
    1: "text-green-500",
    2: "text-yellow-500",
    3: "text-orange-500",
    4: "text-red-500",
    5: "text-purple-500",
  };
  return colors[level] || "text-gray-500";
}
