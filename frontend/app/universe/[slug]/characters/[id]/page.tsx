"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  ArrowLeftRight,
  ArrowRight,
  Loader2,
  AlertCircle,
  Pencil,
  Plus,
  Share2,
  Trash2,
  X,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityFormSection } from "@/components/entity";
import { useCharacter, useUpdateCharacter, useDeleteCharacter } from "@/hooks/use-characters";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { useEntityRelationships, useDeleteRelationship } from "@/hooks/use-relationships";
import {
  CHARACTER_STATUS_LABELS,
  CHARACTER_STATUS_STYLES,
  type CharacterStatus,
} from "@/types/character";
import {
  RELATIONSHIP_TYPE_LABELS,
  ENTITY_TYPE_LABELS,
  type RelationshipType,
  type EntityType,
} from "@/types/relationship";

interface PageProps {
  params: Promise<{ slug: string; id: string }>;
}

// ── Zod schema for inline editing ─────────────────────────────────────────────

const editSchema = z.object({
  name: z.string().min(1, "Name is required").max(200),
  role: z.string().max(200).optional().or(z.literal("")),
  age: z.string().max(50).optional().or(z.literal("")),
  gender: z.string().max(100).optional().or(z.literal("")),
  occupation: z.string().max(200).optional().or(z.literal("")),
  biography: z.string().max(5000).optional().or(z.literal("")),
  personality: z.string().max(2000).optional().or(z.literal("")),
  goals: z.string().max(2000).optional().or(z.literal("")),
  motivations: z.string().max(2000).optional().or(z.literal("")),
  strengths: z.string().max(2000).optional().or(z.literal("")),
  weaknesses: z.string().max(2000).optional().or(z.literal("")),
  notes: z.string().max(2000).optional().or(z.literal("")),
  status: z.enum(["active", "deceased", "unknown", "archived"]),
});

type EditFormValues = z.infer<typeof editSchema>;

// ── Small UI helpers ───────────────────────────────────────────────────────────

function DetailSection({ title, content }: { title: string; content: string | null }) {
  if (!content) return null;
  return (
    <div className="space-y-1.5">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {title}
      </h3>
      <p className="whitespace-pre-wrap text-sm leading-relaxed">{content}</p>
    </div>
  );
}

