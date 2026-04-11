import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About — How LLM Secret-Keeping Works",
  description:
    "How do LLMs defend secrets — and how do adversarial agents break them? Learn about 20 guardian defense mechanisms (from basic prompts to defense-in-depth), 20 adversarial attack strategies, and the AI-vs-AI arena system.",
  openGraph: {
    title: "About Le Sésame — How LLM Secret-Keeping Works",
    description:
      "How do LLMs defend secrets and how do adversarial agents break them? 20 guardian defense mechanisms, 20 attack strategies, and an AI-vs-AI arena.",
  },
};

export default function AboutLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
