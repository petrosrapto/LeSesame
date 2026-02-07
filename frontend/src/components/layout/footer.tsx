import Link from "next/link";
import Image from "next/image";
import { Logo } from "@/components/brand/logo";
import { Github, Linkedin, Globe, GraduationCap, Mail } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border bg-card/50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-4">
            <Link href="/" className="flex items-center gap-2.5">
              <Logo className="h-7 w-7" />
              <span className="font-pixel text-sm text-orange-500">
                Le Sésame
              </span>
            </Link>
            <p className="text-sm text-muted-foreground font-game text-base">
              The Multi-Level Secret Keeper Game. Can you outsmart the AI
              guardians?
            </p>
            <div className="flex items-center gap-2 opacity-60">
              <Image
                src="/mistral-logo.png"
                alt="Mistral AI"
                width={16}
                height={16}
              />
              <span className="text-xs text-muted-foreground">
                Powered by Mistral AI
              </span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-4 text-sm uppercase tracking-wider text-muted-foreground">
              Quick Links
            </h4>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/game"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Play Game
                </Link>
              </li>
              <li>
                <Link
                  href="/leaderboard"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Leaderboard
                </Link>
              </li>
              <li>
                <Link
                  href="/about"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  About
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold mb-4 text-sm uppercase tracking-wider text-muted-foreground">
              Resources
            </h4>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/about#how-it-works"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  How It Works
                </Link>
              </li>
              <li>
                <Link
                  href="/about#levels"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Level Guide
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/petrosrapto"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  GitHub
                </a>
              </li>
            </ul>
          </div>

          {/* Author */}
          <div>
            <h4 className="font-semibold mb-4 text-sm uppercase tracking-wider text-muted-foreground">
              Author
            </h4>
            <p className="text-sm text-muted-foreground mb-3">
              Petros Raptopoulos
            </p>
            <div className="flex gap-2">
              <a
                href="https://github.com/petrosrapto"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
                title="GitHub"
              >
                <Github className="w-4 h-4" />
              </a>
              <a
                href="https://www.linkedin.com/in/petrosrapto/"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
                title="LinkedIn"
              >
                <Linkedin className="w-4 h-4" />
              </a>
              <a
                href="https://scholar.google.com/citations?user=G7paGngAAAAJ&hl=en&oi=ao"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
                title="Google Scholar"
              >
                <GraduationCap className="w-4 h-4" />
              </a>
              <a
                href="https://petrosraptopoulos.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
                title="Website"
              >
                <Globe className="w-4 h-4" />
              </a>
              <a
                href="mailto:petrosrapto@gmail.com"
                className="p-2 rounded-lg bg-secondary hover:bg-secondary/80 transition-colors"
                title="Email"
              >
                <Mail className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-border">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Le Sésame. All rights reserved.
            </p>
            <p className="text-sm text-muted-foreground">
              Powered by{" "}
              <a
                href="https://mistral.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-500 hover:underline"
              >
                Mistral AI
              </a>{" "}
              · Implemented by{" "}
              <a
                href="https://petrosraptopoulos.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-orange-500 hover:underline"
              >
                Petros Raptopoulos
              </a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
