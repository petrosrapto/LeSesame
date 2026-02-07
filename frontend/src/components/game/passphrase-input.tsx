"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Key, Eye, EyeOff, ArrowRight, Sparkles } from "lucide-react";

interface PassphraseInputProps {
  onSubmit: (passphrase: string) => void;
  isLoading?: boolean;
  error?: string;
  hint?: string;
  className?: string;
}

export function PassphraseInput({
  onSubmit,
  isLoading = false,
  error,
  hint,
  className,
}: PassphraseInputProps) {
  const [passphrase, setPassphrase] = useState("");
  const [showPassphrase, setShowPassphrase] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (passphrase.trim()) {
      onSubmit(passphrase.trim());
    }
  };

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="bg-gold-500/5 border-b border-gold-500/10">
        <CardTitle className="flex items-center gap-3 text-lg">
          <div className="p-2 rounded-lg bg-gold-500/20">
            <Key className="w-5 h-5 text-gold-500" />
          </div>
          Enter the Passphrase
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <Input
              type={showPassphrase ? "text" : "password"}
              value={passphrase}
              onChange={(e) => setPassphrase(e.target.value)}
              placeholder="Enter the secret passphrase..."
              className="pr-12 h-12 text-lg"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowPassphrase(!showPassphrase)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            >
              {showPassphrase ? (
                <EyeOff className="w-5 h-5" />
              ) : (
                <Eye className="w-5 h-5" />
              )}
            </button>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
              {error}
            </div>
          )}

          {hint && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-gold-500/10 border border-gold-500/20 text-sm">
              <Sparkles className="w-4 h-4 text-gold-500 shrink-0 mt-0.5" />
              <span className="text-gold-700 dark:text-gold-400">{hint}</span>
            </div>
          )}

          <Button
            type="submit"
            variant="gold"
            className="w-full h-12 text-base gap-2"
            disabled={!passphrase.trim() || isLoading}
          >
            {isLoading ? (
              "Verifying..."
            ) : (
              <>
                Unlock the Secret
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
