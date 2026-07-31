"use client";

import { use } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Plus,
  Users,
  Search,
  Loader2,
  AlertCircle,
  Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityCard, EntityEmptyState, EntityHeader } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { useCharacters } from "@/hooks/use-characters";
import {
  CHARACTER_STATUS_LABELS,
  CHARACTER_STATUS_STYLES,
  type Character,
} from "@/types/character";
import { useState } from "react";

interface PageProps {
  params: Promise<{ slug: string }>;
}

function CharacterAvatar({ name }: { name: string }) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
  return (
    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
      {initials}
    </div>
  );
}

function CharacterListCard({
  character,
  slug,
  index,
}: {
  character: Character;
  slug: string;
  index: number;
}) {
  const updatedAt = new Date(character.updated_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
  const statusClass =
    CHARACTER_STATUS_STYLES[character.status] ??
    CHARACTER_STATUS_STYLES.active;
  const statusLabel = CHARACTER_STATUS_LABELS[character.status] ?? character.status;

  return (
    <EntityCard index={index}>
      <Link
        href={`/universe/${slug}/characters/${character.id}`}
        className="flex gap-4"
      >
        <CharacterAvatar name={character.name} />
        <div className="min-w-0 flex-1 space-y-1.5">
          <div className="flex flex-wrap items-center gap-2">
            <span className="truncate text-sm font-semibold leading-tight">
              {character.name}
            </span>
            <span
              className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium ${statusClass}`}
            >
              {statusLabel}
            </span>
          </div>
          {character.role && (
            <p className="text-xs font-medium text-muted-foreground">{character.role}</p>
          )}
          {character.personality && (
            <p className="line-clamp-2 text-xs leading-relaxed text-muted-foreground">
              {character.personality}
            </p>
          )}
          <div className="flex items-center gap-1 pt-1 text-[11px] text-muted-foreground/70">
            <Clock className="h-3 w-3" />
            <span>Updated {updatedAt}</span>
          </div>
        </div>
      </Link>
    </EntityCard>
  );
}

export default function CharactersPage({ params }: PageProps) {
  const { slug } = use(params);
  const router = useRouter();
  const [search, setSearch] = useState("");

  const { data: universe, isLoading: universeLoading } = useUniverseBySlug(slug);
  const universeId = universe?.id ?? "";
  const { data: charactersData, isLoading: charsLoading } = useCharacters(universeId);

  const isLoading = universeLoading || charsLoading;

  const characters = charactersData?.items ?? [];
  const filtered = search.trim()
    ? characters.filter(
        (c) =>
          c.name.toLowerCase().includes(search.toLowerCase()) ||
          c.role?.toLowerCase().includes(search.toLowerCase())
      )
    : characters;

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!universe) {
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

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-5xl items-center gap-4 px-6">
          <Link
            href={`/universe/${slug}`}
            className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            {universe.name}
          </Link>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium">Characters</span>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-8 px-6 py-10">
        <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}>
          <EntityHeader
            title="Characters"
            subtitle={`${charactersData?.total ?? 0} character${(charactersData?.total ?? 0) !== 1 ? "s" : ""} in ${universe.name}`}
            action={
              <Button
                size="sm"
                onClick={() => router.push(`/universe/${slug}/characters/new`)}
              >
                <Plus className="mr-1.5 h-4 w-4" />
                Create Character
              </Button>
            }
          />
        </motion.div>

        {/* Search */}
        {characters.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="relative"
          >
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search characters..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-border bg-background py-2 pl-9 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </motion.div>
        )}

        {/* List or empty state */}
        {characters.length === 0 ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
            <EntityEmptyState
              icon={Users}
              title="No characters yet"
              description="Create your first story character — protagonists, antagonists, allies, and every soul in between."
              actionLabel="Create Character"
              onAction={() => router.push(`/universe/${slug}/characters/new`)}
            />
          </motion.div>
        ) : filtered.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-xl border border-dashed border-border py-12 text-center text-muted-foreground"
          >
            No characters match &ldquo;{search}&rdquo;.
          </motion.div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((character, i) => (
              <CharacterListCard
                key={character.id}
                character={character}
                slug={slug}
                index={i}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
