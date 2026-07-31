"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { ArrowRight, BookOpen, Layers, Sparkles, Wand2, Globe, GitBranch } from "lucide-react";
import { Button } from "@/components/ui/button";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.5, ease: "easeOut" },
  }),
};

const features = [
  {
    icon: BookOpen,
    title: "Universe Builder",
    desc: "Craft intricate fictional worlds with rich lore, geography, and history — all in one place.",
  },
  {
    icon: Layers,
    title: "Deep World Architecture",
    desc: "Organise characters, locations, timelines, and factions with structured, linked data.",
  },
  {
    icon: Sparkles,
    title: "AI Narrative Intelligence",
    desc: "Upcoming: let AI surface contradictions, suggest connections, and keep your canon consistent.",
  },
  {
    icon: Globe,
    title: "Living World Bible",
    desc: "Your single source of truth. Every detail lives in a structured, searchable knowledge base.",
  },
  {
    icon: GitBranch,
    title: "Timeline Engine",
    desc: "Map every event to a timeline. Visualise how your world evolves across eras and storylines.",
  },
  {
    icon: Wand2,
    title: "Simulation Studio",
    desc: "Upcoming: simulate how characters and factions would react to hypothetical events.",
  },
];

const steps = [
  {
    step: "01",
    title: "Create a Universe",
    desc: "Name your world, pick a genre, and set the tone.",
  },
  {
    step: "02",
    title: "Build Your Lore",
    desc: "Add characters, locations, and world-building details.",
  },
  {
    step: "03",
    title: "Weave the Story",
    desc: "Connect events, trace timelines, explore possibilities.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* ── Nav ── */}
      <header className="glass fixed inset-x-0 top-0 z-50 border-b border-primary/20">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <Image
              src="/logo.jpg"
              alt="Loreweave Logo"
              width={40}
              height={40}
              className="h-10 w-10 rounded-full border border-primary/40 shadow-[0_0_20px_rgba(138,43,226,0.6)]"
            />
            <span className="text-xl font-extrabold tracking-widest text-primary drop-shadow-[0_2px_10px_rgba(0,212,255,0.4)]">
              LOREWEAVE
            </span>
          </div>
          <nav className="flex items-center gap-3">
            <Button variant="ghost" size="sm" asChild>
              <a href="#how-it-works">How It Works</a>
            </Button>
            <Button size="sm" asChild>
              <Link href="/create-universe">
                Create Universe
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Link>
            </Button>
          </nav>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="flex min-h-screen flex-col items-center justify-center px-6 pt-14 text-center">
        <motion.div
          className="mx-auto max-w-3xl space-y-6"
          initial="hidden"
          animate="show"
          variants={{ show: { transition: { staggerChildren: 0.1 } } }}
        >
          <motion.div variants={fadeUp} custom={0} className="mb-4 flex justify-center">
            <span className="inline-block rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary shadow-[0_0_15px_rgba(138,43,226,0.3)]">
              World-Building Platform
            </span>
          </motion.div>

          <motion.div variants={fadeUp} custom={0.5} className="mb-6 flex justify-center">
            <Image
              src="/logo.jpg"
              alt="Loreweave Logo"
              width={160}
              height={160}
              className="h-32 w-32 rounded-full border-2 border-primary/50 shadow-[0_0_60px_rgba(138,43,226,0.6)] sm:h-40 sm:w-40"
            />
          </motion.div>

          <motion.h1
            variants={fadeUp}
            custom={1}
            className="text-5xl font-extrabold leading-tight tracking-tight sm:text-6xl lg:text-7xl"
          >
            Where Stories Become <span className="text-primary">Living Worlds</span>
          </motion.h1>

          <motion.p
            variants={fadeUp}
            custom={2}
            className="mx-auto max-w-xl text-lg text-muted-foreground"
          >
            Build, organise, and evolve fictional universes with AI-powered narrative intelligence.
          </motion.p>

          <motion.div
            variants={fadeUp}
            custom={3}
            className="flex flex-col items-center gap-3 sm:flex-row sm:justify-center"
          >
            <Button size="lg" asChild>
              <Link href="/create-universe">
                Create Universe
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <a href="#features">Learn More</a>
            </Button>
          </motion.div>
        </motion.div>
      </section>

      {/* ── Features ── */}
      <section id="features" className="px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything a world-builder needs
            </h2>
            <p className="mt-3 text-muted-foreground">
              A complete creative studio for fiction, fantasy, and storytelling.
            </p>
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.07, duration: 0.4 }}
                className="glass space-y-3 rounded-2xl p-6 transition-shadow duration-300 hover:shadow-[0_0_20px_rgba(138,43,226,0.2)]"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
                  <f.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold">{f.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section id="how-it-works" className="bg-muted/30 px-6 py-24">
        <div className="mx-auto max-w-4xl">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">How It Works</h2>
            <p className="mt-3 text-muted-foreground">Three steps to a living, breathing world.</p>
          </div>
          <div className="grid gap-8 sm:grid-cols-3">
            {steps.map((s, i) => (
              <motion.div
                key={s.step}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="space-y-3 text-center"
              >
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full border-2 border-primary text-lg font-bold text-primary">
                  {s.step}
                </div>
                <h3 className="font-semibold">{s.title}</h3>
                <p className="text-sm text-muted-foreground">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="px-6 py-24">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="glass relative mx-auto max-w-2xl space-y-6 overflow-hidden rounded-3xl p-12 text-center"
        >
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 to-accent/10 opacity-50"></div>
          <div className="relative z-10">
            <h2 className="text-3xl font-bold tracking-tight">Ready to build your world?</h2>
            <p className="mt-2 text-muted-foreground">
              Start with a name and a genre. Everything else will follow.
            </p>
          </div>
          <Button size="lg" className="relative z-10 shadow-[0_0_20px_rgba(255,0,255,0.4)]" asChild>
            <Link href="/create-universe">
              Create Your Universe
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </motion.div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-border px-6 py-8 text-center">
        <p className="text-sm text-muted-foreground">
          © {new Date().getFullYear()} LOREWEAVE. Built for storytellers.
        </p>
      </footer>
    </div>
  );
}
