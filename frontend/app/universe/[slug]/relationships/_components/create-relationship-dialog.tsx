"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { AlertCircle, Loader2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { CreateRelationshipRequest } from "@/types/relationship";
import {
  RELATIONSHIP_TYPE_LABELS,
  ENTITY_TYPE_LABELS,
  DIRECTION_LABELS,
} from "@/types/relationship";

const schema = z
  .object({
    source_entity_type: z.enum(["character", "location", "organization", "object", "world_rule"]),
    source_entity_id: z.string().min(1, "Required"),
    target_entity_type: z.enum(["character", "location", "organization", "object", "world_rule"]),
    target_entity_id: z.string().min(1, "Required"),
    relationship_type: z.enum([
      "ally_of", "enemy_of", "friend_of", "parent_of", "child_of", "sibling_of",
      "mentor_of", "student_of", "member_of", "leader_of", "owns", "created",
      "created_by", "located_in", "lives_in", "protects", "rules", "loves",
      "hates", "rival_of", "custom",
    ]),
    direction: z.enum(["unidirectional", "bidirectional"]),
    title: z.string().max(300).optional().or(z.literal("")),
    description: z.string().max(5000).optional().or(z.literal("")),
    strength: z
      .union([z.number().int().min(1).max(10), z.nan()])
      .optional()
      .nullable(),
  })
  .refine(
    (d) =>
      !(d.source_entity_type === d.target_entity_type && d.source_entity_id === d.target_entity_id),
    { message: "Source and target must be different entities", path: ["target_entity_id"] },
  );

type FormValues = z.infer<typeof schema>;

const inputCls =
  "w-full rounded-lg border border-border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring";

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

interface Props {
  universeId: string;
  onSubmit: (payload: CreateRelationshipRequest) => Promise<void>;
  onClose: () => void;
  isPending: boolean;
  error?: string;
}

export function CreateRelationshipDialog({ universeId, onSubmit, onClose, isPending, error }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      source_entity_type: "character",
      target_entity_type: "character",
      relationship_type: "ally_of",
      direction: "unidirectional",
    },
  });

  const onValid = async (data: FormValues) => {
    await onSubmit({
      universe_id: universeId,
      source_entity_type: data.source_entity_type,
      source_entity_id: data.source_entity_id,
      target_entity_type: data.target_entity_type,
      target_entity_id: data.target_entity_id,
      relationship_type: data.relationship_type,
      direction: data.direction,
      title: data.title?.trim() || undefined,
      description: data.description?.trim() || undefined,
      strength:
        typeof data.strength === "number" && !Number.isNaN(data.strength)
          ? data.strength
          : undefined,
    });
  };

  return (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Dialog */}
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 12 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 12 }}
        transition={{ duration: 0.2 }}
        className="fixed inset-x-4 top-[10%] z-50 mx-auto max-w-xl overflow-y-auto rounded-2xl border border-border bg-background shadow-2xl"
        style={{ maxHeight: "80vh" }}
      >
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 className="text-lg font-bold">Create Relationship</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit(onValid)} className="space-y-5 px-6 py-5">
          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              <AlertCircle className="h-4 w-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Source */}
          <div className="rounded-xl border border-border bg-muted/20 p-4 space-y-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Source Entity
            </p>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Entity Type" required error={errors.source_entity_type?.message}>
                <select className={inputCls} {...register("source_entity_type")}>
                  {Object.entries(ENTITY_TYPE_LABELS).map(([v, l]) => (
                    <option key={v} value={v}>{l}</option>
                  ))}
                </select>
              </Field>
              <Field label="Entity ID / Name" required error={errors.source_entity_id?.message}>
                <input
                  className={inputCls}
                  placeholder="Enter entity ID"
                  {...register("source_entity_id")}
                />
              </Field>
            </div>
          </div>

          {/* Relationship */}
          <div className="grid grid-cols-2 gap-3">
            <Field label="Relationship Type" required error={errors.relationship_type?.message}>
              <select className={inputCls} {...register("relationship_type")}>
                {Object.entries(RELATIONSHIP_TYPE_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </Field>
            <Field label="Direction" error={errors.direction?.message}>
              <select className={inputCls} {...register("direction")}>
                {Object.entries(DIRECTION_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </Field>
          </div>

          {/* Target */}
          <div className="rounded-xl border border-border bg-muted/20 p-4 space-y-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Target Entity
            </p>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Entity Type" required error={errors.target_entity_type?.message}>
                <select className={inputCls} {...register("target_entity_type")}>
                  {Object.entries(ENTITY_TYPE_LABELS).map(([v, l]) => (
                    <option key={v} value={v}>{l}</option>
                  ))}
                </select>
              </Field>
              <Field label="Entity ID / Name" required error={errors.target_entity_id?.message}>
                <input
                  className={inputCls}
                  placeholder="Enter entity ID"
                  {...register("target_entity_id")}
                />
              </Field>
            </div>
          </div>

          {/* Optional fields */}
          <Field label="Title" error={errors.title?.message}>
            <input
              className={inputCls}
              placeholder="Give this relationship a name…"
              {...register("title")}
            />
          </Field>

          <Field label="Description" error={errors.description?.message}>
            <textarea
              className={inputCls}
              rows={3}
              placeholder="Describe this relationship…"
              {...register("description")}
            />
          </Field>

          <Field label="Strength (1–10)" error={errors.strength?.message}>
            <input
              type="number"
              min={1}
              max={10}
              className={inputCls}
              placeholder="Leave blank for unspecified"
              {...register("strength", { valueAsNumber: true })}
            />
          </Field>

          <div className="flex gap-3 border-t border-border pt-4">
            <Button type="submit" disabled={isPending}>
              {isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating…
                </>
              ) : (
                "Create Relationship"
              )}
            </Button>
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>
      </motion.div>
    </>
  );
}
