import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Arena Leaderboard — AI Guardians vs Adversarials",
  description:
    "Which LLM-based guardians are best at keeping secrets? Which adversarial agents are best at extracting them? ELO-rated AI-vs-AI battle rankings across 20 guardian and 20 adversarial characters powered by different models.",
  openGraph: {
    title: "Le Sésame Arena — AI Guardians vs Adversarial Rankings",
    description:
      "Which LLM guardians keep secrets best? Which adversarial agents break them? ELO-rated AI-vs-AI red-teaming battle rankings.",
  },
};

export default function LeaderboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
