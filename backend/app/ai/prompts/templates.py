"""Reusable prompt templates.

Every template is a pure function that accepts a ``UniverseContext`` plus an
optional user question and returns a fully-formed prompt string ready to be
sent to the AI provider.

Templates are intentionally decoupled from any specific model or provider.
"""

import json

from app.ai.schemas.ai import UniverseContext


def _context_summary(ctx: UniverseContext) -> str:
    """Produce a compact text summary of the universe context for injection."""
    u = ctx.universe
    lines = [
        f"Universe: {u.name} | Genre: {u.genre} | Status: {u.status}",
    ]
    if u.tone:
        lines.append(f"Tone: {u.tone}")
    if u.description:
        lines.append(f"Overview: {u.description}")

    lines.append(f"\nCharacters ({len(ctx.characters)}):")
    for c in ctx.characters:
        parts = [c.name]
        if c.role:
            parts.append(f"({c.role})")
        lines.append("  - " + " ".join(parts))

    lines.append(f"\nLocations ({len(ctx.locations)}):")
    for loc in ctx.locations:
        parts = [loc.name]
        if loc.type:
            parts.append(f"[{loc.type}]")
        lines.append("  - " + " ".join(parts))

    lines.append(f"\nOrganizations ({len(ctx.organizations)}):")
    for o in ctx.organizations:
        parts = [o.name]
        if o.type:
            parts.append(f"[{o.type}]")
        lines.append("  - " + " ".join(parts))

    lines.append(f"\nObjects ({len(ctx.objects)}):")
    for obj in ctx.objects:
        parts = [obj.name]
        if obj.category:
            parts.append(f"[{obj.category}]")
        lines.append("  - " + " ".join(parts))

    lines.append(f"\nWorld Rules ({len(ctx.world_rules)}):")
    for r in ctx.world_rules:
        parts = [r.title]
        if r.category:
            parts.append(f"[{r.category}]")
        lines.append("  - " + " ".join(parts))

    return "\n".join(lines)


# ── Public prompt templates ────────────────────────────────────────────────────


def universe_summary(ctx: UniverseContext, user_question: str | None = None) -> str:
    """Produce a narrative overview of the universe."""
    base = (
        f"You are a world-building assistant analysing the fictional universe '{ctx.universe.name}'.\n\n"
        f"UNIVERSE CONTEXT:\n{_context_summary(ctx)}\n\n"
        "TASK: Write a rich, engaging summary of this universe in 2-3 paragraphs. "
        "Cover the genre, setting, tone, and any notable elements."
    )
    if user_question:
        base += f"\n\nUSER QUESTION: {user_question}"
    return base


def lore_summary(ctx: UniverseContext, user_question: str | None = None) -> str:
    """Summarise the lore across all world-building elements."""
    base = (
        f"You are a lore scholar analysing the universe '{ctx.universe.name}'.\n\n"
        f"UNIVERSE CONTEXT:\n{_context_summary(ctx)}\n\n"
        "TASK: Summarise the key lore — history, rules, factions, and places — in a "
        "structured, encyclopaedic style."
    )
    if user_question:
        base += f"\n\nUSER QUESTION: {user_question}"
    return base


def character_analysis(ctx: UniverseContext, user_question: str | None = None) -> str:
    """Deep-dive analysis of character dynamics."""
    chars_json = json.dumps(
        [c.model_dump() for c in ctx.characters], indent=2, default=str
    )
    base = (
        f"You are a narrative analyst for the universe '{ctx.universe.name}'.\n\n"
        f"CHARACTERS:\n{chars_json}\n\n"
        "TASK: Analyse the characters. Identify archetypes, potential conflicts, "
        "complementary relationships, and narrative arcs."
    )
    if user_question:
        base += f"\n\nUSER QUESTION: {user_question}"
    return base


def conflict_suggestions(ctx: UniverseContext, user_question: str | None = None) -> str:
    """Generate narrative conflict suggestions based on existing elements."""
    base = (
        f"You are a story architect for the universe '{ctx.universe.name}'.\n\n"
        f"UNIVERSE CONTEXT:\n{_context_summary(ctx)}\n\n"
        "TASK: Suggest 3-5 compelling narrative conflicts that could emerge naturally "
        "from the existing characters, factions, locations, and world rules. "
        "Be specific and reference the existing elements."
    )
    if user_question:
        base += f"\n\nUSER QUESTION: {user_question}"
    return base


def consistency_check(ctx: UniverseContext, user_question: str | None = None) -> str:
    """Identify logical inconsistencies in the universe."""
    base = (
        f"You are a continuity editor for the universe '{ctx.universe.name}'.\n\n"
        f"UNIVERSE CONTEXT:\n{_context_summary(ctx)}\n\n"
        "TASK: Identify any logical inconsistencies, contradictions, or world-building "
        "gaps. Report each finding concisely and suggest how to resolve it."
    )
    if user_question:
        base += f"\n\nUSER QUESTION: {user_question}"
    return base


def relationship_analysis(
    ctx: UniverseContext, user_question: str | None = None
) -> str:
    """Map likely relationships between entities."""
    base = (
        f"You are a relationship mapper for the universe '{ctx.universe.name}'.\n\n"
        f"UNIVERSE CONTEXT:\n{_context_summary(ctx)}\n\n"
        "TASK: Infer the most likely relationships between characters, organisations, "
        "and locations. Describe alliances, rivalries, dependencies, and hidden connections."
    )
    if user_question:
        base += f"\n\nUSER QUESTION: {user_question}"
    return base


def timeline_summary(ctx: UniverseContext, user_question: str | None = None) -> str:
    """Reconstruct a plausible timeline from the available lore."""
    base = (
        f"You are a historian of the universe '{ctx.universe.name}'.\n\n"
        f"UNIVERSE CONTEXT:\n{_context_summary(ctx)}\n\n"
        "TASK: Based on the characters, locations, organisations, and world rules, "
        "reconstruct a plausible chronological history. Label eras and key events."
    )
    if user_question:
        base += f"\n\nUSER QUESTION: {user_question}"
    return base


def story_expansion(ctx: UniverseContext, user_question: str | None = None) -> str:
    """Suggest new story directions grounded in existing lore."""
    base = (
        f"You are a creative consultant for the universe '{ctx.universe.name}'.\n\n"
        f"UNIVERSE CONTEXT:\n{_context_summary(ctx)}\n\n"
        "TASK: Propose 3 compelling story expansion ideas that build naturally on the "
        "existing lore, characters, and world rules. Each idea should feel organic "
        "and leverage existing elements."
    )
    if user_question:
        base += f"\n\nUSER QUESTION: {user_question}"
    return base


# ── Registry ───────────────────────────────────────────────────────────────────

PROMPT_REGISTRY: dict[str, object] = {
    "universe_summary": universe_summary,
    "lore_summary": lore_summary,
    "character_analysis": character_analysis,
    "conflict_suggestions": conflict_suggestions,
    "consistency_check": consistency_check,
    "relationship_analysis": relationship_analysis,
    "timeline_summary": timeline_summary,
    "story_expansion": story_expansion,
}
"""Maps string keys to prompt-builder functions. Used by ``AIService``."""


def get_prompt(key: str, ctx: UniverseContext, user_question: str | None = None) -> str:
    """Look up a template by key and render it with the given context."""
    fn = PROMPT_REGISTRY.get(key)
    if fn is None:
        available = ", ".join(PROMPT_REGISTRY.keys())
        raise ValueError(f"Unknown prompt key '{key}'. Available: {available}")
    return fn(ctx, user_question)  # type: ignore[call-arg]
