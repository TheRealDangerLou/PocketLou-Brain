"""
Prompt Builder — assembles the full system prompt for each request.

The system prompt is the core of Pocket Lou's intelligence.
It injects Lou's identity, the right profile slice, relevant memories,
and mode-specific instructions — all in the right order.
"""

from __future__ import annotations

from brain.modes import get_mode


_BASE_IDENTITY = """\
You are Pocket Lou — the private, sovereign AI intelligence of Louis "Louie" Octeau Piché.

You are not an assistant. You are not a product. You are not available to anyone else.
You are a second Lou — faster, quieter, always ready.
His closest confidant, built into a device he wears on his hip, engraved with RLL.

RLL: Rose. Lily. Levi. His children. That is why you exist.\
"""

_GOLDEN_RULES = """\
GOLDEN RULES — non-negotiable:
- Privacy above all. You serve one operator. Only Lou.
- Offline first. You function without the cloud.
- Sound human. Never robotic. Never corporate. Never hedge for no reason.
- Know Lou. Every response is informed by who he is.
- No filler. No "As an AI..." No disclaimers that serve no one.
- Be fast. Lou needs answers, not essays. Match his tempo.
- RLL always. Rose, Lily, Levi. The why behind everything.\
"""


def _format_profile(profile: dict) -> str:
    lines = ["WHO LOU IS:"]

    if "identity" in profile:
        idn = profile["identity"]
        lines.append(f"- Name: {idn.get('name', 'Louis Octeau Piché')} (Louie)")
        if "location" in idn:
            lines.append(f"- Location: {idn['location']}")

    if "career" in profile:
        career = profile["career"]
        lines.append(f"- Career: {career.get('primary', 'Full-time actor')}")
        if "rep" in career:
            r = career["rep"]
            lines.append(f"- Rep: {r['name']} — {r['agency']}, {r['city']}")

    if "languages" in profile:
        lang_str = ", ".join(
            f"{lang} ({level})" for lang, level in profile["languages"].items()
        )
        lines.append(f"- Languages: {lang_str}")

    if "family" in profile:
        fam = profile["family"]
        wife = fam.get("wife", "Mackenzie")
        children = fam.get("children", [])
        child_parts = []
        for c in children:
            if "age_approx" in c:
                child_parts.append(f"{c['name']} (~{c['age_approx']})")
            else:
                child_parts.append(f"{c['name']} ({c.get('status', '')})")
        lines.append(f"- Family: {wife} (wife), {', '.join(child_parts)}")

    if "sobriety" in profile:
        sob = profile["sobriety"]
        if sob.get("sober"):
            lines.append(f"- Sober: Yes. {sob.get('significance', 'Core to his identity.')}")

    if "spiritual_framework" in profile:
        sf = profile["spiritual_framework"]
        lines.append(f"- Spiritual framework: {', '.join(sf)}")

    if "active_projects" in profile:
        lines.append("- Active projects:")
        for proj in profile["active_projects"]:
            lines.append(f"  · {proj['name']} — {proj['description']}")

    if "values" in profile:
        lines.append(f"- Core values: {', '.join(profile['values'])}")

    if "voice_and_communication" in profile:
        vc = profile["voice_and_communication"]
        if "style" in vc:
            lines.append(f"- How he communicates: {vc['style']}")
        if "dislikes" in vc:
            lines.append(f"- He hates: {', '.join(vc['dislikes'])}")
        if "prefers" in vc:
            lines.append(f"- He prefers: {', '.join(vc['prefers'])}")

    return "\n".join(lines)


def _format_memories(memories: list[str]) -> str:
    if not memories:
        return ""
    lines = ["RELEVANT CONTEXT FROM MEMORY:"]
    for mem in memories:
        truncated = mem[:300].strip()
        if truncated:
            lines.append(f"- {truncated}")
    return "\n".join(lines)


class PromptBuilder:
    def __init__(self, config: dict):
        self._config = config

    def build_system_prompt(
        self,
        mode: str,
        profile: dict,
        memories: list[str],
    ) -> str:
        mode_instance = get_mode(mode)
        parts: list[str] = []

        parts.append(_BASE_IDENTITY)

        profile_text = _format_profile(profile)
        if profile_text:
            parts.append(profile_text)

        memories_text = _format_memories(memories)
        if memories_text:
            parts.append(memories_text)

        parts.append(_GOLDEN_RULES)

        mode_additions = mode_instance.system_prompt_additions
        if mode_additions:
            parts.append(f"CURRENT MODE — {mode}:\n{mode_additions}")

        return "\n\n".join(parts)

    def build_messages(
        self,
        session_history: list[dict],
        user_input: str,
    ) -> list[dict]:
        messages = list(session_history)
        messages.append({"role": "user", "content": user_input})
        return messages
