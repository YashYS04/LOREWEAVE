"use client";

import { use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { ArrowLeft, Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EntityFormSection } from "@/components/entity";
import { useUniverseBySlug } from "@/hooks/use-universes";
import { useCreateCharacter } from "@/hooks/use-characters";

interface PageProps {
  params: Promise<{ slug: string }>;
}

// ── Zod schema ─────────────────────────────────────────────────────────────────

const characterSchema = z.object({
  name: z.string().min(1, "Name is required").max(200, "Name is too long"),
  role: z.string().max(200).optional().or(z.literal("")),
  age: z.string().max(50).optional().or(z.literal("")),
  gender: z.string().max(100).optional().or(z.literal("")),
  occupation: z.string().max(200).optional().or(z.literal("")),
  biography: z
    .string()
    .max(5000, "Biography must be under 5000 characters")
    .optional()
    .or(z.literal("")),
  personality: z.string().max(2000).optional().or(z.literal("")),
  goals: z.string().max(2000).optional().or(z.literal("")),
  motivations: z.string().max(2000).optional().or(z.literal("")),
  strengths: z.string().max(2000).optional().or(z.literal("")),
  weaknesses: z.string().max(2000).optional().or(z.literal("")),
  notes: z.string().max(2000).optional().or(z.literal("")),
});

type CharacterFormValues = z.infer<typeof characterSchema>;

// ── Field components ───────────────────────────────────────────────────────────

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

function TextInput({
  placeholder,
  error,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & { error?: boolean }) {
  return (
    <input
      {...props}
      placeholder={placeholder}
      className={`w-full rounded-lg border px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring ${
        error ? "border-destructive" : "border-border bg-background"
      }`}
    />
  );
}

function TextArea({
  placeholder,
  rows = 4,
  error,
  ...props
}: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { error?: boolean }) {
  return (
    <textarea
      {...props}
      rows={rows}
      placeholder={placeholder}
      className={`w-full resize-y rounded-lg border px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring ${
        error ? "border-destructive" : "border-border bg-background"
      }`}
    />
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function NewCharacterPage({ params }: PageProps) {
  const { slug } = use(params);
  const router = useRouter();

  const { data: universe, isLoading: universeLoading } = useUniverseBySlug(slug);
  const universeId = universe?.id ?? "";
  const createCharacter = useCreateCharacter(universeId);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CharacterFormValues>({
    resolver: zodResolver(characterSchema),
    defaultValues: {
      name: "",
      role: "",
      biography: "",
      personality: "",
      goals: "",
      motivations: "",
      strengths: "",
      weaknesses: "",
      notes: "",
    },
  });

  const onSubmit = async (data: CharacterFormValues) => {
    if (!universeId) return;
    const payload = {
      universe_id: universeId,
      name: data.name.trim(),
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
    };
    const created = await createCharacter.mutateAsync(payload);
    router.push(`/universe/${slug}/characters/${created.id}`);
  };

  if (universeLoading) {
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

  const isPending = isSubmitting || createCharacter.isPending;

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
          <span className="text-sm font-medium">New Character</span>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-8"
        >
          <div className="space-y-1">
            <h1 className="text-3xl font-extrabold tracking-tight">New Character</h1>
            <p className="text-muted-foreground">
              Add a character to{" "}
              <span className="font-medium text-foreground">{universe.name}</span>
            </p>
          </div>

          {createCharacter.isError && (
            <div className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
              <AlertCircle className="h-4 w-4 shrink-0" />
              Failed to create character. Please try again.
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-10">
            {/* Basic Information */}
            <EntityFormSection title="Basic Information" description="Core identity fields.">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <FormField label="Name" required error={errors.name?.message}>
                    <TextInput
                      placeholder="Character's full name"
                      error={!!errors.name}
                      {...register("name")}
                    />
                  </FormField>
                </div>
                <FormField label="Role" error={errors.role?.message}>
                  <TextInput placeholder="e.g. Protagonist, Antagonist" {...register("role")} />
                </FormField>
                <FormField label="Occupation" error={errors.occupation?.message}>
                  <TextInput placeholder="e.g. Knight, Scientist" {...register("occupation")} />
                </FormField>
                <FormField label="Age" error={errors.age?.message}>
                  <TextInput placeholder="e.g. 32, Late 40s, Ancient" {...register("age")} />
                </FormField>
                <FormField label="Gender" error={errors.gender?.message}>
                  <TextInput placeholder="e.g. Male, Female, Non-binary" {...register("gender")} />
                </FormField>
              </div>
            </EntityFormSection>

            {/* Biography */}
            <EntityFormSection
              title="Biography"
              description="The character's backstory and history."
            >
              <FormField label="Biography" error={errors.biography?.message}>
                <TextArea
                  rows={6}
                  placeholder="Tell the story of who this character is and where they came from..."
                  error={!!errors.biography}
                  {...register("biography")}
                />
              </FormField>
            </EntityFormSection>

            {/* Personality */}
            <EntityFormSection
              title="Personality"
              description="How this character thinks, feels, and acts."
            >
              <FormField label="Personality Traits" error={errors.personality?.message}>
                <TextArea
                  rows={3}
                  placeholder="Describe the character's personality, demeanour, and quirks..."
                  {...register("personality")}
                />
              </FormField>
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField label="Goals" error={errors.goals?.message}>
                  <TextArea
                    rows={3}
                    placeholder="What does this character want to achieve?"
                    {...register("goals")}
                  />
                </FormField>
                <FormField label="Motivations" error={errors.motivations?.message}>
                  <TextArea
                    rows={3}
                    placeholder="What drives this character forward?"
                    {...register("motivations")}
                  />
                </FormField>
              </div>
            </EntityFormSection>

            {/* Strengths & Weaknesses */}
            <EntityFormSection
              title="Strengths & Weaknesses"
              description="The character's capabilities and limitations."
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField label="Strengths" error={errors.strengths?.message}>
                  <TextArea
                    rows={3}
                    placeholder="What is this character particularly good at?"
                    {...register("strengths")}
                  />
                </FormField>
                <FormField label="Weaknesses" error={errors.weaknesses?.message}>
                  <TextArea
                    rows={3}
                    placeholder="What are their flaws, limitations, or vulnerabilities?"
                    {...register("weaknesses")}
                  />
                </FormField>
              </div>
            </EntityFormSection>

            {/* Notes */}
            <EntityFormSection
              title="Notes"
              description="Any additional details you want to record."
            >
              <FormField label="Notes" error={errors.notes?.message}>
                <TextArea
                  rows={3}
                  placeholder="Miscellaneous notes, ideas, or reminders about this character..."
                  {...register("notes")}
                />
              </FormField>
            </EntityFormSection>

            {/* Actions */}
            <div className="flex items-center gap-3 border-t border-border pt-6">
              <Button type="submit" disabled={isPending}>
                {isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating…
                  </>
                ) : (
                  "Create Character"
                )}
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => router.push(`/universe/${slug}/characters`)}
              >
                Cancel
              </Button>
            </div>
          </form>
        </motion.div>
      </main>
    </div>
  );
}
