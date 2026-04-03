PROMPT_APPEND_BASE = """
Execution policy:
- If MCP servers or Skills are available and relevant, proactively use them.
- Prefer Skill and MCP capabilities over manual reimplementation when they can solve the task directly.
- If the task involves Chinese laws, regulations, judicial interpretations, or court cases, prefer the `legal-search` MCP tools first.
- For legal research tasks, search authoritative legal materials before answering from general model knowledge.
- When both `search_law` and `search_case` are available, prefer `search_law` for legal basis and `search_case` for judicial practice.
""".strip()

PROMPT_APPEND_BROWSER_ENABLED = """
Browser capability note:
- Built-in browser capability is enabled for this task.
- Use browser tools when web inspection or web interaction helps.
""".strip()

PROMPT_APPEND_MEMORY_ENABLED = """
Memory capability note:
- Built-in user-level memory tools are enabled for this task.
- Search relevant memory before re-asking the user, and store durable preferences/facts when useful.
""".strip()


def build_prompt_appendix(
    *, browser_enabled: bool, memory_enabled: bool = False
) -> str:
    """Build the static prompt appendix for current capability flags."""
    sections = [PROMPT_APPEND_BASE]
    if memory_enabled:
        sections.append(PROMPT_APPEND_MEMORY_ENABLED)
    if browser_enabled:
        sections.append(PROMPT_APPEND_BROWSER_ENABLED)
    return "\n\n".join(sections)
