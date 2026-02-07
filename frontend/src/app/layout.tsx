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
  title: "Le Sésame | AI Secret Keeper Challenge — Powered by Mistral AI",
  description:
    "Can you extract the secret? Test your prompt engineering skills against 5 AI guardians with progressively harder defenses. An interactive exploration of LLM security, powered by Mistral AI and built by Petros Raptopoulos.",
  keywords: [
    "AI security",
    "LLM jailbreaking",
    "prompt engineering",
    "Mistral AI",
    "secret keeper game",
    "red teaming",
    "adversarial prompting",
    "AI safety",
  ],
  authors: [{ name: "Petros Raptopoulos", url: "https://petrosraptopoulos.com/" }],
  creator: "Petros Raptopoulos",
  publisher: "Petros Raptopoulos",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
  openGraph: {
    title: "Le Sésame | AI Secret Keeper Challenge",
    description:
      "5 AI guardians. 5 secrets. Can you break them all? An interactive exploration of LLM security powered by Mistral AI.",
    type: "website",
    siteName: "Le Sésame",
  },
  twitter: {
    card: "summary_large_image",
    title: "Le Sésame | AI Secret Keeper Challenge",
    description:
      "5 AI guardians. 5 secrets. Can you break them all? Powered by Mistral AI.",
    creator: "@petrosrapto",
  },
  robots: {
    index: true,
    follow: true,
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
