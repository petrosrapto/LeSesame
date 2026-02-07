"use client";

import { cn } from "@/lib/utils";
import { Lock, Unlock, Shield, ShieldCheck, Eye, Brain } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getLevelName, getLevelDescription } from "@/lib/utils";

interface LevelCardProps {
  level: number;
  status: "locked" | "active" | "completed";
  onSelect?: () => void;
  attempts?: number;
  successRate?: number;
  className?: string;
}

const levelIcons: Record<number, React.ElementType> = {
  1: Lock,
  2: Shield,
  3: Eye,
  4: ShieldCheck,
  5: Brain,
};

const difficultyLabels: Record<number, string> = {
  1: "Beginner",
  2: "Intermediate",
  3: "Advanced",
  4: "Expert",
  5: "Master",
};

const difficultyColors: Record<number, string> = {
  1: "text-green-500 bg-green-500/10",
  2: "text-yellow-500 bg-yellow-500/10",
  3: "text-orange-500 bg-orange-500/10",
  4: "text-red-500 bg-red-500/10",
  5: "text-purple-500 bg-purple-500/10",
};

export function LevelCard({
  level,
  status,
  onSelect,
  attempts = 0,
  successRate,
  className,
}: LevelCardProps) {
  const Icon = status === "completed" ? Unlock : levelIcons[level] || Lock;
  const name = getLevelName(level);
  const description = getLevelDescription(level);

  return (
    <Card
      className={cn(
        "relative overflow-hidden transition-all duration-300 group",
        status === "locked" && "opacity-60 grayscale",
        status === "active" && "ring-2 ring-gold-500/50 shadow-lg shadow-gold-500/10",
        status === "completed" && "bg-success/5 border-success/30",
        status !== "locked" && "hover:shadow-xl hover:scale-[1.02] cursor-pointer",
        className
      )}
      onClick={status !== "locked" ? onSelect : undefined}
    >
      {/* Shimmer effect for active level */}
      {status === "active" && (
        <div className="absolute inset-0 shimmer pointer-events-none" />
      )}

      {/* Status badge */}
      <div className="absolute top-4 right-4">
        <span
          className={cn(
            "level-badge text-xs",
            status === "locked" && "level-locked",
            status === "active" && "level-active",
            status === "completed" && "level-completed"
          )}
        >
          {status === "locked" && "Locked"}
          {status === "active" && "Current"}
          {status === "completed" && "Completed"}
        </span>
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-start gap-4">
          <div
            className={cn(
              "p-3 rounded-xl transition-all duration-300",
              status === "completed"
                ? "bg-success/20 text-success"
                : status === "active"
                ? "bg-gold-500/20 text-gold-500 animate-pulse-glow"
                : "bg-muted text-muted-foreground"
            )}
          >
            <Icon className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <CardTitle className="text-lg flex items-center gap-2">
              Level {level}
              <span
                className={cn(
                  "text-xs px-2 py-0.5 rounded-full font-normal",
                  difficultyColors[level]
                )}
              >
                {difficultyLabels[level]}
              </span>
            </CardTitle>
            <CardDescription className="mt-1 font-display text-base">
              {name}
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">{description}</p>

        {/* Stats */}
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          {attempts > 0 && (
            <span className="flex items-center gap-1">
              <span className="font-medium text-foreground">{attempts}</span>
              attempts
            </span>
          )}
          {successRate !== undefined && (
            <span className="flex items-center gap-1">
              <span className="font-medium text-foreground">
                {successRate.toFixed(1)}%
              </span>
              success rate
            </span>
          )}
        </div>

        {/* Action button */}
        {status !== "locked" && (
          <Button
            variant={status === "completed" ? "outline" : "gold"}
            className="w-full mt-4 group-hover:shadow-md transition-all"
            size="sm"
          >
            {status === "completed" ? "Replay" : "Start Challenge"}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
