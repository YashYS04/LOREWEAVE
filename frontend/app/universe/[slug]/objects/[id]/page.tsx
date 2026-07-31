"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion, AnimatePresence } from "framer-motion";
import { Pencil, Share2, Trash2, X, Check, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityFormSection, EntityPageShell, EntityRelationshipsTab } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import {
  useWorldObject,
  useUpdateWorldObject,
  useDeleteWorldObject,
} from "@/hooks/use-world-objects";
import { useEntityRelationships } from "@/hooks/use-relationships";
import Link from "next/link";

interface PageProps {
  params: Promise<{ slug: string; id: string }>;
}

const schema = z.object({
  name: z.string().min(1).max(200),
  category: z.string().max(100).optional().or(z.literal("")),
  description: z.string().max(5000).optional().or(z.literal("")),
  origin: z.string().max(2000).optional().or(z.literal("")),
  owner: z.string().max(200).optional().or(z.literal("")),
  abilities: z.string().max(2000).optional().or(z.literal("")),
  notes: z.string().max(2000).optional().or(z.literal("")),
});
type FormValues = z.infer<typeof schema>;

const inputCls =
  "w-full rounded-lg border border-border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring";

function Section({ title, content }: { title: string; content: string | null }) {
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

function Field({
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

export default function ObjectProfilePage({ params }: PageProps) {
  const { slug, id } = use(params);
  const router = useRouter();
  const [isEditing, setIsEditing] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "relationships">("overview");

  const { data: universe } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";
  const { data: item, isLoading, isError } = useWorldObject(id);
  const update = useUpdateWorldObject(id, uid);
  const del = useDeleteWorldObject(uid);
  const { data: relData } = useEntityRelationships(uid, id, "object");
  const relCount = relData?.total ?? 0;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const enterEdit = () => {
    if (!item) return;
    reset({
      name: item.name,
      category: item.category ?? "",
      description: item.description ?? "",
      origin: item.origin ?? "",
      owner: item.owner ?? "",
      abilities: item.abilities ?? "",
      notes: item.notes ?? "",
    });
    setIsEditing(true);
  };

  const onSave = async (data: FormValues) => {
    await update.mutateAsync({
      name: data.name,
      category: data.category?.trim() || undefined,
      description: data.description?.trim() || undefined,
      origin: data.origin?.trim() || undefined,
      owner: data.owner?.trim() || undefined,
      abilities: data.abilities?.trim() || undefined,
      notes: data.notes?.trim() || undefined,
    });
    setIsEditing(false);
  };

  const onDelete = async () => {
    await del.mutateAsync(id);
    router.push(`/universe/${slug}/objects`);
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !item) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
        <AlertCircle className="h-10 w-10 text-destructive" />
        <h1 className="text-2xl font-bold">Object not found</h1>
        <Button asChild>
          <Link href={`/universe/${slug}/objects`}>Back</Link>
        </Button>
      </div>
    );
  }

  return (
    <EntityPageShell
      breadcrumbs={[{ label: "Objects", href: `/universe/${slug}/objects` }, { label: item.name }]}
    >
      <AnimatePresence mode="wait">
        {!isEditing ? (
          <motion.div
            key="view"
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-8"
          >
            <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="space-y-2">
                {item.category && (
                  <span className="rounded-full border border-border bg-muted px-2.5 py-0.5 text-xs text-muted-foreground">
                    {item.category}
                  </span>
                )}
                <h1 className="text-4xl font-extrabold tracking-tight">{item.name}</h1>
                {item.owner && <p className="text-sm text-muted-foreground">Owner: {item.owner}</p>}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={enterEdit}>
                  <Pencil className="mr-1.5 h-3.5 w-3.5" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-destructive hover:border-destructive/50 hover:bg-destructive/10"
                  onClick={() => setShowDelete(true)}
                >
                  <Trash2 className="mr-1.5 h-3.5 w-3.5" />
                  Delete
                </Button>
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 border-b border-border">
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
                  {tab === "relationships" && relCount > 0 && (
                    <span className="ml-1 rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-semibold">
                      {relCount}
                    </span>
                  )}
                </button>
              ))}
            </div>

            <AnimatePresence>
              {showDelete && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="rounded-lg border border-destructive/40 bg-destructive/10 p-4">
                    <p className="mb-3 text-sm font-medium text-destructive">
                      Delete &ldquo;{item.name}&rdquo;? This action cannot be undone.
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={onDelete}
                        disabled={del.isPending}
                      >
                        {del.isPending ? (
                          <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <Check className="mr-1.5 h-3.5 w-3.5" />
                        )}
                        Confirm
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => setShowDelete(false)}>
                        <X className="mr-1.5 h-3.5 w-3.5" />
                        Cancel
                      </Button>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence mode="wait">
              {activeTab === "overview" ? (
                <motion.div
                  key="overview"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <div className="divide-y divide-border">
                    {item.description && (
                      <div className="py-6">
                        <Section title="Description" content={item.description} />
                      </div>
                    )}
                    {(item.origin || item.abilities) && (
                      <div className="grid gap-6 py-6 sm:grid-cols-2">
                        <Section title="Origin" content={item.origin} />
                        <Section title="Abilities" content={item.abilities} />
                      </div>
                    )}
                    {item.notes && (
                      <div className="py-6">
                        <Section title="Notes" content={item.notes} />
                      </div>
                    )}
                  </div>
                  <div className="space-y-0.5 border-t border-border pt-6 text-xs text-muted-foreground">
                    <p>Created {new Date(item.created_at).toLocaleDateString()}</p>
                    <p>Updated {new Date(item.updated_at).toLocaleDateString()}</p>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="relationships"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <EntityRelationshipsTab
                    universeId={uid}
                    entityId={id}
                    entityType="object"
                    entityName={item.name}
                    slug={slug}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ) : (
          <motion.div
            key="edit"
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-8"
          >
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold">Edit Object</h1>
              <Button variant="ghost" size="sm" onClick={() => setIsEditing(false)}>
                <X className="mr-1.5 h-3.5 w-3.5" />
                Discard
              </Button>
            </div>
            {update.isError && (
              <div className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                <AlertCircle className="h-4 w-4" />
                Failed to update.
              </div>
            )}
            <form onSubmit={handleSubmit(onSave)} className="space-y-10">
              <EntityFormSection title="Basic Information">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="sm:col-span-2">
                    <Field label="Name" required error={errors.name?.message}>
                      <input className={inputCls} {...register("name")} />
                    </Field>
                  </div>
                  <Field label="Category">
                    <input className={inputCls} {...register("category")} />
                  </Field>
                  <Field label="Owner">
                    <input className={inputCls} {...register("owner")} />
                  </Field>
                </div>
              </EntityFormSection>
              <EntityFormSection title="Description">
                <Field label="Description">
                  <textarea className={inputCls} rows={5} {...register("description")} />
                </Field>
              </EntityFormSection>
              <EntityFormSection title="History & Abilities">
                <div className="grid gap-4 sm:grid-cols-2">
                  <Field label="Origin">
                    <textarea className={inputCls} rows={3} {...register("origin")} />
                  </Field>
                  <Field label="Abilities">
                    <textarea className={inputCls} rows={3} {...register("abilities")} />
                  </Field>
                </div>
              </EntityFormSection>
              <EntityFormSection title="Notes">
                <Field label="Notes">
                  <textarea className={inputCls} rows={3} {...register("notes")} />
                </Field>
              </EntityFormSection>
              <div className="flex gap-3 border-t border-border pt-6">
                <Button type="submit" disabled={isSubmitting || update.isPending}>
                  {isSubmitting || update.isPending ? (
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
    </EntityPageShell>
  );
}
