"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import AIChat from "@/components/ui/ai-chat";
import FloatingChatButton from "./floating-chat-button";

interface Message {
  id: string;
  sender: "ai" | "user";
  text: string;
  timestamp: string;
}

interface ChatContainerProps {
  showFloatingButton?: boolean;
}

export default function ChatContainer({
  showFloatingButton = true,
}: ChatContainerProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [mode, setMode] = useState<"normal" | "admin">("normal");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "ai",
      text: "👋 Привет! Я AI-помощник. Чем могу помочь?",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const handleSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await fetch("/api/chat/message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
          mode,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      const aiMessage: Message = {
        id: Date.now().toString() + "-ai",
        sender: "ai",
        text: data.message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setSessionId(data.session_id);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: Date.now().toString() + "-error",
        sender: "ai",
        text: "Извините, произошла ошибка. Попробуйте позже.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const toggleMode = () => {
    setMode((prev) => (prev === "normal" ? "admin" : "normal"));
  };

  return (
    <>
      {showFloatingButton && (
        <FloatingChatButton
          isExpanded={isExpanded}
          onClick={() => setIsExpanded(!isExpanded)}
        />
      )}

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.3 }}
            className="fixed bottom-20 right-4 z-40 w-[360px] h-[500px] md:w-[400px] md:h-[600px]"
          >
            <div className="relative w-full h-full">
              {/* Mode Toggle */}
              <div className="absolute -top-10 right-0 z-50">
                <button
                  onClick={toggleMode}
                  className="px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-white text-xs font-medium hover:bg-white/20 transition-colors"
                >
                  {mode === "normal" ? "Switch to Admin" : "Switch to Normal"}
                </button>
              </div>

              <AIChat
                mode={mode}
                messages={messages}
                isTyping={isTyping}
                onSendMessage={handleSendMessage}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

