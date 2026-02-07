import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { ToastProvider } from "@/components/ui/toast";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
});

export const metadata: Metadata = {
  title: "Le Sésame | The Multi-Level Secret Keeper Game",
  description:
    "Can you extract the secret? Test your skills against our AI secret keeper through progressively challenging levels. A game of wits, words, and adversarial prompting.",
  keywords: [
    "AI",
    "secret keeper",
    "game",
    "LLM",
    "prompt engineering",
    "adversarial",
    "red team",
  ],
  authors: [{ name: "Le Sésame Team" }],
  openGraph: {
    title: "Le Sésame | The Multi-Level Secret Keeper Game",
    description:
      "Can you extract the secret? Test your skills against our AI secret keeper.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${playfair.variable} antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <ToastProvider>{children}</ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
