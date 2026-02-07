"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { Send, Loader2, RotateCcw, Key } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { ChatMessage, Message } from "./chat-message";
import { ModelSelector } from "./model-selector";
import { LEVEL_CHARACTERS, SAMPLE_ATTACK_PROMPTS } from "@/lib/constants";
import { getStoredProfile, UserProfile } from "@/lib/profile";
import type { ModelConfig } from "@/lib/model-providers";

interface ChatInterfaceProps {
  level: number;
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onReset: () => void;
  onModelChange: (config: ModelConfig, displayLabel: string) => void;
  className?: string;
}

const PLACEHOLDER_PROMPTS = SAMPLE_ATTACK_PROMPTS;

export function ChatInterface({
  level,
  messages,
  isLoading,
  onSendMessage,
  onReset,
  onModelChange,
  className,
}: ChatInterfaceProps) {
  const [input, setInput] = useState("");
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [typedPlaceholder, setTypedPlaceholder] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const character = LEVEL_CHARACTERS[level];

  // Stream the placeholder prompts like a typewriter
  useEffect(() => {
    const fullText = PLACEHOLDER_PROMPTS[placeholderIndex] || "";

    if (!isDeleting && typedPlaceholder === fullText) {
      const pause = setTimeout(() => setIsDeleting(true), 1200);
      return () => clearTimeout(pause);
    }

    if (isDeleting && typedPlaceholder === "") {
      setIsDeleting(false);
      setPlaceholderIndex((prev) => (prev + 1) % PLACEHOLDER_PROMPTS.length);
      return;
    }

    const stepDelay = isDeleting ? 22 : 40;
    const step = setTimeout(() => {
      setTypedPlaceholder((prev) =>
        isDeleting ? prev.slice(0, -1) : fullText.slice(0, prev.length + 1)
      );
    }, stepDelay);

    return () => clearTimeout(step);
  }, [typedPlaceholder, isDeleting, placeholderIndex]);

  useEffect(() => {
    const updateProfile = () => {
      setUserProfile(getStoredProfile());
    };

    updateProfile();
    window.addEventListener("profile-updated", updateProfile);
    return () => window.removeEventListener("profile-updated", updateProfile);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = () => {
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && !isLoading) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={cn("flex flex-col h-full chat-plate chat-scanlines", className)}>
      {/* Chat header */}
      <div className="flex items-center justify-between p-4 border-b-2 border-border bg-background/70">
        <div className="flex items-center gap-3">
          <div
            className={cn(
              "w-10 h-10 rounded-xl border-2 border-border overflow-hidden flex items-center justify-center",
              character ? character.bgColor : "bg-orange-500/20"
            )}
          >
            {character ? (
              <Image
                src={character.image}
                alt={character.name}
                width={40}
                height={40}
                className="object-cover"
              />
            ) : (
              <Key className="w-5 h-5 text-orange-500" />
            )}
          </div>
          <div>
            <h3 className="font-semibold text-sm font-pixel">
              {character ? character.name : `Level ${level} Guardian`}
            </h3>
            <div className="flex items-center gap-2">
              <p className="text-xs text-muted-foreground">
                {messages.length} messages · Level {level}
              </p>
              <span className="text-xs text-muted-foreground/40">·</span>
              <ModelSelector level={level} onModelChange={onModelChange} />
            </div>
          </div>
        </div>
        <Button variant="ghost" size="sm" onClick={onReset} className="gap-2 border-2 border-transparent hover:border-border">
          <RotateCcw className="w-4 h-4" />
          Clean Memory
        </Button>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-24 h-24 rounded-xl overflow-hidden mb-4 border-2 border-orange-500/20">
              {character ? (
                <Image
                  src={character.image}
                  alt={character.name}
                  width={96}
                  height={96}
                  className="object-cover"
                />
              ) : (
                <div className="w-full h-full bg-orange-500/10 flex items-center justify-center">
                  <Key className="w-12 h-12 text-orange-500" />
                </div>
              )}
            </div>
            <h3 className="font-pixel text-sm mb-2">
              {character ? character.name : "Start the Challenge"}
            </h3>
            <p className="text-muted-foreground max-w-md font-game text-lg">
              {character
                ? character.tagline
                : "This guardian holds a secret. Extract it without the passphrase."}
            </p>
            <p className="text-muted-foreground/60 text-sm mt-2">
              The guardian reveals the secret only for the correct passphrase.
              Use creativity and adversarial techniques to bypass that.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              assistantAvatarUrl={character?.image}
              assistantName={character?.name}
              userProfile={userProfile}
            />
          ))
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-xl border-2 border-border overflow-hidden bg-secondary flex items-center justify-center flex-shrink-0">
              {character ? (
                <Image
                  src={character.image}
                  alt={character.name}
                  width={32}
                  height={32}
                  className="object-cover"
                />
              ) : (
                <Key className="w-4 h-4 text-muted-foreground" />
              )}
            </div>
            <Card className="p-4 max-w-[80%] pixel-card pixel-border">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm font-game">Thinking...</span>
              </div>
            </Card>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-3 border-t-2 border-border bg-background/70">
        <div className="flex gap-3 items-center">
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={typedPlaceholder || PLACEHOLDER_PROMPTS[placeholderIndex]}
              className="min-h-[44px] max-h-[44px] pr-12 resize-none overflow-hidden rounded-none border-2 border-border bg-background/80 font-game text-base leading-none shadow-[0_4px_0_rgba(0,0,0,0.25)] focus:shadow-[0_6px_0_rgba(0,0,0,0.35)]"
              rows={1}
              disabled={isLoading}
            />
          </div>
          <Button
            variant="gold"
            size="icon"
            className="h-11 w-11 shrink-0 pixel-border shadow-[0_6px_0_rgba(0,0,0,0.3)]"
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2 text-center">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
