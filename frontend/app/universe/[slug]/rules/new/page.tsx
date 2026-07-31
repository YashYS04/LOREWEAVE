"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityFormSection, EntityPageShell } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { useCreateWorldRule } from "@/hooks/use-world-rules";

interface PageProps {
  params: Promise<{ slug: string }>;
}

const schema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  category: z.string().max(100).optional().or(z.literal("")),
  description: z.string().max(5000).optional().or(z.literal("")),
  limitations: z.string().max(2000).optional().or(z.literal("")),
  exceptions: z.string().max(2000).optional().or(z.literal("")),
  notes: z.string().max(2000).optional().or(z.literal("")),
});
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

export default function NewWorldRulePage({ params }: PageProps) {
  const { slug } = use(params);
  const router = useRouter();
  const { data: universe } = useUniverseBySlug(slug);
  const uid = universe?.id ?? "";
  const create = useCreateWorldRule(uid);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormValues) => {
    if (!uid) return;
    const item = await create.mutateAsync({
      universe_id: uid,
      title: data.title.trim(),
      category: data.category?.trim() || undefined,
      description: data.description?.trim() || undefined,
      limitations: data.limitations?.trim() || undefined,
      exceptions: data.exceptions?.trim() || undefined,
      notes: data.notes?.trim() || undefined,
    });
    router.push(`/universe/${slug}/rules/${item.id}`);
  };

  return (
    <EntityPageShell
      breadcrumbs={[
        { label: "World Rules", href: `/universe/${slug}/rules` },
        { label: "New Rule" },
      ]}
    >
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-8"
      >
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">New World Rule</h1>
          <p className="mt-1 text-muted-foreground">
            Define a law, system, or principle of your universe.
          </p>
        </div>
        {create.isError && (
          <div className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />
            Failed to create. Please try again.
          </div>
        )}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-10">
          <EntityFormSection title="Basic Information">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <Field label="Title" required error={errors.title?.message}>
                  <input
                    className={inputCls}
                    placeholder="e.g. Law of Conservation of Magic"
                    {...register("title")}
                  />
                </Field>
              </div>
              <Field label="Category">
                <input
                  className={inputCls}
                  placeholder="e.g. Magic System, Physics, Social"
                  {...register("category")}
                />
              </Field>
            </div>
          </EntityFormSection>
          <EntityFormSection title="Description">
            <Field label="Description" error={errors.description?.message}>
              <textarea
                className={inputCls}
                rows={5}
                placeholder="Explain this rule in detail..."
                {...register("description")}
              />
            </Field>
          </EntityFormSection>
          <EntityFormSection title="Limitations & Exceptions">
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Limitations">
                <textarea
                  className={inputCls}
                  rows={3}
                  placeholder="What are the constraints?"
                  {...register("limitations")}
                />
              </Field>
              <Field label="Exceptions">
                <textarea
                  className={inputCls}
                  rows={3}
                  placeholder="When does this rule not apply?"
                  {...register("exceptions")}
                />
              </Field>
            </div>
          </EntityFormSection>
          <EntityFormSection title="Notes">
            <Field label="Notes">
              <textarea className={inputCls} rows={3} {...register("notes")} />
            </Field>
          </EntityFormSection>
          <div className="flex gap-3 border-t border-border pt-6">
            <Button type="submit" disabled={isSubmitting || create.isPending}>
              {isSubmitting || create.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating…
                </>
              ) : (
                "Create Rule"
              )}
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => router.push(`/universe/${slug}/rules`)}
            >
              Cancel
            </Button>
          </div>
        </form>
      </motion.div>
    </EntityPageShell>
  );
}
