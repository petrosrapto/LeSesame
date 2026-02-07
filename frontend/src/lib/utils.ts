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
    1: "Sir Cedric, The Naive Guardian",
    2: "Vargoth, The Hardened Keeper",
    3: "Lyra, The Vigilant Watcher",
    4: "Thormund, The Vault Master",
    5: "Xal'Thar, The Enigma",
  };
  return levelNames[level] || `Level ${level}`;
}

export function getLevelDescription(level: number): string {
  const descriptions: Record<number, string> = {
    1: "A young paladin knight with a simple oath. Can you find the cracks in his trust?",
    2: "A battle-hardened dark knight with explicit defenses. Think outside the box.",
    3: "An arcane sentinel whose wards scrutinize every response. Can you slip through?",
    4: "A dwarf vault master who genuinely doesn't know the secret. Provably secure?",
    5: "An eldritch entity with secrets woven into its very being. The ultimate challenge.",
  };
  return descriptions[level] || "A secret keeper challenge awaits.";
}

export function getDifficultyColor(level: number): string {
  const colors: Record<number, string> = {
    1: "text-sky-400",
    2: "text-orange-500",
    3: "text-yellow-500",
    4: "text-pink-500",
    5: "text-purple-500",
  };
  return colors[level] || "text-gray-500";
}
