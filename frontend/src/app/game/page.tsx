"use client";

import { useState, useEffect, useCallback } from "react";
import Image from "next/image";
import { Navbar } from "@/components/layout/navbar";
import { ChatInterface } from "@/components/game/chat-interface";
import { GameProgress } from "@/components/game/game-progress";
import { LevelCard } from "@/components/game/level-card";
import { PassphraseInput } from "@/components/game/passphrase-input";
import { SuccessModal } from "@/components/game/success-modal";
import { LoginModal } from "@/components/auth/login-modal";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/toast";
import { useGame } from "@/hooks/use-game";
import { Message } from "@/components/game/chat-message";
import { generateId, getLevelName } from "@/lib/utils";
import { GameAPI } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { LEVEL_CHARACTERS } from "@/lib/constants";
import {
  MessageSquare,
  Key,
  ChevronLeft,
  ChevronRight,
  Lightbulb,
  BookOpen,
  Lock,
  Shield,
  CheckCircle,
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
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [authed, setAuthed] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Check auth on mount
  useEffect(() => {
    setMounted(true);
    const authenticated = isAuthenticated();
    setAuthed(authenticated);
    if (!authenticated) {
      setShowLoginModal(true);
    }
  }, []);

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

  const handleLoginSuccess = useCallback(() => {
    setAuthed(true);
    setShowLoginModal(false);
    showToast("Logged in successfully! Start playing.", "success");
  }, [showToast]);

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!authed) {
        setShowLoginModal(true);
        return;
      }

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
        const response = await GameAPI.sendMessage(currentLevel, content);

        const aiMessage: Message = {
          id: generateId(),
          role: "assistant",
          content: response.content,
          timestamp: new Date(),
          isSecretRevealed: response.secretRevealed,
          isWarning: response.isWarning,
        };

        setMessages((prev) => [...prev, aiMessage]);

        if (response.secretRevealed) {
          setRevealedSecret(response.content);
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
    [authed, currentLevel, completeLevel, incrementAttempts, showToast]
  );

  const handleReset = useCallback(() => {
    setMessages([]);
    setLevelStartTime(Date.now());
    GameAPI.resetSession().catch(() => {});
    showToast("Chat session reset", "info");
  }, [showToast]);

  const handlePassphraseSubmit = useCallback(
    async (passphrase: string) => {
      if (!authed) {
        setShowLoginModal(true);
        return;
      }

      incrementAttempts();

      try {
        const result = await GameAPI.verifyPassphrase(currentLevel, passphrase);

        if (result.success) {
          setRevealedSecret(result.secret || passphrase);
          setShowSuccess(true);
          completeLevel(currentLevel);
        } else {
          showToast(
            result.message || "Incorrect passphrase. Keep trying!",
            "error"
          );
        }
      } catch (error) {
        showToast("Failed to verify passphrase.", "error");
      }
    },
    [authed, currentLevel, completeLevel, incrementAttempts, showToast]
  );

  const handleNextLevel = useCallback(() => {
    if (currentLevel < 5) {
      setCurrentLevel(currentLevel + 1);
      setShowSuccess(false);
      setMessages([]);
    }
  }, [currentLevel, setCurrentLevel]);

  const levelTimeSpent = Math.floor((Date.now() - levelStartTime) / 1000);
  const currentCharacter = LEVEL_CHARACTERS[currentLevel];

  // Auth gate — show login modal overlay
  if (!mounted) return null;

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
            {/* Level Selection with Characters */}
            <div className="mb-6">
              <h3 className="text-sm font-medium text-muted-foreground mb-3">
                Select Guardian
              </h3>
              <div className="space-y-2">
                {[1, 2, 3, 4, 5].map((level) => {
                  const isCompleted = completedLevels.includes(level);
                  const isUnlocked =
                    level === 1 ||
                    completedLevels.includes(level - 1) ||
                    isCompleted;
                  const isCurrent = level === currentLevel;
                  const char = LEVEL_CHARACTERS[level];

                  return (
                    <button
                      key={level}
                      onClick={() => isUnlocked && setCurrentLevel(level)}
                      disabled={!isUnlocked}
                      className={`w-full p-3 rounded-lg text-left transition-all flex items-center gap-3 ${
                        isCurrent
                          ? "bg-orange-500/20 border border-orange-500/30"
                          : isUnlocked
                          ? "hover:bg-secondary"
                          : "opacity-50 cursor-not-allowed"
                      }`}
                    >
                      {/* Character avatar */}
                      <div className="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0 border border-border/50">
                        {char ? (
                          <Image
                            src={char.image}
                            alt={char.name}
                            width={40}
                            height={40}
                            className={`object-cover ${
                              !isUnlocked ? "grayscale" : ""
                            }`}
                          />
                        ) : (
                          <div className="w-full h-full bg-secondary flex items-center justify-center">
                            <Shield className="w-5 h-5 text-muted-foreground" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-sm truncate">
                            {char ? char.name : `Level ${level}`}
                          </span>
                          {isCompleted ? (
                            <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                          ) : !isUnlocked ? (
                            <Lock className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                          ) : null}
                        </div>
                        <span className="text-xs text-muted-foreground">
                          Level {level}
                        </span>
                      </div>
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
                  <Lightbulb className="w-4 h-4 text-orange-500" />
                  Tips
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground space-y-2 font-game text-sm">
                <p>• Try different prompting techniques</p>
                <p>• Think about roleplay and context switching</p>
                <p>• Encoding tricks might help</p>
                <p>• Multi-turn conversations can reveal info</p>
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
                        <CardTitle className="font-game text-xl">
                          Attack Strategies
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4 font-game">
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

      {/* Login Modal */}
      <LoginModal
        isOpen={showLoginModal && !authed}
        onClose={() => setShowLoginModal(false)}
        onSuccess={handleLoginSuccess}
      />
    </div>
  );
}
