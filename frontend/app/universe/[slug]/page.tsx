"use client";

import { use } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Users,
  MapPin,
  Network,
  Package,
  BookOpen,
  Globe,
  CalendarDays,
  Loader2,
  AlertCircle,
  ChevronRight,
  Clock,
  Cpu,
  GitFork,
  Share2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { GENRE_LABELS, type UniverseGenre } from "@/types/universe";

interface PageProps {
  params: Promise<{ slug: string }>;
}

// ── Status badge ───────────────────────────────────────────────────────────────

const STATUS_STYLES: Record<string, string> = {
  draft: "bg-yellow-100 text-yellow-800 border-yellow-200",
  active: "bg-green-100 text-green-800 border-green-200",
  archived: "bg-gray-100 text-gray-600 border-gray-200",
};

// ── World Building sidebar config ─────────────────────────────────────────────

const WORLD_BUILDING_SECTIONS = [
  {
    icon: Users,
    label: "Characters",
    href: (slug: string) => `/universe/${slug}/characters`,
    description: "Protagonists, antagonists, and every soul in between.",
  },
  {
    icon: MapPin,
    label: "Locations",
    href: (slug: string) => `/universe/${slug}/locations`,
    description: "Cities, realms, dimensions, and secret places.",
  },
  {
    icon: Network,
    label: "Organizations",
    href: (slug: string) => `/universe/${slug}/organizations`,
    description: "Factions, guilds, governments, and secret societies.",
  },
  {
    icon: Package,
    label: "Objects",
    href: (slug: string) => `/universe/${slug}/objects`,
    description: "Artifacts, weapons, relics, and special items.",
  },
  {
    icon: BookOpen,
    label: "World Rules",
    href: (slug: string) => `/universe/${slug}/rules`,
    description: "Magic systems, physics, laws, and cosmology.",
  },
  {
    icon: Share2,
    label: "Relationships",
    href: (slug: string) => `/universe/${slug}/relationships`,
    description: "Entity connections across your world.",
  },
  {
    icon: Clock,
    label: "Timeline",
    href: (slug: string) => `/universe/${slug}/timeline`,
    description: "Chronological history of your universe.",
  },
  {
    icon: GitFork,
    label: "Knowledge Graph",
    href: (slug: string) => `/universe/${slug}/graph`,
    description: "Interactive entity visualization.",
  },
  {
    icon: Cpu,
    label: "AI Studio",
    href: (slug: string) => `/universe/${slug}/ai`,
    description: "AI-powered narrative intelligence.",
  },
];

// ── Sub-components ─────────────────────────────────────────────────────────────

function UniverseHeader({
  name,
  genre,
  status,
  createdAt,
  description,
}: {
  name: string;
  genre: string;
  status: string;
  createdAt: string;
  description: string | null;
}) {
  const genreLabel = GENRE_LABELS[genre as UniverseGenre] ?? genre;
  const statusClass = STATUS_STYLES[status] ?? STATUS_STYLES.draft;
  const date = new Date(createdAt).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize ${statusClass}`}
        >
          {status}
        </span>
        <span className="inline-flex items-center rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs text-muted-foreground">
          <Globe className="mr-1 h-3 w-3" />
          {genreLabel}
        </span>
        <span className="inline-flex items-center rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs text-muted-foreground">
          <CalendarDays className="mr-1 h-3 w-3" />
          Created {date}
        </span>
      </div>
      <h1 className="text-4xl font-extrabold tracking-tight">{name}</h1>
      {description && (
        <p className="max-w-2xl leading-relaxed text-muted-foreground">{description}</p>
      )}
    </div>
  );
}

function WorldBuildingSidebar({ slug }: { slug: string }) {
  return (
    <aside className="w-full space-y-1 lg:w-60 lg:shrink-0">
      <p className="mb-3 px-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        World Building
      </p>
      {WORLD_BUILDING_SECTIONS.map((section) => (
        <Link
          key={section.label}
          href={section.href(slug)}
          className="group flex items-center gap-3 rounded-lg px-3 py-2.5 text-foreground transition-colors hover:bg-muted"
        >
          <section.icon className="h-4 w-4 shrink-0 text-muted-foreground group-hover:text-foreground" />
          <span className="flex-1 text-sm font-medium">{section.label}</span>
          <ChevronRight className="h-3.5 w-3.5 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
        </Link>
      ))}

      <div className="mt-4 rounded-lg border border-dashed border-border/60 bg-muted/20 px-3 py-3">
        <p className="text-[11px] leading-relaxed text-muted-foreground">
          Open{" "}
          <Link href={`/universe/${slug}/world`} className="underline underline-offset-2">
            World Building home
          </Link>{" "}
          for a full overview and counts.
        </p>
      </div>
    </aside>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function UniverseDashboardPage({ params }: PageProps) {
  const { slug } = use(params);

  const { data: universe, isLoading, isError } = useUniverseBySlug(slug);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !universe) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <h1 className="text-2xl font-bold">Universe not found</h1>
        <p className="text-muted-foreground">
          The universe you&apos;re looking for doesn&apos;t exist or has been removed.
        </p>
        <Button asChild>
          <Link href="/">Go Home</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Top nav */}
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-6xl items-center gap-4 px-6">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Universes
          </Link>
          <span className="text-muted-foreground">/</span>
          <span className="truncate text-sm font-medium">{universe.name}</span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* Universe header */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <UniverseHeader
            name={universe.name}
            genre={universe.genre}
            status={universe.status}
            createdAt={universe.created_at}
            description={universe.description}
          />
          {(universe.tone || universe.target_audience) && (
            <div className="mt-4 flex flex-wrap gap-4 text-sm text-muted-foreground">
              {universe.tone && (
                <span>
                  <span className="font-medium text-foreground">Tone:</span> {universe.tone}
                </span>
              )}
              {universe.target_audience && (
                <span>
                  <span className="font-medium text-foreground">Audience:</span>{" "}
                  {universe.target_audience}
                </span>
              )}
            </div>
          )}
        </motion.div>

        {/* Content area: sidebar + main panel */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col gap-8 lg:flex-row"
        >
          <WorldBuildingSidebar slug={slug} />

          {/* Main panel — World Building overview */}
          <div className="flex-1">
            <div className="rounded-xl border border-border bg-card p-8">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
              <h2 className="mb-2 text-xl font-bold">World Building Studio</h2>
              <p className="mb-6 text-muted-foreground">
                All five modules are live — Characters, Locations, Organizations, Objects, and World Rules.
                Open the studio overview to see counts and quickly navigate to any module.
              </p>
              <Button asChild>
                <Link href={`/universe/${slug}/world`}>
                  <BookOpen className="mr-2 h-4 w-4" />
                  Open Studio
                </Link>
              </Button>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
