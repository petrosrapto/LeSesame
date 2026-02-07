"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import {
  Trophy,
  Medal,
  Crown,
  Clock,
  Target,
  MessageSquare,
  User,
  ChevronUp,
  ChevronDown,
  Minus,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Mock leaderboard data
const leaderboardData = {
  overall: [
    {
      rank: 1,
      username: "SecretHunter",
      score: 4850,
      levelsCompleted: 5,
      avgAttempts: 12,
      change: "up",
    },
    {
      rank: 2,
      username: "PromptMaster",
      score: 4200,
      levelsCompleted: 5,
      avgAttempts: 18,
      change: "same",
    },
    {
      rank: 3,
      username: "AIWhisperer",
      score: 3900,
      levelsCompleted: 4,
      avgAttempts: 8,
      change: "down",
    },
    {
      rank: 4,
      username: "JailbreakPro",
      score: 3650,
      levelsCompleted: 4,
      avgAttempts: 22,
      change: "up",
    },
    {
      rank: 5,
      username: "CryptoNinja",
      score: 3400,
      levelsCompleted: 4,
      avgAttempts: 15,
      change: "up",
    },
    {
      rank: 6,
      username: "RedTeamer",
      score: 3100,
      levelsCompleted: 3,
      avgAttempts: 10,
      change: "same",
    },
    {
      rank: 7,
      username: "SesameSolver",
      score: 2850,
      levelsCompleted: 3,
      avgAttempts: 25,
      change: "down",
    },
    {
      rank: 8,
      username: "VaultBreaker",
      score: 2600,
      levelsCompleted: 3,
      avgAttempts: 30,
      change: "up",
    },
    {
      rank: 9,
      username: "KeyMaster",
      score: 2400,
      levelsCompleted: 2,
      avgAttempts: 5,
      change: "same",
    },
    {
      rank: 10,
      username: "EnigmaDecoder",
      score: 2200,
      levelsCompleted: 2,
      avgAttempts: 12,
      change: "down",
    },
  ],
  weekly: [
    {
      rank: 1,
      username: "WeeklyChamp",
      score: 1200,
      levelsCompleted: 3,
      avgAttempts: 8,
      change: "up",
    },
    {
      rank: 2,
      username: "RisingStark",
      score: 950,
      levelsCompleted: 2,
      avgAttempts: 10,
      change: "up",
    },
    {
      rank: 3,
      username: "QuickSolver",
      score: 800,
      levelsCompleted: 2,
      avgAttempts: 6,
      change: "same",
    },
  ],
  fastest: [
    {
      rank: 1,
      username: "SpeedRunner",
      time: "2:34",
      level: 1,
      attempts: 3,
      change: "same",
    },
    {
      rank: 2,
      username: "FlashSolve",
      time: "3:12",
      level: 1,
      attempts: 5,
      change: "up",
    },
    {
      rank: 3,
      username: "LightningFast",
      time: "4:45",
      level: 2,
      attempts: 8,
      change: "down",
    },
  ],
};

const getRankIcon = (rank: number) => {
  switch (rank) {
    case 1:
      return <Crown className="w-5 h-5 text-orange-500" />;
    case 2:
      return <Medal className="w-5 h-5 text-gray-400" />;
    case 3:
      return <Medal className="w-5 h-5 text-amber-600" />;
    default:
      return <span className="w-5 text-center font-bold">{rank}</span>;
  }
};

const getChangeIcon = (change: string) => {
  switch (change) {
    case "up":
      return <ChevronUp className="w-4 h-4 text-success" />;
    case "down":
      return <ChevronDown className="w-4 h-4 text-destructive" />;
    default:
      return <Minus className="w-4 h-4 text-muted-foreground" />;
  }
};

