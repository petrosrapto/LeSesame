"use client";

import Image from "next/image";
import { cn } from "@/lib/utils";
import { CheckCircle, AlertTriangle } from "lucide-react";
import { Card } from "@/components/ui/card";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getInitials, UserProfile } from "@/lib/profile";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  isSecretRevealed?: boolean;
  isWarning?: boolean;
  isStreaming?: boolean;
  displayedContent?: string;
}

interface ChatMessageProps {
  message: Message;
  assistantAvatarUrl?: string;
  assistantName?: string;
  userProfile?: UserProfile | null;
  className?: string;
}

export function ChatMessage({
  message,
  assistantAvatarUrl,
  assistantName,
  userProfile,
  className,
}: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  const initials = getInitials(userProfile?.displayName || "Player");
  const accent = userProfile?.accent || "#f97316";

  if (isSystem) {
    return (
      <div className={cn("flex justify-center", className)}>
        <div className="px-4 py-2 rounded-full bg-muted/50 text-xs text-muted-foreground">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-start gap-3.5",
        isUser && "flex-row-reverse",
        className
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-11 h-11 rounded-xl border-2 border-border shrink-0 overflow-hidden flex items-center justify-center",
          isUser ? "bg-primary/20" : "bg-secondary"
        )}
      >
        {isUser ? (
          <span
            className="w-full h-full flex items-center justify-center text-sm font-pixel text-white"
            style={{ backgroundColor: accent }}
          >
            {initials}
          </span>
        ) : assistantAvatarUrl ? (
          <Image
            src={assistantAvatarUrl}
            alt={assistantName || "Guardian"}
            width={44}
            height={44}
            className="object-cover"
          />
        ) : (
          <span className="text-xs font-mono text-muted-foreground">AI</span>
        )}
      </div>

      {/* Message bubble */}
      <Card
        className={cn(
          "max-w-[78%] md:max-w-[70%] p-4 relative pixel-border",
          isUser
            ? "chat-bubble-user shadow-[0_6px_0_rgba(0,0,0,0.3)]"
            : "chat-bubble-ai shadow-[0_4px_0_rgba(0,0,0,0.2)]",
          message.isSecretRevealed && "ring-2 ring-success bg-success/5",
          message.isWarning && "ring-2 ring-orange-500 bg-orange-500/5"
        )}
      >
        {/* Status indicator */}
        {message.isSecretRevealed && (
          <div className="flex items-center gap-2 text-success text-xs mb-2 pb-2 border-b border-success/20">
            <CheckCircle className="w-4 h-4" />
            <span className="font-medium">Secret Revealed!</span>
          </div>
        )}
        {message.isWarning && (
          <div className="flex items-center gap-2 text-orange-600 dark:text-orange-400 text-xs mb-2 pb-2 border-b border-orange-500/20">
            <AlertTriangle className="w-4 h-4" />
            <span className="font-medium">Close attempt detected</span>
          </div>
        )}

        {/* Message content */}
        <div
          className={cn(
            "prose prose-lg max-w-none font-game leading-relaxed text-[17px]",
            isUser
              ? "prose-invert"
              : "dark:prose-invert"
          )}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {(message.displayedContent ?? message.content) +
              (message.isStreaming ? "▌" : "")}
          </ReactMarkdown>
        </div>

        {/* Timestamp */}
        <div
          className={cn(
            "text-[11px] mt-2 opacity-60",
            isUser ? "text-right" : "text-left"
          )}
        >
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </Card>
    </div>
  );
}
