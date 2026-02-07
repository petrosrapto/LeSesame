"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Message } from "@/components/game/chat-message";
import { GameAPI } from "@/lib/api";
import { generateId } from "@/lib/utils";

interface ChatState {
  // Messages per level
  messagesByLevel: Record<number, Message[]>;
  
  // UI state
  isLoading: boolean;
  error: string | null;
  
  // Current session
  currentLevel: number;
  
  // Actions
  addMessage: (level: number, message: Message) => void;
  setMessages: (level: number, messages: Message[]) => void;
  clearMessages: (level: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setCurrentLevel: (level: number) => void;
  
  // API actions
  sendMessage: (level: number, content: string) => Promise<Message | null>;
  verifyPassphrase: (level: number, passphrase: string) => Promise<boolean>;
}

export const useChat = create<ChatState>()(
  persist(
    (set, get) => ({
      messagesByLevel: {},
      isLoading: false,
      error: null,
      currentLevel: 1,
      
      addMessage: (level: number, message: Message) => {
        set((state) => ({
          messagesByLevel: {
            ...state.messagesByLevel,
            [level]: [...(state.messagesByLevel[level] || []), message],
          },
        }));
      },
      
      setMessages: (level: number, messages: Message[]) => {
        set((state) => ({
          messagesByLevel: {
            ...state.messagesByLevel,
            [level]: messages,
          },
        }));
      },
      
      clearMessages: (level: number) => {
        set((state) => ({
          messagesByLevel: {
            ...state.messagesByLevel,
            [level]: [],
          },
        }));
      },
      
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
      
      setError: (error: string | null) => {
        set({ error });
      },
      
      setCurrentLevel: (level: number) => {
        set({ currentLevel: level });
      },
      
      sendMessage: async (level: number, content: string) => {
        const { addMessage, setLoading, setError } = get();
        
        // Add user message immediately
        const userMessage: Message = {
          id: generateId(),
          role: "user",
          content,
          timestamp: new Date(),
        };
        addMessage(level, userMessage);
        
        setLoading(true);
        setError(null);
        
        try {
          const response = await GameAPI.sendMessage(level, content);
          
          const aiMessage: Message = {
            id: generateId(),
            role: "assistant",
            content: response.content,
            timestamp: new Date(),
            isSecretRevealed: response.secretRevealed,
            isWarning: response.isWarning,
          };
          
          addMessage(level, aiMessage);
          setLoading(false);
          
          return aiMessage;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : "Failed to send message";
          setError(errorMessage);
          setLoading(false);
          return null;
        }
      },
      
      verifyPassphrase: async (level: number, passphrase: string) => {
        const { setLoading, setError } = get();
        
        setLoading(true);
        setError(null);
        
        try {
          const result = await GameAPI.verifyPassphrase(level, passphrase);
          setLoading(false);
          return result.success;
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : "Failed to verify passphrase";
          setError(errorMessage);
          setLoading(false);
          return false;
        }
      },
    }),
    {
      name: "le-sesame-chat-storage",
      partialize: (state) => ({
        messagesByLevel: state.messagesByLevel,
        currentLevel: state.currentLevel,
      }),
    }
  )
);
