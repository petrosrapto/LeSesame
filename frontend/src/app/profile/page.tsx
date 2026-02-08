"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { User } from "lucide-react";
import { getStoredUsername } from "@/lib/auth";
import { getInitials, getStoredProfile, storeProfile } from "@/lib/profile";
import { AdminConsole } from "@/components/admin/admin-console";

const ACCENT_OPTIONS = [
  "#f97316",
  "#f59e0b",
  "#10b981",
  "#3b82f6",
  "#8b5cf6",
  "#ec4899",
];

export default function ProfilePage() {
  const [displayName, setDisplayName] = useState("");
  const [accent, setAccent] = useState(ACCENT_OPTIONS[0]);
  const [saved, setSaved] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const username = getStoredUsername() || "Player";
    const stored = getStoredProfile();
    if (stored) {
      setDisplayName(stored.displayName);
      setAccent(stored.accent);
    } else {
      setDisplayName(username);
    }

    // Check admin role from localStorage
    if (typeof window !== "undefined") {
      setIsAdmin(localStorage.getItem("le-sesame-user-role") === "admin");
    }
  }, []);

  const initials = getInitials(displayName || "Player");

  const handleSave = () => {
    storeProfile({ displayName: displayName.trim() || "Player", accent });
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-16 px-4">
        <div className="container mx-auto max-w-4xl">
          <Card className="pixel-card pixel-border">
            <CardHeader>
              <CardTitle className="pixel-heading text-2xl flex items-center gap-2">
                <User className="w-5 h-5 text-orange-500" />
                Profile
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex flex-col items-center gap-4">
                  <div
                    className="w-24 h-24 rounded-xl border-2 border-border flex items-center justify-center text-2xl font-pixel text-white"
                    style={{ backgroundColor: accent }}
                  >
                    {initials}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    This avatar appears next to your chat messages.
                  </p>
                </div>

                <div className="flex-1 space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground">
                      Display Name
                    </label>
                    <Input
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder="Your name"
                      className="rounded-none border-2 border-border"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground">
                      Accent Color
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {ACCENT_OPTIONS.map((option) => (
                        <button
                          key={option}
                          type="button"
                          className={`w-8 h-8 rounded-xl border-2 ${
                            accent === option
                              ? "border-orange-500"
                              : "border-border"
                          }`}
                          style={{ backgroundColor: option }}
                          onClick={() => setAccent(option)}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <Button variant="gold" className="pixel-border" onClick={handleSave}>
                      Save Profile
                    </Button>
                    {saved && (
                      <span className="text-sm text-success">Saved!</span>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Admin Console – visible only to admin users */}
          {isAdmin && (
            <div className="mt-8">
              <AdminConsole />
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