function FormField({
  label,
  error,
  required,
  children,
}: {
  label: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium">
        {label}
        {required && <span className="ml-1 text-destructive">*</span>}
      </label>
      {children}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}

const inputCls =
  "w-full rounded-lg border border-border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring";

// ── Page ───────────────────────────────────────────────────────────────────────

export default function CharacterProfilePage({ params }: PageProps) {
  const { slug, id } = use(params);
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "relationships">("overview");

  const { data: universe } = useUniverseBySlug(slug);
  const universeId = universe?.id ?? "";

  const { data: character, isLoading, isError } = useCharacter(id);

  const updateCharacter = useUpdateCharacter(id, universeId);
  const deleteCharacter = useDeleteCharacter(universeId);
  const deleteRel = useDeleteRelationship(universeId);
  const { data: relData, isLoading: relsLoading } = useEntityRelationships(
    universeId,
    id,
    "character"
  );
  const rels = relData?.items ?? [];
  const incomingRels = rels.filter((r) => r.target_entity_id === id);
  const outgoingRels = rels.filter((r) => r.source_entity_id === id);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<EditFormValues>({
    resolver: zodResolver(editSchema),
  });

  const enterEditMode = () => {
    if (!character) return;
    reset({
      name: character.name,
      role: character.role ?? "",
      age: character.age ?? "",
      gender: character.gender ?? "",
      occupation: character.occupation ?? "",
      biography: character.biography ?? "",
      personality: character.personality ?? "",
      goals: character.goals ?? "",
      motivations: character.motivations ?? "",
      strengths: character.strengths ?? "",
      weaknesses: character.weaknesses ?? "",
      notes: character.notes ?? "",
      status: character.status as CharacterStatus,
    });
    setIsEditing(true);
  };

  const onSave = async (data: EditFormValues) => {
    await updateCharacter.mutateAsync({
      name: data.name,
      role: data.role?.trim() || undefined,
      age: data.age?.trim() || undefined,
      gender: data.gender?.trim() || undefined,
      occupation: data.occupation?.trim() || undefined,
      biography: data.biography?.trim() || undefined,
      personality: data.personality?.trim() || undefined,
      goals: data.goals?.trim() || undefined,
      motivations: data.motivations?.trim() || undefined,
      strengths: data.strengths?.trim() || undefined,
      weaknesses: data.weaknesses?.trim() || undefined,
      notes: data.notes?.trim() || undefined,
      status: data.status,
    });
    setIsEditing(false);
  };

  const onDelete = async () => {
    await deleteCharacter.mutateAsync(id);
    router.push(`/universe/${slug}/characters`);
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !character) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <h1 className="text-2xl font-bold">Character not found</h1>
        <Button asChild>
          <Link href={`/universe/${slug}/characters`}>Back to Characters</Link>
        </Button>
      </div>
    );
  }

  const statusClass = CHARACTER_STATUS_STYLES[character.status] ?? CHARACTER_STATUS_STYLES.active;
  const statusLabel = CHARACTER_STATUS_LABELS[character.status] ?? character.status;
  const createdDate = new Date(character.created_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  const updatedDate = new Date(character.updated_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-3xl items-center gap-4 px-6">
          <Link
            href={`/universe/${slug}/characters`}
            className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Characters
          </Link>
          <span className="text-muted-foreground">/</span>
          <span className="max-w-xs truncate text-sm font-medium">{character.name}</span>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-10">
        <AnimatePresence mode="wait">
          {!isEditing ? (
            // ── VIEW MODE ─────────────────────────────────────────────────────
            <motion.div
              key="view"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="space-y-8"
            >
              {/* Title row */}
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div className="space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${statusClass}`}
                    >
                      {statusLabel}
                    </span>
                    {character.role && (
                      <span className="text-sm text-muted-foreground">{character.role}</span>
                    )}
                  </div>
                  <h1 className="text-4xl font-extrabold tracking-tight">{character.name}</h1>
                  {(character.occupation || character.gender || character.age) && (
                    <p className="text-sm text-muted-foreground">
                      {[character.occupation, character.gender, character.age]
                        .filter(Boolean)
                        .join(" · ")}
                    </p>
                  )}
                </div>
                <div className="flex shrink-0 gap-2">
                  <Button variant="outline" size="sm" onClick={enterEditMode}>
                    <Pencil className="mr-1.5 h-3.5 w-3.5" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-destructive hover:border-destructive/50 hover:bg-destructive/10"
                    onClick={() => setShowDeleteConfirm(true)}
                  >
                    <Trash2 className="mr-1.5 h-3.5 w-3.5" />
                    Delete
                  </Button>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex gap-1 border-b border-border pb-0">
                {(["overview", "relationships"] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`flex items-center gap-1.5 border-b-2 px-3 pb-2 text-sm font-medium capitalize transition-colors ${
                      activeTab === tab
                        ? "border-primary text-foreground"
                        : "border-transparent text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {tab === "relationships" && <Share2 className="h-3.5 w-3.5" />}
                    {tab}
                    {tab === "relationships" && relData && (
                      <span className="ml-1 rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-semibold">
                        {rels.length}
                      </span>
                    )}
                  </button>
                ))}
              </div>

              {/* Delete confirm */}
              <AnimatePresence>
                {showDeleteConfirm && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-4">
                      <p className="mb-3 text-sm font-medium text-destructive">
                        Delete &ldquo;{character.name}&rdquo;? This action cannot be undone.
                      </p>
                      <div className="flex gap-2">
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={onDelete}
                          disabled={deleteCharacter.isPending}
                        >
                          {deleteCharacter.isPending ? (
                            <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Check className="mr-1.5 h-3.5 w-3.5" />
                          )}
                          Confirm
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowDeleteConfirm(false)}
                        >
                          <X className="mr-1.5 h-3.5 w-3.5" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Tab content */}
              <AnimatePresence mode="wait">
                {activeTab === "overview" ? (
                  <motion.div
                    key="overview"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    {/* Content sections */}
                    <div className="divide-y divide-border">
                      {character.biography && (
                        <div className="py-6">
                          <DetailSection title="Biography" content={character.biography} />
                        </div>
                      )}
                      {character.personality && (
                        <div className="py-6">
                          <DetailSection title="Personality" content={character.personality} />
                        </div>
                      )}
                      {(character.goals || character.motivations) && (
                        <div className="grid gap-6 py-6 sm:grid-cols-2">
                          <DetailSection title="Goals" content={character.goals} />
                          <DetailSection title="Motivations" content={character.motivations} />
                        </div>
                      )}
                      {(character.strengths || character.weaknesses) && (
                        <div className="grid gap-6 py-6 sm:grid-cols-2">
                          <DetailSection title="Strengths" content={character.strengths} />
                          <DetailSection title="Weaknesses" content={character.weaknesses} />
                        </div>
                      )}
                      {character.notes && (
                        <div className="py-6">
                          <DetailSection title="Notes" content={character.notes} />
                        </div>
                      )}
                    </div>
                    <div className="space-y-0.5 border-t border-border pt-6 text-xs text-muted-foreground">
                      <p>Created {createdDate}</p>
                      <p>Last updated {updatedDate}</p>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    key="relationships"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="space-y-6 py-2"
                  >
                    {relsLoading ? (
                      <div className="flex justify-center py-10">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                      </div>
                    ) : rels.length === 0 ? (
                      <div className="flex flex-col items-center gap-3 py-12 text-center">
                        <Share2 className="h-10 w-10 text-muted-foreground/40" />
                        <p className="text-sm text-muted-foreground">No relationships yet</p>
                        <Button size="sm" asChild variant="outline">
                          <Link href={`/universe/${slug}/relationships`}>
                            <Plus className="mr-1.5 h-3.5 w-3.5" />
                            Manage Relationships
                          </Link>
                        </Button>
                      </div>
                    ) : (
                      <>
                        {outgoingRels.length > 0 && (
                          <div>
                            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                              Outgoing ({outgoingRels.length})
                            </h3>
                            <div className="space-y-2">
                              {outgoingRels.map((r) => {
                                const label =
                                  RELATIONSHIP_TYPE_LABELS[
                                    r.relationship_type as RelationshipType
                                  ] ?? r.relationship_type;
                                const isBidi = r.direction === "bidirectional";
                                return (
                                  <div
                                    key={r.id}
                                    className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-sm"
                                  >
                                    <span className="font-medium">{character.name}</span>
                                    <span className="shrink-0 rounded-full border border-border bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
                                      {isBidi ? (
                                        <ArrowLeftRight className="inline h-3 w-3" />
                                      ) : (
                                        <ArrowRight className="inline h-3 w-3" />
                                      )}{" "}
                                      {label}
                                    </span>
                                    <span className="min-w-0 flex-1 truncate text-muted-foreground">
                                      {ENTITY_TYPE_LABELS[r.target_entity_type as EntityType] ??
                                        r.target_entity_type}
                                      : {r.target_entity_id}
                                    </span>
                                    <button
                                      className="ml-1 shrink-0 rounded p-0.5 text-muted-foreground hover:text-destructive"
                                      onClick={() => deleteRel.mutate(r.id)}
                                    >
                                      <X className="h-3.5 w-3.5" />
                                    </button>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}
                        {incomingRels.length > 0 && (
                          <div>
                            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                              Incoming ({incomingRels.length})
                            </h3>
                            <div className="space-y-2">
                              {incomingRels.map((r) => {
                                const label =
                                  RELATIONSHIP_TYPE_LABELS[
                                    r.relationship_type as RelationshipType
                                  ] ?? r.relationship_type;
                                return (
                                  <div
                                    key={r.id}
                                    className="flex items-center gap-2 rounded-lg border border-border bg-muted/30 px-3 py-2 text-sm"
                                  >
                                    <span className="min-w-0 flex-1 truncate text-muted-foreground">
                                      {ENTITY_TYPE_LABELS[r.source_entity_type as EntityType] ??
                                        r.source_entity_type}
                                      : {r.source_entity_id}
                                    </span>
                                    <span className="shrink-0 rounded-full border border-border bg-muted px-2 py-0.5 text-[10px] font-semibold text-muted-foreground">
                                      {label}
                                    </span>
                                    <span className="font-medium">{character.name}</span>
                                    <button
                                      className="ml-1 shrink-0 rounded p-0.5 text-muted-foreground hover:text-destructive"
                                      onClick={() => deleteRel.mutate(r.id)}
                                    >
                                      <X className="h-3.5 w-3.5" />
                                    </button>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}
                        <div className="pt-2">
                          <Button size="sm" variant="outline" asChild>
                            <Link href={`/universe/${slug}/relationships`}>
                              <Share2 className="mr-1.5 h-3.5 w-3.5" />
                              Manage All Relationships
                            </Link>
                          </Button>
                        </div>
                      </>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ) : (
            // ── EDIT MODE ─────────────────────────────────────────────────────
            <motion.div
              key="edit"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="space-y-8"
            >
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold">Edit Character</h1>
                <Button variant="ghost" size="sm" onClick={() => setIsEditing(false)}>
                  <X className="mr-1.5 h-3.5 w-3.5" />
                  Discard
                </Button>
              </div>

              {updateCharacter.isError && (
                <div className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  Failed to update. Please try again.
                </div>
              )}

              <form onSubmit={handleSubmit(onSave)} className="space-y-10">
                <EntityFormSection title="Basic Information">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="sm:col-span-2">
                      <FormField label="Name" required error={errors.name?.message}>
                        <input className={inputCls} {...register("name")} />
                      </FormField>
                    </div>
                    <FormField label="Role">
                      <input
                        className={inputCls}
                        placeholder="Protagonist, Antagonist…"
                        {...register("role")}
                      />
                    </FormField>
                    <FormField label="Status">
                      <select className={inputCls} {...register("status")}>
                        <option value="active">Active</option>
                        <option value="deceased">Deceased</option>
                        <option value="unknown">Unknown</option>
                        <option value="archived">Archived</option>
                      </select>
                    </FormField>
                    <FormField label="Occupation">
                      <input className={inputCls} {...register("occupation")} />
                    </FormField>
                    <FormField label="Age">
                      <input className={inputCls} {...register("age")} />
                    </FormField>
                    <FormField label="Gender">
                      <input className={inputCls} {...register("gender")} />
                    </FormField>
                  </div>
                </EntityFormSection>

                <EntityFormSection title="Biography">
                  <FormField label="Biography" error={errors.biography?.message}>
                    <textarea className={inputCls} rows={6} {...register("biography")} />
                  </FormField>
                </EntityFormSection>

                <EntityFormSection title="Personality">
                  <FormField label="Personality">
                    <textarea className={inputCls} rows={3} {...register("personality")} />
                  </FormField>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <FormField label="Goals">
                      <textarea className={inputCls} rows={3} {...register("goals")} />
                    </FormField>
                    <FormField label="Motivations">
                      <textarea className={inputCls} rows={3} {...register("motivations")} />
                    </FormField>
                  </div>
                </EntityFormSection>

                <EntityFormSection title="Strengths & Weaknesses">
                  <div className="grid gap-4 sm:grid-cols-2">
                    <FormField label="Strengths">
                      <textarea className={inputCls} rows={3} {...register("strengths")} />
                    </FormField>
                    <FormField label="Weaknesses">
                      <textarea className={inputCls} rows={3} {...register("weaknesses")} />
                    </FormField>
                  </div>
                </EntityFormSection>

                <EntityFormSection title="Notes">
                  <FormField label="Notes">
                    <textarea className={inputCls} rows={3} {...register("notes")} />
                  </FormField>
                </EntityFormSection>

                <div className="flex gap-3 border-t border-border pt-6">
                  <Button type="submit" disabled={isSubmitting || updateCharacter.isPending}>
                    {isSubmitting || updateCharacter.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Saving…
                      </>
                    ) : (
                      "Save Changes"
                    )}
                  </Button>
                  <Button type="button" variant="ghost" onClick={() => setIsEditing(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
