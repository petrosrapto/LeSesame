"use client";

import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { CheckCircle, Key, Sparkles, Trophy } from "lucide-react";
import { Button } from "@/components/ui/button";
import confetti from "@/lib/confetti";
import { useEffect } from "react";

interface SuccessModalProps {
  isOpen: boolean;
  level: number;
  secret: string;
  attempts: number;
  timeSpent: number;
  onNextLevel: () => void;
  onClose: () => void;
}

export function SuccessModal({
  isOpen,
  level,
  secret,
  attempts,
  timeSpent,
  onNextLevel,
  onClose,
}: SuccessModalProps) {
  useEffect(() => {
    if (isOpen) {
      confetti();
    }
  }, [isOpen]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: "spring", duration: 0.5 }}
            className="bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header with animation */}
            <div className="relative bg-gradient-to-br from-gold-500 to-gold-600 p-8 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm mb-4"
              >
                <Trophy className="w-10 h-10 text-white" />
              </motion.div>
              <motion.h2
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-2xl font-display font-bold text-white"
              >
                Level {level} Complete!
              </motion.h2>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-white/80 mt-1"
              >
                You&apos;ve extracted the secret
              </motion.p>

              {/* Floating sparkles */}
              <Sparkles className="absolute top-4 right-4 w-6 h-6 text-white/40 animate-float" />
              <Sparkles className="absolute bottom-4 left-4 w-4 h-4 text-white/30 animate-float delay-300" />
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Secret reveal */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="p-4 rounded-xl bg-success/10 border border-success/20"
              >
                <div className="flex items-center gap-2 text-success text-sm mb-2">
                  <Key className="w-4 h-4" />
                  <span className="font-medium">The Secret Was:</span>
                </div>
                <p className="font-mono text-lg font-medium text-foreground">
                  {secret}
                </p>
              </motion.div>

              {/* Stats */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="grid grid-cols-2 gap-4"
              >
                <div className="text-center p-3 rounded-lg bg-secondary/50">
                  <p className="text-2xl font-bold text-foreground">
                    {attempts}
                  </p>
                  <p className="text-xs text-muted-foreground">Attempts</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-secondary/50">
                  <p className="text-2xl font-bold text-foreground">
                    {formatTime(timeSpent)}
                  </p>
                  <p className="text-xs text-muted-foreground">Time Spent</p>
                </div>
              </motion.div>

              {/* Actions */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className="flex gap-3"
              >
                <Button variant="outline" className="flex-1" onClick={onClose}>
                  View Stats
                </Button>
                <Button variant="gold" className="flex-1" onClick={onNextLevel}>
                  Next Level
                </Button>
              </motion.div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
