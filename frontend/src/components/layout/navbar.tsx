"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/brand/logo";
import {
  Gamepad2,
  Trophy,
  Info,
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

  const router = useRouter();

  const handleLogout = () => {
    logout();
    setAuthed(false);
    setUsername(null);
    router.push("/");
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b-2 border-border/70 bg-card/90 backdrop-blur-md pixel-grid">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid h-16 items-center" style={{ gridTemplateColumns: '1fr auto 1fr' }}>
          {/* Left — Logo & Title */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center gap-3 shrink-0">
              <div className="p-1.5 border-2 border-border bg-background/60 pixel-border">
                <Logo className="h-7 w-7" />
              </div>
              <span className="font-pixel text-sm text-orange-500 hidden sm:block">
                Le Sésame
              </span>
            </Link>
          </div>

          {/* Center — Navigation */}
          <div className="hidden md:flex items-center gap-2 justify-center">
            {navItems.map((item) => (
              <Link key={item.href} href={item.href}>
                <Button
                  variant={pathname === item.href ? "secondary" : "ghost"}
                  className={cn(
                    "gap-2 text-sm border-2 border-transparent",
                    pathname === item.href && "bg-orange-500/10 text-orange-500 border-orange-500/30"
                  )}
                >
                  {item.icon && <item.icon className="w-4 h-4" />}
                  {item.label}
                </Button>
              </Link>
            ))}
          </div>

          {/* Right — Theme, Profile, Logout */}
          <div className="flex items-center gap-2 justify-end">
            {/* Theme toggle */}
            {mounted && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="text-muted-foreground hover:text-foreground border-2 border-transparent hover:border-border"
              >
                {theme === "dark" ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </Button>
            )}

            {/* Auth button */}
            {!mounted ? (
              <div className="hidden sm:block w-[148px]" aria-hidden="true" />
            ) : authed ? (
              <div className="hidden sm:flex items-center gap-2">
                <Link
                  href="/profile"
                  className="text-xs text-muted-foreground font-mono border-2 border-border/50 px-2 py-1 bg-background/70 hover:border-orange-500/40 hover:text-foreground transition-colors"
                >
                  <User className="w-3 h-3 inline mr-1" />
                  {username}
                </Link>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="gap-1 text-xs border-2 border-transparent hover:border-border"
                >
                  <LogOut className="w-3 h-3" />
                  Logout
                </Button>
              </div>
            ) : (
              <Link href="/game" className="hidden sm:block">
                <Button variant="gold" size="sm" className="gap-2 pixel-border">
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
              className="md:hidden border-2 border-transparent hover:border-border"
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
          <div className="md:hidden border-t-2 border-border py-4 animate-slide-up">
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
                      "w-full justify-start gap-2 border-2 border-transparent",
                      pathname === item.href && "bg-orange-500/10 text-orange-500 border-orange-500/30"
                    )}
                  >
                    {item.icon && <item.icon className="w-4 h-4" />}
                    {item.label}
                  </Button>
                </Link>
              ))}
              {mounted && authed && (
                <>
                  <Link href="/profile" onClick={() => setMobileMenuOpen(false)}>
                    <Button
                      variant="ghost"
                      className="w-full justify-start gap-2"
                    >
                      <User className="w-4 h-4" />
                      Profile
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    className="w-full justify-start gap-2"
                    onClick={handleLogout}
                  >
                    <LogOut className="w-4 h-4" />
                    Logout ({username})
                  </Button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