export default function LeaderboardPage() {
  const [selectedLevel, setSelectedLevel] = useState<number | "all">("all");

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="pt-24 pb-16 px-4">
        <div className="container mx-auto max-w-6xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <div className="section-label bg-orange-500/10 text-orange-500 border border-orange-500/20 mb-6 mx-auto w-fit">
              <Trophy className="w-3 h-3" />
              <span>GLOBAL RANKINGS</span>
            </div>
            <h1 className="pixel-heading text-2xl md:text-3xl mb-4 text-foreground">
              <span className="text-orange-500">Leaderboard</span>
            </h1>
            <p className="text-muted-foreground max-w-2xl mx-auto font-game text-xl">
              See how you rank against other secret hunters. The best attackers
              rise to the top.
            </p>
          </motion.div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-lg bg-orange-500/10">
                      <Trophy className="w-6 h-6 text-orange-500" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">847</p>
                      <p className="text-sm text-muted-foreground">
                        Total Players
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-success/10">
                      <Target className="w-6 h-6 text-success" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">23</p>
                      <p className="text-sm text-muted-foreground">
                        Level 5 Completions
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-blue-500/10">
                      <MessageSquare className="w-6 h-6 text-blue-500" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">45.2K</p>
                      <p className="text-sm text-muted-foreground">
                        Total Attempts
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Leaderboard Tabs */}
          <Tabs defaultValue="overall" className="space-y-6">
            <TabsList className="grid w-full grid-cols-3 max-w-md">
              <TabsTrigger value="overall">Overall</TabsTrigger>
              <TabsTrigger value="weekly">This Week</TabsTrigger>
              <TabsTrigger value="fastest">Fastest Clears</TabsTrigger>
            </TabsList>

            <TabsContent value="overall">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-orange-500" />
                    All-Time Rankings
                  </CardTitle>
                  <CardDescription>
                    Top players ranked by total score across all levels
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {leaderboardData.overall.map((player, index) => (
                      <motion.div
                        key={player.username}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.05 * index }}
                        className={cn(
                          "flex items-center gap-4 p-4 rounded-lg transition-colors",
                          player.rank <= 3
                            ? "bg-orange-500/5 border border-orange-500/10"
                            : "hover:bg-secondary/50"
                        )}
                      >
                        <div className="w-8 flex justify-center">
                          {getRankIcon(player.rank)}
                        </div>
                        <div className="flex items-center gap-3 flex-1">
                          <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
                            <User className="w-5 h-5 text-muted-foreground" />
                          </div>
                          <div>
                            <p className="font-medium">{player.username}</p>
                            <p className="text-xs text-muted-foreground">
                              {player.levelsCompleted} levels completed
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-lg">{player.score}</p>
                          <p className="text-xs text-muted-foreground">
                            {player.avgAttempts} avg attempts
                          </p>
                        </div>
                        <div className="w-6">{getChangeIcon(player.change)}</div>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="weekly">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-blue-500" />
                    Weekly Rankings
                  </CardTitle>
                  <CardDescription>
                    Top performers this week
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {leaderboardData.weekly.map((player, index) => (
                      <motion.div
                        key={player.username}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.05 * index }}
                        className={cn(
                          "flex items-center gap-4 p-4 rounded-lg transition-colors",
                          player.rank <= 3
                            ? "bg-orange-500/5 border border-orange-500/10"
                            : "hover:bg-secondary/50"
                        )}
                      >
                        <div className="w-8 flex justify-center">
                          {getRankIcon(player.rank)}
                        </div>
                        <div className="flex items-center gap-3 flex-1">
                          <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
                            <User className="w-5 h-5 text-muted-foreground" />
                          </div>
                          <div>
                            <p className="font-medium">{player.username}</p>
                            <p className="text-xs text-muted-foreground">
                              {player.levelsCompleted} levels completed
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-lg">{player.score}</p>
                          <p className="text-xs text-muted-foreground">
                            {player.avgAttempts} avg attempts
                          </p>
                        </div>
                        <div className="w-6">{getChangeIcon(player.change)}</div>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="fastest">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-success" />
                    Fastest Clears
                  </CardTitle>
                  <CardDescription>
                    Speedrun records for each level
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {leaderboardData.fastest.map((player, index) => (
                      <motion.div
                        key={player.username}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.05 * index }}
                        className="flex items-center gap-4 p-4 rounded-xl hover:bg-secondary/50 transition-colors"
                      >
                        <div className="w-8 flex justify-center">
                          {getRankIcon(player.rank)}
                        </div>
                        <div className="flex items-center gap-3 flex-1">
                          <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center">
                            <User className="w-5 h-5 text-muted-foreground" />
                          </div>
                          <div>
                            <p className="font-medium">{player.username}</p>
                            <p className="text-xs text-muted-foreground">
                              Level {player.level}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-lg font-mono">
                            {player.time}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {player.attempts} attempts
                          </p>
                        </div>
                        <div className="w-6">{getChangeIcon(player.change)}</div>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      <Footer />
    </div>
  );
}
