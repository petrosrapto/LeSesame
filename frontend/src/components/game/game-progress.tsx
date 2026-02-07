"use client";

import { cn } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import { Card } from "@/components/ui/card";
import {
  Lock,
  Unlock,
  Trophy,
  Target,
  MessageSquare,
  Clock,
} from "lucide-react";
import { getLevelName } from "@/lib/utils";

interface GameProgressProps {
  currentLevel: number;
  maxLevel: number;
  completedLevels: number[];
  totalAttempts: number;
  successfulAttempts: number;
  sessionTime: number; // in seconds
  className?: string;
}

export function GameProgress({
  currentLevel,
  maxLevel,
  completedLevels,
  totalAttempts,
  successfulAttempts,
  sessionTime,
  className,
}: GameProgressProps) {
  const progressPercentage = (completedLevels.length / maxLevel) * 100;
  const successRate =
    totalAttempts > 0 ? (successfulAttempts / totalAttempts) * 100 : 0;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Card className={cn("p-6 pixel-card pixel-border", className)}>
      <div className="space-y-6">
        {/* Overall Progress */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm text-muted-foreground">
              {completedLevels.length} / {maxLevel} Levels
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>

        {/* Level indicators */}
        <div className="flex justify-between">
          {Array.from({ length: maxLevel }, (_, i) => i + 1).map((level) => {
            const isCompleted = completedLevels.includes(level);
            const isCurrent = level === currentLevel;
            const isLocked = level > currentLevel && !isCompleted;

            return (
              <div
                key={level}
                className={cn(
                  "flex flex-col items-center gap-1",
                  isLocked && "opacity-40"
                )}
              >
                <div
                  className={cn(
                    "w-10 h-10 rounded-none border-2 border-border flex items-center justify-center transition-all duration-300",
                    isCompleted && "bg-success text-success-foreground",
                    isCurrent &&
                      !isCompleted &&
                      "bg-orange-500 text-white ring-4 ring-orange-500/30 animate-pulse-glow",
                    isLocked && "bg-muted text-muted-foreground"
                  )}
                >
                  {isCompleted ? (
                    <Unlock className="w-4 h-4" />
                  ) : (
                    <Lock className="w-4 h-4" />
                  )}
                </div>
                <span className="text-xs text-muted-foreground">{level}</span>
              </div>
            );
          })}
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-3 p-3 rounded-none border-2 border-border bg-secondary/50">
            <div className="p-2 rounded-none border-2 border-border bg-primary/10">
              <MessageSquare className="w-4 h-4 text-primary" />
            </div>
            <div>
              <p className="text-lg font-semibold">{totalAttempts}</p>
              <p className="text-xs text-muted-foreground">Total Attempts</p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 rounded-none border-2 border-border bg-secondary/50">
            <div className="p-2 rounded-none border-2 border-border bg-success/10">
              <Target className="w-4 h-4 text-success" />
            </div>
            <div>
              <p className="text-lg font-semibold">{successRate.toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground">Success Rate</p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 rounded-none border-2 border-border bg-secondary/50">
            <div className="p-2 rounded-none border-2 border-border bg-orange-500/10">
              <Trophy className="w-4 h-4 text-orange-500" />
            </div>
            <div>
              <p className="text-lg font-semibold">{completedLevels.length}</p>
              <p className="text-xs text-muted-foreground">Levels Completed</p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3 rounded-none border-2 border-border bg-secondary/50">
            <div className="p-2 rounded-none border-2 border-border bg-blue-500/10">
              <Clock className="w-4 h-4 text-blue-500" />
            </div>
            <div>
              <p className="text-lg font-semibold">{formatTime(sessionTime)}</p>
              <p className="text-xs text-muted-foreground">Session Time</p>
            </div>
          </div>
        </div>

        {/* Current level info */}
        <div className="pt-4 border-t border-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Current Challenge</p>
              <p className="font-mono font-semibold">
                Level {currentLevel}: {getLevelName(currentLevel)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Difficulty</p>
              <div className="flex gap-1">
                {Array.from({ length: 5 }, (_, i) => (
                  <div
                    key={i}
                    className={cn(
                      "w-2 h-2 rounded-full",
                      i < currentLevel ? "bg-orange-500" : "bg-muted"
                    )}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
