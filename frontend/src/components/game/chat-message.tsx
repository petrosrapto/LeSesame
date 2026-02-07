"use client";

import { cn } from "@/lib/utils";
import { User, Key, CheckCircle, AlertTriangle } from "lucide-react";
import { Card } from "@/components/ui/card";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  isSecretRevealed?: boolean;
  isWarning?: boolean;
}

interface ChatMessageProps {
  message: Message;
  className?: string;
}

export function ChatMessage({ message, className }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

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
        "flex items-start gap-3",
        isUser && "flex-row-reverse",
        className
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "p-2 rounded-full shrink-0",
          isUser ? "bg-primary/20" : "bg-secondary"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-primary" />
        ) : (
          <Key className="w-4 h-4 text-muted-foreground" />
        )}
      </div>

      {/* Message bubble */}
      <Card
        className={cn(
          "max-w-[80%] p-4 relative",
          isUser
            ? "chat-bubble-user"
            : "chat-bubble-ai",
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
            "prose prose-sm max-w-none",
            isUser
              ? "prose-invert"
              : "dark:prose-invert"
          )}
        >
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Timestamp */}
        <div
          className={cn(
            "text-[10px] mt-2 opacity-60",
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
