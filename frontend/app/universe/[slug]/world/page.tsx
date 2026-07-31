"use client";

import { use, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Users,
  MapPin,
  Network,
  Package,
  BookOpen,
  Share2,
  GitFork,
  Clock,
  Plus,
  Loader2,
  AlertCircle,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityPageShell, GenerateStarterWorldDialog } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { useCharacters } from "@/hooks/use-characters";
import { useLocations } from "@/hooks/use-locations";
import { useOrganizations } from "@/hooks/use-organizations";
import { useWorldObjects } from "@/hooks/use-world-objects";
import { useWorldRules } from "@/hooks/use-world-rules";
import { useRelationships } from "@/hooks/use-relationships";
import { useTimelineEvents } from "@/hooks/use-timeline";

interface PageProps {
  params: Promise<{ slug: string }>;
}

interface StudioCardProps {
  icon: React.ElementType;
  title: string;
  description: string;
  count: number | undefined;
  href: string;
  newHref: string;
  isLoading: boolean;
  index: number;
}

function StudioCard({
  icon: Icon,
  title,
  description,
  count,
  href,
  newHref,
  isLoading,
  index,
}: StudioCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07, duration: 0.3 }}
      className="flex flex-col rounded-xl border border-border bg-card p-6"
    >
      <div className="mb-4 flex items-start justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
          <Icon className="h-5 w-5 text-primary" />
        </div>
        <span className="text-2xl font-bold tabular-nums text-foreground">
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          ) : (
            (count ?? 0)
          )}
        </span>
      </div>

      <h3 className="mb-1 font-semibold">{title}</h3>
      <p className="mb-6 flex-1 text-sm leading-relaxed text-muted-foreground">{description}</p>

      <div className="flex gap-2">
        <Button variant="outline" size="sm" asChild className="flex-1">
          <Link href={href}>
            <ArrowRight className="mr-1.5 h-3.5 w-3.5" />
            Open
          </Link>
        </Button>
        <Button size="sm" asChild>
          <Link href={newHref}>
            <Plus className="mr-1.5 h-3.5 w-3.5" />
            New
          </Link>
        </Button>
      </div>
    </motion.div>
  );
}

