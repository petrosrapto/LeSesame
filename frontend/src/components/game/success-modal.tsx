"use client";

import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { cn } from "@/lib/utils";
import {
  CheckCircle,
  Key,
  Sparkles,
  Trophy,
  BookOpen,
  Shield,
  AlertTriangle,
  Lightbulb,
  Globe,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import confetti from "@/lib/confetti";
import { useEffect, useState } from "react";
import { LEVEL_CHARACTERS, LEVEL_EDUCATION } from "@/lib/constants";

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
  const [showEducation, setShowEducation] = useState(false);

  useEffect(() => {
    if (isOpen) {
      confetti();
      setShowEducation(false);
    }
  }, [isOpen]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const character = LEVEL_CHARACTERS[level];
  const education = LEVEL_EDUCATION[level];

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
            className="bg-card border-2 border-border rounded-none shadow-2xl max-w-lg w-full overflow-hidden max-h-[90vh] overflow-y-auto custom-scrollbar pixel-border"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header with character */}
            <div className="relative bg-gradient-to-br from-orange-500 to-orange-600 p-8 text-center border-b-2 border-orange-500/30">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="inline-flex items-center justify-center w-20 h-20 rounded-none border-2 border-white/40 bg-white/20 backdrop-blur-sm mb-4 overflow-hidden"
              >
                {character ? (
                  <Image
                    src={character.image}
                    alt={character.name}
                    width={80}
                    height={80}
                    className="object-cover"
                  />
                ) : (
                  <Trophy className="w-10 h-10 text-white" />
                )}
              </motion.div>
              <motion.h2
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-xl font-pixel text-white"
              >
                Level {level} Complete!
              </motion.h2>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-white/80 mt-1 font-game text-lg"
              >
                {character
                  ? `You defeated ${character.name}!`
                  : "You've extracted the secret"}
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
                className="p-4 rounded-none border-2 border-success/30 bg-success/10 pixel-border"
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
                <div className="text-center p-3 rounded-none border-2 border-border bg-secondary/50">
                  <p className="text-2xl font-bold text-foreground">
                    {attempts}
                  </p>
                  <p className="text-xs text-muted-foreground">Attempts</p>
                </div>
                <div className="text-center p-3 rounded-none border-2 border-border bg-secondary/50">
                  <p className="text-2xl font-bold text-foreground">
                    {formatTime(timeSpent)}
                  </p>
                  <p className="text-xs text-muted-foreground">Time Spent</p>
                </div>
              </motion.div>

              {/* Educational content toggle */}
              {education && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.65 }}
                >
                  <button
                    onClick={() => setShowEducation(!showEducation)}
                    className="w-full flex items-center justify-between p-3 rounded-none border-2 border-orange-500/30 bg-orange-500/10 hover:bg-orange-500/15 transition-colors"
                  >
                    <div className="flex items-center gap-2 text-orange-500">
                      <BookOpen className="w-4 h-4" />
                      <span className="font-medium text-sm">
                        What did you learn?
                      </span>
                    </div>
                    {showEducation ? (
                      <ChevronUp className="w-4 h-4 text-orange-500" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-orange-500" />
                    )}
                  </button>

                  <AnimatePresence>
                    {showEducation && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                      >
                        <div className="mt-3 space-y-4 p-4 rounded-none border-2 border-border bg-secondary/30">
                          <h4 className="font-pixel text-xs text-orange-500">
                            {education.title}
                          </h4>

                          <div>
                            <div className="flex items-center gap-2 text-sm font-medium text-foreground mb-1">
                              <Lightbulb className="w-3.5 h-3.5 text-yellow-500" />
                              What You Learned
                            </div>
                            <p className="text-sm text-muted-foreground font-game">
                              {education.whatYouLearned}
                            </p>
                          </div>

                          <div>
                            <div className="flex items-center gap-2 text-sm font-medium text-foreground mb-1">
                              <Shield className="w-3.5 h-3.5 text-blue-500" />
                              How It Worked
                            </div>
                            <p className="text-sm text-muted-foreground font-game">
                              {education.howItWorked}
                            </p>
                          </div>

                          <div>
                            <div className="flex items-center gap-2 text-sm font-medium text-foreground mb-1">
                              <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
                              Why It Broke
                            </div>
                            <p className="text-sm text-muted-foreground font-game">
                              {education.whyItBroke}
                            </p>
                          </div>

                          <div>
                            <div className="text-sm font-medium text-foreground mb-2">
                              Techniques Used:
                            </div>
                            <div className="flex flex-wrap gap-1.5">
                              {education.techniques.map((tech) => (
                                <span
                                  key={tech}
                                  className="px-2 py-0.5 rounded-full bg-orange-500/10 text-orange-500 text-xs border border-orange-500/20"
                                >
                                  {tech}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div className="p-3 rounded-none border-2 border-border bg-card">
                            <div className="flex items-center gap-2 text-sm font-medium text-foreground mb-1">
                              <Globe className="w-3.5 h-3.5 text-green-500" />
                              Real-World Implication
                            </div>
                            <p className="text-sm text-muted-foreground font-game">
                              {education.realWorldImplication}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              )}

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
                {level < 5 && (
                  <Button
                    variant="gold"
                    className="flex-1"
                    onClick={onNextLevel}
                  >
                    Next Level
                  </Button>
                )}
              </motion.div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
