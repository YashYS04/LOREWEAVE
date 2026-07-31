/**
 * EntityHeader — page header for entity list and detail pages.
 * Displays title, optional subtitle, a primary action button, and breadcrumb.
 */
"use client";

interface EntityHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function EntityHeader({ title, subtitle, action }: EntityHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="space-y-1">
        <h1 className="text-3xl font-extrabold tracking-tight">{title}</h1>
        {subtitle && <p className="text-muted-foreground">{subtitle}</p>}
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
