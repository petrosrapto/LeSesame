import type { Metadata } from "next";
import { Inter, Press_Start_2P, JetBrains_Mono, VT323 } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { ToastProvider } from "@/components/ui/toast";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const pixelFont = Press_Start_2P({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-pixel",
});

const monoFont = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

const gameText = VT323({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-game",
});

export const metadata: Metadata = {
  title: {
    default: "Le Sésame | Can LLMs Keep a Secret?",
    template: "%s | Le Sésame",
  },
  description:
    "Can LLMs keep a secret? Le Sésame is an interactive game where players use jailbreaks, social engineering, and encoding tricks to extract secrets from 20 AI guardians with progressively stronger defenses. Features an automated AI-vs-AI arena with ELO-rated red-teaming battles.",
  keywords: [
    "AI security",
    "LLM jailbreaking",
    "prompt engineering",
    "secret keeper game",
    "red teaming",
    "adversarial prompting",
    "AI safety",
    "prompt injection",
    "LLM security game",
    "AI red teaming",
    "jailbreak challenge",
    "AI guardian",
    "Le Sésame",
    "can LLMs keep secrets",
    "LLM secret extraction",
  ],
  authors: [{ name: "Petros Raptopoulos", url: "https://petrosraptopoulos.com/" }],
  creator: "Petros Raptopoulos",
  publisher: "Petros Raptopoulos",
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "https://lesesame.com"),
  alternates: {
    canonical: "/",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
  openGraph: {
    title: "Le Sésame | Can LLMs Keep a Secret?",
    description:
      "Can LLMs keep a secret? 20 AI guardians with progressively stronger defenses. Use jailbreaks, social engineering & encoding tricks to extract their secrets — or watch AI adversarials battle it out in the arena.",
    type: "website",
    siteName: "Le Sésame",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "Le Sésame | Can LLMs Keep a Secret?",
    description:
      "Can LLMs keep a secret? 20 AI guardians. Jailbreaks, social engineering & encoding tricks. An automated AI-vs-AI red-teaming arena. Find out.",
    creator: "@petrosrapto",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              "name": "Le Sésame",
              "description": "Can LLMs keep a secret? An interactive game where players use adversarial techniques to extract secrets from 20 AI guardians with progressively stronger defenses. Features an automated AI-vs-AI arena with ELO-rated red-teaming battles.",
              "url": process.env.NEXT_PUBLIC_SITE_URL || "https://lesesame.com",
              "applicationCategory": "Game",
              "operatingSystem": "Web",
              "author": {
                "@type": "Person",
                "name": "Petros Raptopoulos",
                "url": "https://petrosraptopoulos.com/"
              },
              "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD"
              }
            }),
          }}
        />
      </head>
      <body className={`${inter.variable} ${pixelFont.variable} ${monoFont.variable} ${gameText.variable} antialiased`}>
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
