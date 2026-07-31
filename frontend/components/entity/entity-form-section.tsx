/**
 * EntityFormSection — a labelled section group inside a multi-section form.
 * Reusable wrapper used by Character, Location, Organization forms.
 */
"use client";

import { cn } from "@/lib/utils";

interface EntityFormSectionProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function EntityFormSection({
  title,
  description,
  children,
  className,
}: EntityFormSectionProps) {
  return (
    <section className={cn("space-y-4", className)}>
      <div className="border-b border-border pb-2">
        <h2 className="text-base font-semibold">{title}</h2>
        {description && <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>}
      </div>
      <div className="space-y-4">{children}</div>
    </section>
  );
}
