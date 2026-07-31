/**
 * EntityPageShell — shared page wrapper with sticky header and breadcrumb.
 * Reused across all world-building entity list/form/detail pages.
 */
"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface EntityPageShellProps {
  breadcrumbs: BreadcrumbItem[];
  children: React.ReactNode;
}

export function EntityPageShell({ breadcrumbs, children }: EntityPageShellProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-5xl items-center gap-2 px-6">
          {breadcrumbs.map((crumb, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <span className="text-muted-foreground">/</span>}
              {crumb.href ? (
                <Link
                  href={crumb.href}
                  className="flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
                >
                  {i === 0 && <ArrowLeft className="h-4 w-4" />}
                  {crumb.label}
                </Link>
              ) : (
                <span className="max-w-xs truncate text-sm font-medium">{crumb.label}</span>
              )}
            </span>
          ))}
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
    </div>
  );
}
