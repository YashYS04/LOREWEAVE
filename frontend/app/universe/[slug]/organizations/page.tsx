"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Plus, Network, Search, Clock, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityCard, EntityEmptyState, EntityHeader, EntityPageShell } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { useOrganizations } from "@/hooks/use-organizations";
import type { Organization } from "@/types/organization";
import Link from "next/link";

interface PageProps { params: Promise<{ slug: string }> }

function OrgCard({ org, slug, index }: { org: Organization; slug: string; index: number }) {
  return (
    <EntityCard index={index}>
      <Link href={`/universe/${slug}/organizations/${org.id}`} className="block space-y-2">
        <div className="flex items-start justify-between gap-2">
          <span className="text-sm font-semibold">{org.name}</span>
          {org.type && <span className="shrink-0 rounded-full border border-border bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">{org.type}</span>}
        </div>
        {org.leader && <p className="text-xs text-muted-foreground"><span className="font-medium">Leader:</span> {org.leader}</p>}
        {org.description && <p className="line-clamp-2 text-xs leading-relaxed text-muted-foreground">{org.description}</p>}
        <div className="flex items-center gap-1 pt-1 text-[11px] text-muted-foreground/70">
          <Clock className="h-3 w-3" />
          <span>Updated {new Date(org.updated_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}</span>
        </div>
      </Link>
    </EntityCard>
  );
}

export default function OrganizationsPage({ params }: PageProps) {
  const { slug } = use(params);
  const router = useRouter();
  const [search, setSearch] = useState("");
  const { data: universe } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";
  const { data, isLoading } = useOrganizations(uid);
  const items = data?.items ?? [];
  const filtered = search.trim() ? items.filter(o => o.name.toLowerCase().includes(search.toLowerCase()) || o.type?.toLowerCase().includes(search.toLowerCase())) : items;

  return (
    <EntityPageShell breadcrumbs={[{ label: universe?.name ?? "Universe", href: `/universe/${slug}/world` }, { label: "Organizations" }]}>
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <EntityHeader title="Organizations" subtitle={`${data?.total ?? 0} organization${(data?.total ?? 0) !== 1 ? "s" : ""}`}
          action={<Button size="sm" onClick={() => router.push(`/universe/${slug}/organizations/new`)}><Plus className="mr-1.5 h-4 w-4" />New Organization</Button>} />
      </motion.div>
      {items.length > 0 && (
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input type="text" placeholder="Search organizations..." value={search} onChange={e => setSearch(e.target.value)} className="w-full rounded-lg border border-border bg-background py-2 pl-9 pr-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring" />
        </div>
      )}
      {isLoading ? <div className="flex justify-center py-20"><Loader2 className="h-8 w-8 animate-spin text-muted-foreground" /></div>
        : items.length === 0 ? <EntityEmptyState icon={Network} title="No organizations yet" description="Define the factions, guilds, and societies of your world." actionLabel="New Organization" onAction={() => router.push(`/universe/${slug}/organizations/new`)} />
        : filtered.length === 0 ? <p className="py-12 text-center text-sm text-muted-foreground">No organizations match &ldquo;{search}&rdquo;.</p>
        : <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{filtered.map((o, i) => <OrgCard key={o.id} org={o} slug={slug} index={i} />)}</div>}
    </EntityPageShell>
  );
}
