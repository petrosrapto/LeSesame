"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Logo } from "@/components/brand/logo";
import {
  LogIn,
  UserPlus,
  Loader2,
  X,
  Eye,
  EyeOff,
  Shield,
} from "lucide-react";
import { AuthAPI } from "@/lib/api";
import { storeToken } from "@/lib/auth";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  closable?: boolean;
}

export function LoginModal({ isOpen, onClose, onSuccess, closable = true }: LoginModalProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password.");
      return;
    }

    setIsLoading(true);

    try {
      if (mode === "login") {
        await AuthAPI.login(username, password);

        // Dispatch auth event so navbar updates
        if (typeof window !== "undefined") {
          window.dispatchEvent(new CustomEvent("auth-login"));
        }

        onSuccess();
      } else {
        const result = await AuthAPI.register(username, password, email || undefined);
        // Registration requires admin approval – show message, don't auto-login
        setSuccessMessage(
          result.message ||
            "Account created! An admin must approve your account before you can sign in."
        );
        // Switch to login mode so user can sign in after approval
        setMode("login");
        setUsername("");
        setPassword("");
        setEmail("");
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      const detail = axiosErr?.response?.data?.detail;
      setError(
        typeof detail === "string"
          ? detail
          : mode === "login"
          ? "Invalid username or password."
          : "Registration failed. Username may already be taken."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={closable ? onClose : undefined}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: "spring", duration: 0.5 }}
            className="bg-card border-2 border-border rounded-none shadow-2xl max-w-md w-full overflow-hidden pixel-border"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="relative bg-gradient-to-br from-orange-500 to-orange-600 p-6 text-center border-b-2 border-orange-500/30">
              {closable && (
                <button
                  onClick={onClose}
                  className="absolute top-3 right-3 p-1 rounded-none border-2 border-white/40 bg-white/20 hover:bg-white/30 transition-colors"
                >
                  <X className="w-4 h-4 text-white" />
                </button>
              )}
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-none border-2 border-white/40 bg-white/20 backdrop-blur-sm mb-3">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-lg font-pixel text-white">
                {mode === "login" ? "Welcome Back" : "Join the Game"}
              </h2>
              <p className="text-white/80 text-sm mt-1 font-game">
                {mode === "login"
                  ? "Sign in to challenge the guardians"
                  : "Create an account to start playing"}
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {error && (
                <div className="p-3 rounded-none border-2 border-red-500/30 bg-red-500/10 text-red-500 text-sm">
                  {error}
                </div>
              )}

              {successMessage && (
                <div className="p-3 rounded-none border-2 border-green-500/30 bg-green-500/10 text-green-500 text-sm">
                  {successMessage}
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Username
                </label>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter your username"
                  autoComplete="username"
                  disabled={isLoading}
                  className="rounded-none border-2 border-border"
                />
              </div>

              {mode === "register" && (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">
                    Email{" "}
                    <span className="text-xs text-muted-foreground/60">
                      (optional)
                    </span>
                  </label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    autoComplete="email"
                    disabled={isLoading}
                    className="rounded-none border-2 border-border"
                  />
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Password
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    autoComplete={
                      mode === "login" ? "current-password" : "new-password"
                    }
                    disabled={isLoading}
                    className="pr-10 rounded-none border-2 border-border"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                variant="gold"
                className="w-full gap-2 pixel-border"
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : mode === "login" ? (
                  <LogIn className="w-4 h-4" />
                ) : (
                  <UserPlus className="w-4 h-4" />
                )}
                {isLoading
                  ? "Please wait..."
                  : mode === "login"
                  ? "Sign In"
                  : "Create Account"}
              </Button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => {
                    setMode(mode === "login" ? "register" : "login");
                    setError(null);
                    setSuccessMessage(null);
                  }}
                  className="text-sm text-muted-foreground hover:text-orange-500 transition-colors"
                >
                  {mode === "login"
                    ? "Don't have an account? Register"
                    : "Already have an account? Sign in"}
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
