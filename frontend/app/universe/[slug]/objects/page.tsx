"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Plus, Package, Search, Clock, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityCard, EntityEmptyState, EntityHeader, EntityPageShell } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { useWorldObjects } from "@/hooks/use-world-objects";
import type { WorldObject } from "@/types/world-object";
import Link from "next/link";

interface PageProps {
  params: Promise<{ slug: string }>;
}

function ObjectCard({ obj, slug, index }: { obj: WorldObject; slug: string; index: number }) {
  return (
    <EntityCard index={index}>
      <Link href={`/universe/${slug}/objects/${obj.id}`} className="block space-y-2">
        <div className="flex items-start justify-between gap-2">
          <span className="text-sm font-semibold">{obj.name}</span>
          {obj.category && (
            <span className="shrink-0 rounded-full border border-border bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
              {obj.category}
            </span>
          )}
        </div>
        {obj.owner && (
          <p className="text-xs text-muted-foreground">
            <span className="font-medium">Owner:</span> {obj.owner}
          </p>
        )}
        {obj.description && (
          <p className="line-clamp-2 text-xs leading-relaxed text-muted-foreground">
            {obj.description}
          </p>
        )}
        <div className="flex items-center gap-1 pt-1 text-[11px] text-muted-foreground/70">
          <Clock className="h-3 w-3" />
          <span>
            Updated{" "}
            {new Date(obj.updated_at).toLocaleDateString(undefined, {
              year: "numeric",
              month: "short",
              day: "numeric",
            })}
          </span>
        </div>
      </Link>
    </EntityCard>
  );
}

export default function ObjectsPage({ params }: PageProps) {
  const { slug } = use(params);
  const router = useRouter();
  const [search, setSearch] = useState("");
  const { data: universe } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";
  const { data, isLoading } = useWorldObjects(uid);
  const items = data?.items ?? [];
  const filtered = search.trim()
    ? items.filter(
        (o) =>
          o.name.toLowerCase().includes(search.toLowerCase()) ||
          o.category?.toLowerCase().includes(search.toLowerCase())
      )
    : items;

  return (
    <EntityPageShell
      breadcrumbs={[
        { label: universe?.name ?? "Universe", href: `/universe/${slug}/world` },
        { label: "Objects" },
      ]}
    >
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <EntityHeader
          title="Objects"
          subtitle={`${data?.total ?? 0} object${(data?.total ?? 0) !== 1 ? "s" : ""}`}
          action={
            <Button size="sm" onClick={() => router.push(`/universe/${slug}/objects/new`)}>
              <Plus className="mr-1.5 h-4 w-4" />
              New Object
            </Button>
          }
        />
      </motion.div>
      {items.length > 0 && (
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search objects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-border bg-background py-2 pl-9 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      )}
      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : items.length === 0 ? (
        <EntityEmptyState
          icon={Package}
          title="No objects yet"
          description="Add artifacts, weapons, relics, and items to your world."
          actionLabel="New Object"
          onAction={() => router.push(`/universe/${slug}/objects/new`)}
        />
      ) : filtered.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">
          No objects match &ldquo;{search}&rdquo;.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((o, i) => (
            <ObjectCard key={o.id} obj={o} slug={slug} index={i} />
          ))}
        </div>
      )}
    </EntityPageShell>
  );
}