export default function WorldBuildingHomePage({ params }: PageProps) {
  const { slug } = use(params);
  const [showStarterDialog, setShowStarterDialog] = useState(false);

  const { data: universe, isLoading: uLoading, isError } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";

  const { data: chars, isLoading: charsLoading } = useCharacters(uid);
  const { data: locs, isLoading: locsLoading } = useLocations(uid);
  const { data: orgs, isLoading: orgsLoading } = useOrganizations(uid);
  const { data: objs, isLoading: objsLoading } = useWorldObjects(uid);
  const { data: rules, isLoading: rulesLoading } = useWorldRules(uid);
  const { data: rels, isLoading: relsLoading } = useRelationships({
    universe_id: uid,
    limit: 1,
  });
  const { data: timelineData, isLoading: timelineLoading } = useTimelineEvents({
    universe_id: uid,
    limit: 1,
  });

  if (uLoading) {
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
        <Button asChild>
          <Link href="/">Go Home</Link>
        </Button>
      </div>
    );
  }

  const modules = [
    {
      icon: Users,
      title: "Characters",
      description: "Protagonists, antagonists, and every soul in between.",
      count: chars?.total,
      href: `/universe/${slug}/characters`,
      newHref: `/universe/${slug}/characters/new`,
      isLoading: charsLoading,
    },
    {
      icon: MapPin,
      title: "Locations",
      description: "Cities, realms, dimensions, and secret places.",
      count: locs?.total,
      href: `/universe/${slug}/locations`,
      newHref: `/universe/${slug}/locations/new`,
      isLoading: locsLoading,
    },
    {
      icon: Network,
      title: "Organizations",
      description: "Factions, guilds, governments, and secret societies.",
      count: orgs?.total,
      href: `/universe/${slug}/organizations`,
      newHref: `/universe/${slug}/organizations/new`,
      isLoading: orgsLoading,
    },
    {
      icon: Package,
      title: "Objects",
      description: "Artifacts, weapons, relics, and special items.",
      count: objs?.total,
      href: `/universe/${slug}/objects`,
      newHref: `/universe/${slug}/objects/new`,
      isLoading: objsLoading,
    },
    {
      icon: BookOpen,
      title: "World Rules",
      description: "Magic systems, physics, laws, and cosmology.",
      count: rules?.total,
      href: `/universe/${slug}/rules`,
      newHref: `/universe/${slug}/rules/new`,
      isLoading: rulesLoading,
    },
    {
      icon: Share2,
      title: "Relationships",
      description: "Connections between every entity in your world.",
      count: rels?.total,
      href: `/universe/${slug}/relationships`,
      newHref: `/universe/${slug}/relationships`,
      isLoading: relsLoading,
    },
    {
      icon: Clock,
      title: "Timeline",
      description: "Chronological events that shape your world's history.",
      count: timelineData?.total,
      href: `/universe/${slug}/timeline`,
      newHref: `/universe/${slug}/timeline`,
      isLoading: timelineLoading,
    },
    {
      icon: GitFork,
      title: "Knowledge Graph",
      description: "Visualize your universe as an interactive node graph.",
      count: undefined,
      href: `/universe/${slug}/graph`,
      newHref: `/universe/${slug}/graph`,
      isLoading: false,
    },
  ];

  const totalEntities =
    (chars?.total || 0) +
    (locs?.total || 0) +
    (orgs?.total || 0) +
    (objs?.total || 0) +
    (rules?.total || 0) +
    (rels?.total || 0) +
    (timelineData?.total || 0);

  const isCompletelyEmpty =
    totalEntities === 0 &&
    !charsLoading &&
    !locsLoading &&
    !orgsLoading &&
    !objsLoading &&
    !rulesLoading &&
    !relsLoading &&
    !timelineLoading;

  return (
    <EntityPageShell
      breadcrumbs={[
        { label: universe.name, href: `/universe/${slug}` },
        { label: "World Building" },
      ]}
    >
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10 space-y-1"
      >
        <h1 className="text-3xl font-extrabold tracking-tight">World Building</h1>
        <p className="text-muted-foreground">
          Every element that makes{" "}
          <span className="font-medium text-foreground">{universe.name}</span> a living world.
        </p>
      </motion.div>

      {isCompletelyEmpty && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="mb-8 rounded-xl border border-primary/20 bg-primary/5 p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6"
        >
          <div>
            <h3 className="text-lg font-bold text-foreground flex items-center gap-2 mb-2">
              <Sparkles className="h-5 w-5 text-primary" />
              Empty Universe Detected
            </h3>
            <p className="text-muted-foreground max-w-2xl text-sm leading-relaxed">
              Your universe is completely empty! You can start building manually by creating characters, locations, and rules, or you can instantly generate a rich, interconnected <strong>Starter World</strong> to explore the Knowledge Graph, Timeline, and AI capabilities right away.
            </p>
          </div>
          <div className="shrink-0 flex gap-3">
            <Button
              onClick={() => setShowStarterDialog(true)}
              className="gap-2 shadow-[0_0_15px_rgba(138,43,226,0.3)] hover:shadow-[0_0_25px_rgba(138,43,226,0.5)] transition-all"
            >
              <Sparkles className="h-4 w-4" />
              Generate Starter World
            </Button>
          </div>
        </motion.div>
      )}

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {modules.map((mod, i) => (
          <StudioCard key={mod.title} {...mod} index={i} />
        ))}
      </div>

      <GenerateStarterWorldDialog
        universeId={uid}
        slug={slug}
        open={showStarterDialog}
        onOpenChange={setShowStarterDialog}
      />
    </EntityPageShell>
  );
}
