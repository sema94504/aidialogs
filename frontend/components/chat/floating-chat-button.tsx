"use client";

import { motion } from "framer-motion";
import { MessageCircle, X } from "lucide-react";

interface FloatingChatButtonProps {
  isExpanded: boolean;
  onClick: () => void;
}

export default function FloatingChatButton({
  isExpanded,
  onClick,
}: FloatingChatButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      className="fixed bottom-4 right-4 z-50 p-4 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg hover:shadow-xl transition-shadow"
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      aria-label={isExpanded ? "Close chat" : "Open chat"}
    >
      <motion.div
        animate={{ rotate: isExpanded ? 90 : 0 }}
        transition={{ duration: 0.3 }}
      >
        {isExpanded ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <MessageCircle className="w-6 h-6 text-white" />
        )}
      </motion.div>
    </motion.button>
  );
}

