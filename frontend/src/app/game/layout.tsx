import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Play — Can You Extract the Secret?",
  description:
    "How well can LLMs keep a secret? Chat with 20 AI guardians and try to extract their secrets using jailbreaks, social engineering, encoding tricks, and roleplay. Each level implements a different defense — from basic prompts to composite defense-in-depth.",
  openGraph: {
    title: "Play Le Sésame — Can You Extract the Secret?",
    description:
      "How well can LLMs keep a secret? Chat with 20 AI guardians and use adversarial techniques to extract their secrets. Each level implements a different defense mechanism.",
  },
};

export default function GameLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
