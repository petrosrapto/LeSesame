"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Loader2, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Status = "loading" | "success" | "error";

function VerifyEmailContent() {
  const params = useSearchParams();
  const token = params.get("token");
  const [status, setStatus] = useState<Status>("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Missing verification token.");
      return;
    }

    (async () => {
      try {
        const res = await fetch(
          `${API_BASE_URL}/auth/verify-email?token=${encodeURIComponent(token)}`
        );
        const data = await res.json();

        if (res.ok) {
          setStatus("success");
          setMessage(data.message || "Email verified successfully!");
        } else {
          setStatus("error");
          setMessage(data.detail || "Verification failed.");
        }
      } catch {
        setStatus("error");
        setMessage("Could not reach the server. Please try again later.");
      }
    })();
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="max-w-md w-full bg-card border-2 border-border rounded-none shadow-2xl pixel-border overflow-hidden"
      >
        {/* Header */}
        <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-6 text-center border-b-2 border-orange-500/30">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-none border-2 border-white/40 bg-white/20 backdrop-blur-sm mb-3">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-lg font-pixel text-white">Email Verification</h1>
        </div>

        {/* Body */}
        <div className="p-8 flex flex-col items-center text-center space-y-6">
          {status === "loading" && (
            <>
              <Loader2 className="w-12 h-12 text-orange-500 animate-spin" />
              <p className="text-muted-foreground">Verifying your email…</p>
            </>
          )}

          {status === "success" && (
            <>
              <CheckCircle2 className="w-12 h-12 text-green-500" />
              <p className="text-green-400 font-medium">{message}</p>
              <Link href="/">
                <Button variant="gold" className="pixel-border">
                  Go to Le Sésame
                </Button>
              </Link>
            </>
          )}

          {status === "error" && (
            <>
              <XCircle className="w-12 h-12 text-red-500" />
              <p className="text-red-400 font-medium">{message}</p>
              <Link href="/">
                <Button variant="gold" className="pixel-border">
                  Back to Home
                </Button>
              </Link>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center p-4 bg-background">
          <Loader2 className="w-12 h-12 text-orange-500 animate-spin" />
        </div>
      }
    >
      <VerifyEmailContent />
    </Suspense>
  );
}
