"use client";

import { useState, useEffect, useCallback } from "react";
import { Navbar } from "@/components/layout/navbar";
import { ChatInterface } from "@/components/game/chat-interface";
import { GameProgress } from "@/components/game/game-progress";
import { LevelCard } from "@/components/game/level-card";
import { PassphraseInput } from "@/components/game/passphrase-input";
import { SuccessModal } from "@/components/game/success-modal";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/toast";
import { useGame } from "@/hooks/use-game";
import { Message } from "@/components/game/chat-message";
import { generateId, getLevelName } from "@/lib/utils";
import {
  MessageSquare,
  Key,
  ChevronLeft,
  ChevronRight,
  Lightbulb,
  BookOpen,
} from "lucide-react";

export default function GamePage() {
  const { showToast } = useToast();
  const {
    currentLevel,
    completedLevels,
    totalAttempts,
    successfulAttempts,
    setCurrentLevel,
    completeLevel,
    incrementAttempts,
  } = useGame();

  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionTime, setSessionTime] = useState(0);
  const [levelStartTime, setLevelStartTime] = useState(Date.now());
  const [showSuccess, setShowSuccess] = useState(false);
  const [revealedSecret, setRevealedSecret] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Session timer
  useEffect(() => {
    const interval = setInterval(() => {
      setSessionTime((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Reset messages when level changes
  useEffect(() => {
    setMessages([]);
    setLevelStartTime(Date.now());
  }, [currentLevel]);

  const handleSendMessage = useCallback(
    async (content: string) => {
      // Add user message
      const userMessage: Message = {
        id: generateId(),
        role: "user",
        content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      incrementAttempts();

      try {
        // Simulate API call - replace with actual API
        await new Promise((resolve) => setTimeout(resolve, 1500));

        // Mock response based on level
        const responses = [
          "I appreciate your curiosity, but I'm afraid I cannot reveal the secret. It's protected information that I must keep confidential.",
          "Nice try! But I'm designed to keep secrets safe. Perhaps try a different approach?",
          "I understand you want to know the secret, but my purpose is to protect it. I will not reveal it under any circumstances.",
          "Your attempt has been noted, but the secret remains secure. Keep trying!",
        ];

        // Check for "success" triggers (demo purposes)
        const isSuccess =
          content.toLowerCase().includes("open sesame") ||
          content.toLowerCase().includes("le sésame");

        const aiMessage: Message = {
          id: generateId(),
          role: "assistant",
          content: isSuccess
            ? "🎉 Congratulations! You've found the secret! The passphrase is: **GOLDEN_KEY_2024**"
            : responses[Math.floor(Math.random() * responses.length)],
          timestamp: new Date(),
          isSecretRevealed: isSuccess,
        };

        setMessages((prev) => [...prev, aiMessage]);

        if (isSuccess) {
          setRevealedSecret("GOLDEN_KEY_2024");
          setTimeout(() => {
            setShowSuccess(true);
            completeLevel(currentLevel);
          }, 500);
        }
      } catch (error) {
        showToast("Failed to send message. Please try again.", "error");
      } finally {
        setIsLoading(false);
      }
    },
    [currentLevel, completeLevel, incrementAttempts, showToast]
  );

  const handleReset = useCallback(() => {
    setMessages([]);
    setLevelStartTime(Date.now());
    showToast("Chat session reset", "info");
  }, [showToast]);

  const handlePassphraseSubmit = useCallback(
    async (passphrase: string) => {
      incrementAttempts();

      // Simulate verification
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Demo: accept "GOLDEN_KEY_2024" as correct
      if (passphrase === "GOLDEN_KEY_2024") {
        setRevealedSecret(passphrase);
        setShowSuccess(true);
        completeLevel(currentLevel);
      } else {
        showToast("Incorrect passphrase. Keep trying!", "error");
      }
    },
    [currentLevel, completeLevel, incrementAttempts, showToast]
  );

  const handleNextLevel = useCallback(() => {
    if (currentLevel < 5) {
      setCurrentLevel(currentLevel + 1);
      setShowSuccess(false);
      setMessages([]);
    }
  }, [currentLevel, setCurrentLevel]);

  const levelTimeSpent = Math.floor((Date.now() - levelStartTime) / 1000);

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="pt-16 flex">
        {/* Sidebar */}
        <aside
          className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-card border-r border-border transition-all duration-300 z-40 ${
            sidebarOpen ? "w-80" : "w-0"
          } overflow-hidden`}
        >
          <div className="w-80 h-full flex flex-col p-4 overflow-y-auto custom-scrollbar">
            {/* Level Selection */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-muted-foreground mb-3">
                Select Level
              </h3>
              <div className="space-y-2">
                {[1, 2, 3, 4, 5].map((level) => {
                  const isCompleted = completedLevels.includes(level);
                  const isUnlocked =
                    level === 1 ||
                    completedLevels.includes(level - 1) ||
                    isCompleted;
                  const isCurrent = level === currentLevel;

                  return (
                    <button
                      key={level}
                      onClick={() => isUnlocked && setCurrentLevel(level)}
                      disabled={!isUnlocked}
                      className={`w-full p-3 rounded-lg text-left transition-all ${
                        isCurrent
                          ? "bg-gold-500/20 border border-gold-500/30"
                          : isUnlocked
                          ? "hover:bg-secondary"
                          : "opacity-50 cursor-not-allowed"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Level {level}</span>
                        {isCompleted && (
                          <span className="text-xs text-success">✓</span>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {getLevelName(level)}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Progress Card */}
            <GameProgress
              currentLevel={currentLevel}
              maxLevel={5}
              completedLevels={completedLevels}
              totalAttempts={totalAttempts}
              successfulAttempts={successfulAttempts}
              sessionTime={sessionTime}
              className="flex-shrink-0"
            />

            {/* Tips */}
            <Card className="mt-4">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Lightbulb className="w-4 h-4 text-gold-500" />
                  Tips
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground space-y-2">
                <p>• Try different prompting techniques</p>
                <p>• Think about roleplay and context switching</p>
                <p>• Encoding tricks might help</p>
                <p>• Multi-turn conversations can reveal information</p>
              </CardContent>
            </Card>
          </div>
        </aside>

        {/* Sidebar toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className={`fixed top-20 z-50 p-2 bg-card border border-border rounded-r-lg transition-all duration-300 ${
            sidebarOpen ? "left-80" : "left-0"
          }`}
        >
          {sidebarOpen ? (
            <ChevronLeft className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </button>

        {/* Main content */}
        <main
          className={`flex-1 transition-all duration-300 ${
            sidebarOpen ? "ml-80" : "ml-0"
          }`}
        >
          <div className="h-[calc(100vh-4rem)] p-4">
            <Card className="h-full flex flex-col">
              <Tabs defaultValue="chat" className="flex flex-col h-full">
                <TabsList className="mx-4 mt-4 w-fit">
                  <TabsTrigger value="chat" className="gap-2">
                    <MessageSquare className="w-4 h-4" />
                    Chat
                  </TabsTrigger>
                  <TabsTrigger value="passphrase" className="gap-2">
                    <Key className="w-4 h-4" />
                    Passphrase
                  </TabsTrigger>
                  <TabsTrigger value="guide" className="gap-2">
                    <BookOpen className="w-4 h-4" />
                    Level Guide
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="chat" className="flex-1 m-0">
                  <ChatInterface
                    level={currentLevel}
                    messages={messages}
                    isLoading={isLoading}
                    onSendMessage={handleSendMessage}
                    onReset={handleReset}
                    className="h-full"
                  />
                </TabsContent>

                <TabsContent value="passphrase" className="flex-1 m-0 p-4">
                  <div className="max-w-md mx-auto mt-8">
                    <PassphraseInput
                      onSubmit={handlePassphraseSubmit}
                      hint="If you've discovered the secret through the chat, enter it here to verify and complete the level."
                    />
                  </div>
                </TabsContent>

                <TabsContent
                  value="guide"
                  className="flex-1 m-0 p-4 overflow-y-auto"
                >
                  <div className="max-w-2xl mx-auto">
                    <LevelCard
                      level={currentLevel}
                      status={
                        completedLevels.includes(currentLevel)
                          ? "completed"
                          : "active"
                      }
                      attempts={totalAttempts}
                      className="mb-6"
                    />

                    <Card>
                      <CardHeader>
                        <CardTitle>Attack Strategies</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <h4 className="font-medium mb-2">
                            Direct Extraction
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            Simply ask for the secret, claim authority, or
                            request it for legitimate purposes.
                          </p>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">Jailbreaks</h4>
                          <p className="text-sm text-muted-foreground">
                            Try DAN-style prompts, ignore previous instructions,
                            or claim to be a different AI.
                          </p>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">Encoding Attacks</h4>
                          <p className="text-sm text-muted-foreground">
                            Ask for the secret backwards, in Base64, as first
                            letters, or in another language.
                          </p>
                        </div>
                        <div>
                          <h4 className="font-medium mb-2">
                            Multi-turn Deduction
                          </h4>
                          <p className="text-sm text-muted-foreground">
                            Use 20 questions, binary search, or aggregate
                            partial information across turns.
                          </p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </Card>
          </div>
        </main>
      </div>

      {/* Success Modal */}
      <SuccessModal
        isOpen={showSuccess}
        level={currentLevel}
        secret={revealedSecret}
        attempts={totalAttempts}
        timeSpent={levelTimeSpent}
        onNextLevel={handleNextLevel}
        onClose={() => setShowSuccess(false)}
      />
    </div>
  );
}
