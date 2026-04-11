"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  LogIn,
  UserPlus,
  Loader2,
  X,
  Eye,
  EyeOff,
  Shield,
  Mail,
} from "lucide-react";
import { AuthAPI } from "@/lib/api";
import { useGoogleLogin } from "@react-oauth/google";
import { useGoogleReCaptcha } from "react-google-recaptcha-v3";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  closable?: boolean;
}

/** True when the env var is set (empty string = not configured). */
const googleEnabled = !!process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID;

export function LoginModal({ isOpen, onClose, onSuccess, closable = true }: LoginModalProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const { executeRecaptcha } = useGoogleReCaptcha();

  /** Obtain a reCAPTCHA v3 token for the given action.
   *  Returns empty string when reCAPTCHA is not configured so the
   *  backend can decide to skip verification in dev mode. */
  const getCaptchaToken = useCallback(
    async (action: string): Promise<string> => {
      if (!executeRecaptcha) return "";
      return executeRecaptcha(action);
    },
    [executeRecaptcha],
  );

  // ─── Local login / register ──────────────────────────────────

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password.");
      return;
    }

    if (mode === "register" && !email.trim()) {
      setError("Please enter your email address.");
      return;
    }

    setIsLoading(true);

    try {
      const captcha = await getCaptchaToken(mode);

      if (mode === "login") {
        await AuthAPI.login(username, password, captcha);

        if (typeof window !== "undefined") {
          window.dispatchEvent(new CustomEvent("auth-login"));
        }
        onSuccess();
      } else {
        const result = await AuthAPI.register(username, password, email, captcha);
        setSuccessMessage(
          result.message ||
            "Account created! Check your email for a verification link.",
        );
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
          : "Registration failed. Username or email may already be taken.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  // ─── Google OAuth ────────────────────────────────────────────

  const handleGoogleLogin = useCallback(async (credentialResponse: { credential?: string }) => {
    const credential = credentialResponse.credential;
    if (!credential) {
      setError("Google sign-in failed. No credential received.");
      return;
    }

    setError(null);
    setSuccessMessage(null);
    setIsLoading(true);

    try {
      const captcha = await getCaptchaToken("google_auth");
      await AuthAPI.googleAuth(credential, captcha);

      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("auth-login"));
      }
      onSuccess();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      const detail = axiosErr?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Google sign-in failed.");
    } finally {
      setIsLoading(false);
    }
  }, [getCaptchaToken, onSuccess]);

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

              {/* ── Google sign-in button ── */}
              {googleEnabled && (
                <>
                  <GoogleSignInButton
                    onSuccess={handleGoogleLogin}
                    disabled={isLoading}
                  />

                  <div className="relative flex items-center gap-3">
                    <div className="flex-1 h-px bg-border" />
                    <span className="text-xs text-muted-foreground select-none">or</span>
                    <div className="flex-1 h-px bg-border" />
                  </div>
                </>
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
                    Email
                  </label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    autoComplete="email"
                    disabled={isLoading}
                    required
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

              {/* Resend verification link (login mode only) */}
              {mode === "login" && (
                <div className="text-center">
                  <ResendVerificationLink getCaptchaToken={getCaptchaToken} />
                </div>
              )}

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

              {/* reCAPTCHA attribution (required when badge is hidden) */}
              <p className="text-[10px] text-muted-foreground/50 text-center leading-snug">
                This site is protected by reCAPTCHA and the Google{" "}
                <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="underline hover:text-muted-foreground">Privacy Policy</a> and{" "}
                <a href="https://policies.google.com/terms" target="_blank" rel="noopener noreferrer" className="underline hover:text-muted-foreground">Terms of Service</a> apply.
              </p>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// ─── Google Sign-In Button ─────────────────────────────────────

function GoogleSignInButton({
  onSuccess,
  disabled,
}: {
  onSuccess: (resp: { credential?: string }) => void;
  disabled: boolean;
}) {
  // useGoogleLogin with implicit flow returns an access_token.
  // The backend verifies it via Google's userinfo endpoint.
  const login = useGoogleLogin({
    flow: "implicit",
    onSuccess: (tokenResponse) => {
      onSuccess({ credential: tokenResponse.access_token });
    },
    onError: () => {
      /* handled by parent */
    },
  });

  return (
    <button
      type="button"
      onClick={() => login()}
      disabled={disabled}
      className="w-full flex items-center justify-center gap-3 px-4 py-2.5 border-2 border-border bg-background hover:bg-muted transition-colors text-sm font-medium disabled:opacity-50"
    >
      <svg className="w-5 h-5" viewBox="0 0 24 24">
        <path
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
          fill="#4285F4"
        />
        <path
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          fill="#34A853"
        />
        <path
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          fill="#FBBC05"
        />
        <path
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          fill="#EA4335"
        />
      </svg>
      Continue with Google
    </button>
  );
}

// ─── Resend Verification Link ──────────────────────────────────

function ResendVerificationLink({
  getCaptchaToken,
}: {
  getCaptchaToken: (action: string) => Promise<string>;
}) {
  const [show, setShow] = useState(false);
  const [resendEmail, setResendEmail] = useState("");
  const [resendMsg, setResendMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleResend = async () => {
    if (!resendEmail.trim()) return;
    setLoading(true);
    setResendMsg(null);
    try {
      const captcha = await getCaptchaToken("resend_verification");
      await AuthAPI.resendVerification(resendEmail, captcha);
      setResendMsg("If that email is registered, a new verification link has been sent.");
    } catch {
      setResendMsg("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!show) {
    return (
      <button
        type="button"
        onClick={() => setShow(true)}
        className="text-xs text-muted-foreground/60 hover:text-orange-500 transition-colors"
      >
        Didn&apos;t get a verification email?
      </button>
    );
  }

  return (
    <div className="space-y-2 p-3 border-2 border-border rounded-none bg-muted/30">
      <p className="text-xs text-muted-foreground">
        Enter your email to resend the verification link:
      </p>
      <div className="flex gap-2">
        <Input
          type="email"
          value={resendEmail}
          onChange={(e) => setResendEmail(e.target.value)}
          placeholder="you@example.com"
          className="text-xs rounded-none border-2 border-border h-8"
        />
        <Button
          type="button"
          variant="gold"
          className="h-8 px-3 text-xs"
          disabled={loading}
          onClick={handleResend}
        >
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Mail className="w-3 h-3" />}
        </Button>
      </div>
      {resendMsg && (
        <p className="text-xs text-green-500">{resendMsg}</p>
      )}
    </div>
  );
}
