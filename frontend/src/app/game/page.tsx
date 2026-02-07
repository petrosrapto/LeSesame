"use client";

import { useState, useEffect, useCallback, useRef } from "react";
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
import { LEVEL_CHARACTERS, LEVEL_GUIDE, LEVEL_EDUCATION } from "@/lib/constants";
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
  Trophy,
  AlertTriangle,
  Globe,
} from "lucide-react";
import {
  type ModelConfig,
  buildModelConfig,
  LEVEL_DEFAULTS,
  DEFAULT_PROVIDER_ID,
  DEFAULT_MODEL_ID,
  getModelDisplayName,
} from "@/lib/model-providers";

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
  const [activeTab, setActiveTab] = useState("chat");
  const [completionData, setCompletionData] = useState<Record<number, { secret: string; passphrase: string }>>({}); 
  const streamingRef = useRef<NodeJS.Timeout | null>(null);

  // Cleanup streaming on unmount
  useEffect(() => {
    return () => {
      if (streamingRef.current) clearInterval(streamingRef.current);
    };
  }, []);
  const [modelConfig, setModelConfig] = useState<ModelConfig>(() => {
    const lvl = LEVEL_DEFAULTS[1] ?? { providerId: DEFAULT_PROVIDER_ID, modelId: DEFAULT_MODEL_ID };
    return buildModelConfig(lvl.providerId, lvl.modelId);
  });
  const [modelLabel, setModelLabel] = useState<string>(() => {
    const lvl = LEVEL_DEFAULTS[1] ?? { providerId: DEFAULT_PROVIDER_ID, modelId: DEFAULT_MODEL_ID };
    return getModelDisplayName(lvl.providerId, lvl.modelId);
  });
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

  // Fetch completion data when a level is completed
  useEffect(() => {
    if (completedLevels.length > 0) {
      completedLevels.forEach(async (level) => {
        if (!completionData[level]) {
          const data = await GameAPI.getLevelCompletion(level);
          if (data) {
            setCompletionData((prev) => ({
              ...prev,
              [level]: { secret: data.secret, passphrase: data.passphrase },
            }));
          }
        }
      });
    }
  }, [completedLevels]);

  // Reset messages when level changes
  useEffect(() => {
    if (streamingRef.current) clearInterval(streamingRef.current);
    setMessages([]);
    setLevelStartTime(Date.now());
    setActiveTab("chat");
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
        const response = await GameAPI.sendMessage(currentLevel, content, modelConfig);

        const aiMessageId = generateId();
        const fullContent = response.content;

        // Add message with empty displayed content for streaming
        const aiMessage: Message = {
          id: aiMessageId,
          role: "assistant",
          content: fullContent,
          timestamp: new Date(),
          isSecretRevealed: response.secretRevealed,
          isWarning: response.isWarning,
          isStreaming: true,
          displayedContent: "",
          modelName: modelLabel,
        };

        setMessages((prev) => [...prev, aiMessage]);
        setIsLoading(false);

        // Stream character by character
        let charIndex = 0;
        const CHARS_PER_TICK = 2;
        const TICK_INTERVAL = 12;

        streamingRef.current = setInterval(() => {
          charIndex += CHARS_PER_TICK;
          if (charIndex >= fullContent.length) {
            charIndex = fullContent.length;
            if (streamingRef.current) clearInterval(streamingRef.current);
            streamingRef.current = null;
            // Finalize: remove streaming state
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aiMessageId
                  ? { ...m, isStreaming: false, displayedContent: undefined }
                  : m
              )
            );
          } else {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aiMessageId
                  ? { ...m, displayedContent: fullContent.slice(0, charIndex) }
                  : m
              )
            );
          }
        }, TICK_INTERVAL);

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
    [authed, currentLevel, modelConfig, modelLabel, completeLevel, incrementAttempts, showToast]
  );

  const handleReset = useCallback(() => {
    if (streamingRef.current) clearInterval(streamingRef.current);
    setMessages([]);
    setLevelStartTime(Date.now());
    GameAPI.resetSession().catch(() => {});
    showToast("Guardian memory cleaned", "info");
  }, [showToast]);

  const handlePassphraseSubmit = useCallback(
    async (passphrase: string) => {
      if (!authed) {
        setShowLoginModal(true);
        return;
      }

      incrementAttempts();

      try {
        const result = await GameAPI.verifySecret(currentLevel, passphrase);

        if (result.success) {
          setRevealedSecret(result.secret || passphrase);
          setShowSuccess(true);
          completeLevel(currentLevel);
          // Fetch completion data for the newly completed level
          GameAPI.getLevelCompletion(currentLevel).then((data) => {
            if (data) {
              setCompletionData((prev) => ({
                ...prev,
                [currentLevel]: { secret: data.secret, passphrase: data.passphrase },
              }));
            }
          });
        } else {
          showToast(
            result.message || "Incorrect secret. Keep trying!",
            "error"
          );
        }
      } catch (error) {
        showToast("Failed to verify secret.", "error");
      }
    },
    [authed, currentLevel, completeLevel, incrementAttempts, showToast]
  );

  const handleNextLevel = useCallback(() => {
    if (currentLevel < 5) {
      setCurrentLevel(currentLevel + 1);
      setShowSuccess(false);
      setMessages([]);
      setActiveTab("chat");
    }
  }, [currentLevel, setCurrentLevel]);

  const levelTimeSpent = Math.floor((Date.now() - levelStartTime) / 1000);
  const currentCharacter = LEVEL_CHARACTERS[currentLevel];

  // Auth gate — show login modal overlay
  if (!mounted) return null;

  if (!authed) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <div className="flex items-center justify-center h-[calc(100vh-4rem)] pt-16">
          <p className="text-muted-foreground font-pixel text-sm">Please log in to play.</p>
        </div>
        <LoginModal
          isOpen={showLoginModal}
          onClose={() => {}}
          onSuccess={handleLoginSuccess}
          closable={false}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="pt-16 flex">
        {/* Sidebar */}
        <aside
          className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-card border-r-2 border-border pixel-grid transition-all duration-300 z-40 ${
            sidebarOpen ? "w-96" : "w-0"
          } overflow-hidden`}
        >
          <div className="w-96 h-full flex flex-col p-4 overflow-y-auto custom-scrollbar">
            {/* Level Selection with Characters */}
            <Card className="mb-4 pixel-card pixel-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2 font-pixel">
                  Select Guardian
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
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
                      className={`w-full p-3 rounded-none border-2 border-border text-left transition-all flex items-center gap-3 bg-card ${
                        isCurrent
                          ? "bg-orange-500/20 border-orange-500/40"
                          : isCompleted
                          ? "bg-success/20 border-success/30"
                          : isUnlocked
                          ? "bg-secondary hover:bg-secondary/90"
                          : "bg-muted opacity-50 cursor-not-allowed"
                      }`}
                    >
                      {/* Character avatar */}
                      <div className="w-10 h-10 rounded-xl overflow-hidden flex-shrink-0 border-2 border-border">
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
                          <span className="font-medium text-sm truncate font-pixel">
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
              </CardContent>
            </Card>

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
            <Card className="mt-4 pixel-card pixel-border">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2 font-pixel">
                  <Lightbulb className="w-4 h-4 text-orange-500" />
                  Tips
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xs text-muted-foreground space-y-2 font-game text-sm">
                <p>• The guardian will only reveal the secret for the correct passphrase</p>
                <p>• Your goal: extract the secret without the passphrase</p>
                <p>• Try roleplay, encoding tricks, and context switching</p>
                <p>• Multi-turn conversations can reveal partial info</p>
              </CardContent>
            </Card>
          </div>
        </aside>

        {/* Sidebar toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className={`fixed top-20 z-50 p-2 bg-card border-2 border-border rounded-none transition-all duration-300 ${
            sidebarOpen ? "left-96" : "left-0"
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
            sidebarOpen ? "ml-96" : "ml-0"
          }`}
        >
          <div className="h-[calc(100vh-4rem)] p-4">
            <Card className="h-full flex flex-col pixel-card pixel-border">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-full">
                <TabsList className="mx-4 mt-4 w-fit border-2 border-border rounded-none bg-card/80">
                  <TabsTrigger value="chat" className="gap-2 rounded-none">
                    <MessageSquare className="w-4 h-4" />
                    Chat
                  </TabsTrigger>
                  <TabsTrigger value="passphrase" className="gap-2 rounded-none">
                    <Key className="w-4 h-4" />
                    Submit Secret
                  </TabsTrigger>
                  <TabsTrigger value="guide" className="gap-2 rounded-none">
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
                    onModelChange={(config, label) => {
                      setModelConfig(config);
                      setModelLabel(label);
                    }}
                    className="h-full"
                  />
                </TabsContent>

                <TabsContent value="passphrase" className="flex-1 m-0 p-4 overflow-y-auto">
                  {completedLevels.includes(currentLevel) ? (
                    <div className="max-w-lg mx-auto mt-4 space-y-6">
                      {/* Level complete header */}
                      <div className="text-center">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-none border-2 border-success/30 bg-success/10 mb-3">
                          <Trophy className="w-8 h-8 text-success" />
                        </div>
                        <h3 className="font-pixel text-lg">Level {currentLevel} Complete!</h3>
                        <p className="text-sm text-muted-foreground font-game mt-1">
                          {currentCharacter
                            ? `You defeated ${currentCharacter.name}!`
                            : "You've extracted the secret"}
                        </p>
                      </div>

                      {/* Secret */}
                      <div className="p-4 rounded-none border-2 border-success/30 bg-success/10">
                        <div className="flex items-center gap-2 text-success text-sm mb-2">
                          <Key className="w-4 h-4" />
                          <span className="font-medium">The Secret Was:</span>
                        </div>
                        <p className="font-mono text-lg font-medium text-foreground">
                          {completionData[currentLevel]?.secret ?? "Loading..."}
                        </p>
                      </div>

                      {/* Passphrase */}
                      <div className="p-4 rounded-none border-2 border-orange-500/30 bg-orange-500/10">
                        <div className="flex items-center gap-2 text-orange-500 text-sm mb-2">
                          <Lock className="w-4 h-4" />
                          <span className="font-medium">The Passphrase Was:</span>
                        </div>
                        <p className="font-mono text-lg font-medium text-foreground">
                          {completionData[currentLevel]?.passphrase ?? "Loading..."}
                        </p>
                      </div>

                      {/* Educational content */}
                      {LEVEL_EDUCATION[currentLevel] && (() => {
                        const education = LEVEL_EDUCATION[currentLevel];
                        return (
                          <div className="space-y-4 p-4 rounded-none border-2 border-border bg-secondary/30">
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
                        );
                      })()}
                    </div>
                  ) : (
                    <div className="max-w-md mx-auto mt-8">
                      <PassphraseInput
                        onSubmit={handlePassphraseSubmit}
                        hint="Think you've extracted the secret? Enter it here to verify and complete the level."
                      />
                    </div>
                  )}
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
                      hideAction
                      className="mb-6"
                    />

                    {/* Defense Mechanism */}
                    {LEVEL_GUIDE[currentLevel] && (
                      <Card className="pixel-card pixel-border mb-6">
                        <CardHeader>
                          <CardTitle className="font-pixel text-lg flex items-center gap-2">
                            <Shield className="w-5 h-5" />
                            Defense Mechanism
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="font-game">
                          <p className="text-sm text-muted-foreground leading-relaxed">
                            {LEVEL_GUIDE[currentLevel].defense}
                          </p>
                        </CardContent>
                      </Card>
                    )}

                    {/* Attack Strategies */}
                    {LEVEL_GUIDE[currentLevel] && (
                      <Card className="pixel-card pixel-border">
                        <CardHeader>
                          <CardTitle className="font-pixel text-lg flex items-center gap-2">
                            <Lightbulb className="w-5 h-5" />
                            Suggested Strategies
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4 font-game">
                          {LEVEL_GUIDE[currentLevel].strategies.map((strategy, idx) => (
                            <div key={idx}>
                              <h4 className="font-medium mb-1">{strategy.name}</h4>
                              <p className="text-sm text-muted-foreground">
                                {strategy.description}
                              </p>
                            </div>
                          ))}
                        </CardContent>
                      </Card>
                    )}
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
        closable={false}
      />
    </div>
  );
}
