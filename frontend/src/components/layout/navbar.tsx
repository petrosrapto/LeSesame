"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/brand/logo";
import {
  Gamepad2,
  Trophy,
  Info,
  Github,
  Moon,
  Sun,
  Menu,
  X,
  ArrowRight,
  LogOut,
  User,
} from "lucide-react";
import { useTheme } from "next-themes";
import { useState, useEffect } from "react";
import { isAuthenticated, getStoredUsername, logout } from "@/lib/auth";

const navItems = [
  { href: "/", label: "Home", icon: null },
  { href: "/game", label: "Play", icon: Gamepad2 },
  { href: "/leaderboard", label: "Leaderboard", icon: Trophy },
  { href: "/about", label: "About", icon: Info },
];

export function Navbar() {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [authed, setAuthed] = useState(false);
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
    setAuthed(isAuthenticated());
    setUsername(getStoredUsername());

    const handleAuthChange = () => {
      setAuthed(isAuthenticated());
      setUsername(getStoredUsername());
    };

    window.addEventListener("auth-logout", handleAuthChange);
    window.addEventListener("auth-login", handleAuthChange);
    return () => {
      window.removeEventListener("auth-logout", handleAuthChange);
      window.removeEventListener("auth-login", handleAuthChange);
    };
  }, []);

  const handleLogout = () => {
    logout();
    setAuthed(false);
    setUsername(null);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/90 backdrop-blur-md">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5">
            <Logo className="h-7 w-7" />
            <span className="font-pixel text-sm text-orange-500 hidden sm:block">
              Le Sésame
            </span>
            <Image
              src="/mistral-logo.png"
              alt="Mistral AI"
              width={20}
              height={20}
              className="opacity-60 hidden sm:block"
            />
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link key={item.href} href={item.href}>
                <Button
                  variant={pathname === item.href ? "secondary" : "ghost"}
                  className={cn(
                    "gap-2 text-sm",
                    pathname === item.href && "bg-orange-500/10 text-orange-500"
                  )}
                >
                  {item.icon && <item.icon className="w-4 h-4" />}
                  {item.label}
                </Button>
              </Link>
            ))}
          </div>

          {/* Right side actions */}
          <div className="flex items-center gap-2">
            {/* Theme toggle */}
            {mounted && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="text-muted-foreground hover:text-foreground"
              >
                {theme === "dark" ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </Button>
            )}

            {/* GitHub link */}
            <a
              href="https://github.com/petrosrapto"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="ghost" size="icon" className="hidden sm:flex">
                <Github className="h-5 w-5" />
              </Button>
            </a>

            {/* Auth button */}
            {mounted && authed ? (
              <div className="hidden sm:flex items-center gap-2">
                <span className="text-xs text-muted-foreground font-mono">
                  <User className="w-3 h-3 inline mr-1" />
                  {username}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="gap-1 text-xs"
                >
                  <LogOut className="w-3 h-3" />
                  Logout
                </Button>
              </div>
            ) : (
              <Link href="/game" className="hidden sm:block">
                <Button variant="gold" size="sm" className="gap-2">
                  <Gamepad2 className="w-4 h-4" />
                  Play Now
                  <ArrowRight className="w-3 h-3" />
                </Button>
              </Link>
            )}

            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-border py-4 animate-slide-up">
            <div className="flex flex-col gap-2">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Button
                    variant={pathname === item.href ? "secondary" : "ghost"}
                    className={cn(
                      "w-full justify-start gap-2",
                      pathname === item.href && "bg-orange-500/10 text-orange-500"
                    )}
                  >
                    {item.icon && <item.icon className="w-4 h-4" />}
                    {item.label}
                  </Button>
                </Link>
              ))}
              {mounted && authed && (
                <Button
                  variant="ghost"
                  className="w-full justify-start gap-2"
                  onClick={handleLogout}
                >
                  <LogOut className="w-4 h-4" />
                  Logout ({username})
                </Button>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
