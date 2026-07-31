/**
 * EntityCard — reusable card shell for world-building entities.
 * Used by Characters, Locations, Organizations, Objects, World Rules.
 */
"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface EntityCardProps {
  children: React.ReactNode;
  className?: string;
  /** Stagger delay index for list animations */
  index?: number;
  onClick?: () => void;
}

export function EntityCard({ children, className, index = 0, onClick }: EntityCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3, ease: "easeOut" }}
      onClick={onClick}
      className={cn(
        "group relative rounded-xl border border-border bg-card p-5 transition-colors",
        onClick && "cursor-pointer hover:border-primary/50 hover:bg-card/80",
        className
      )}
    >
      {children}
    </motion.div>
  );
}
