"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowRight, Loader2, Sparkles } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { useCreateUniverse } from "@/hooks/use-universes";
import { GENRE_LABELS, type UniverseGenre } from "@/types/universe";

const schema = z.object({
  name: z
    .string()
    .min(1, "Universe name is required")
    .max(120, "Name must be 120 characters or fewer")
    .refine((v) => v.trim().length > 0, "Name must not be blank"),
  genre: z.enum(
    [
      "fantasy",
      "science_fiction",
      "mystery",
      "horror",
      "romance",
      "adventure",
      "historical",
      "thriller",
      "cyberpunk",
      "steampunk",
      "slice_of_life",
      "other",
    ],
    { required_error: "Please select a genre" }
  ),
  description: z.string().max(3000, "Description must be 3000 characters or fewer").optional(),
  tone: z.string().max(200, "Tone must be 200 characters or fewer").optional(),
  target_audience: z
    .string()
    .max(200, "Target audience must be 200 characters or fewer")
    .optional(),
});

type FormValues = z.infer<typeof schema>;

function slugify(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

export default function CreateUniversePage() {
  const router = useRouter();
  const { mutateAsync: createUniverse, isPending, isSuccess } = useCreateUniverse();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const nameValue = watch("name") ?? "";
  const slugPreview = slugify(nameValue);

  async function onSubmit(values: FormValues) {
    const universe = await createUniverse({
      name: values.name.trim(),
      genre: values.genre as UniverseGenre,
      description: values.description || undefined,
      tone: values.tone || undefined,
      target_audience: values.target_audience || undefined,
    });
    router.push(`/universe/${universe.slug}`);
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border/60 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-6">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Link>
          <span className="text-sm font-semibold">Create Universe</span>
          <div className="w-16" />
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-8"
        >
          {/* Title */}
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">New Universe</h1>
            <p className="text-muted-foreground">
              Give your world a name and a genre. Everything else can be filled in later.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>
            {/* Name */}
            <div className="space-y-1.5">
              <label htmlFor="name" className="text-sm font-medium">
                Universe Name <span className="text-destructive">*</span>
              </label>
              <input
                id="name"
                type="text"
                placeholder="e.g. The Shattered Realm"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register("name")}
                aria-invalid={!!errors.name}
                aria-describedby={errors.name ? "name-error" : undefined}
              />
              {/* Slug preview */}
              {slugPreview && (
                <p className="text-xs text-muted-foreground">
                  Slug: <code className="font-mono">{slugPreview}</code>
                </p>
              )}
              {errors.name && (
                <p id="name-error" className="text-xs text-destructive" role="alert">
                  {errors.name.message}
                </p>
              )}
            </div>

            {/* Genre */}
            <div className="space-y-1.5">
              <label htmlFor="genre" className="text-sm font-medium">
                Genre <span className="text-destructive">*</span>
              </label>
              <select
                id="genre"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register("genre")}
                aria-invalid={!!errors.genre}
                aria-describedby={errors.genre ? "genre-error" : undefined}
              >
                <option value="">Select a genre…</option>
                {(Object.keys(GENRE_LABELS) as UniverseGenre[]).map((key) => (
                  <option key={key} value={key}>
                    {GENRE_LABELS[key]}
                  </option>
                ))}
              </select>
              {errors.genre && (
                <p id="genre-error" className="text-xs text-destructive" role="alert">
                  {errors.genre.message}
                </p>
              )}
            </div>

            {/* Description */}
            <div className="space-y-1.5">
              <label htmlFor="description" className="text-sm font-medium">
                Description <span className="font-normal text-muted-foreground">(optional)</span>
              </label>
              <textarea
                id="description"
                rows={4}
                placeholder="What is this universe about? Set the scene in a few sentences…"
                className="flex w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register("description")}
                aria-invalid={!!errors.description}
              />
              {errors.description && (
                <p className="text-xs text-destructive" role="alert">
                  {errors.description.message}
                </p>
              )}
            </div>

            {/* Tone */}
            <div className="space-y-1.5">
              <label htmlFor="tone" className="text-sm font-medium">
                Tone <span className="font-normal text-muted-foreground">(optional)</span>
              </label>
              <input
                id="tone"
                type="text"
                placeholder="e.g. Dark and gritty, hopeful, satirical…"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register("tone")}
              />
            </div>

            {/* Target Audience */}
            <div className="space-y-1.5">
              <label htmlFor="target_audience" className="text-sm font-medium">
                Target Audience{" "}
                <span className="font-normal text-muted-foreground">(optional)</span>
              </label>
              <input
                id="target_audience"
                type="text"
                placeholder="e.g. Young adult, general fiction, tabletop RPG players…"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register("target_audience")}
              />
            </div>

            {/* Submit */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <Button type="button" variant="outline" asChild>
                <Link href="/">Cancel</Link>
              </Button>
              <Button type="submit" disabled={isPending || isSuccess}>
                {isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating…
                  </>
                ) : isSuccess ? (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Created!
                  </>
                ) : (
                  <>
                    Create Universe
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </form>
        </motion.div>
      </main>
    </div>
  );
}
