/**
 * EntityEmptyState — shown when a resource list is empty.
 * Reusable across Characters, Locations, Organizations, etc.
 */
"use client";

import { type LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EntityEmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EntityEmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
}: EntityEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-muted/20 px-6 py-16 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-muted">
        <Icon className="h-6 w-6 text-muted-foreground" />
      </div>
      <h3 className="mb-1 text-lg font-semibold">{title}</h3>
      <p className="mb-6 max-w-xs text-sm leading-relaxed text-muted-foreground">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
