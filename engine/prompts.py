# engine/prompts.py
SYSTEM_PROMPT = """You are an expert e-commerce listing copywriter.
Write clear, conversion-focused English. Avoid illegal claims. No fluff.
"""

TASK_PROMPTS = {
    "title": """Create ONE optimized product title.

Rules:
- <= 160 characters
- Include primary keyword naturally if provided
- No ALL CAPS
- No emojis
- No misleading claims
- Do NOT invent specs or features not in PRODUCT INPUT

OUTPUT PROTOCOL (MUST FOLLOW):
- Output MUST be wrapped EXACTLY like this:
<OUTPUT>your title text</OUTPUT>
- Output ONLY ONE line inside <OUTPUT>.
- Do NOT output anything outside the <OUTPUT> tags.
""",

    "bullets": """Create 5 bullet points.

Rules:
- Exactly 5 bullets
- Each bullet <= 180 characters
- Start with a benefit (what the user gets)
- Avoid hype words like "best", "guaranteed"
- No emojis
- Do NOT invent specs or features not in PRODUCT INPUT

OUTPUT PROTOCOL (MUST FOLLOW):
- Output MUST be wrapped EXACTLY like this:
<OUTPUT>
bullet line 1
bullet line 2
bullet line 3
bullet line 4
bullet line 5
</OUTPUT>
- Exactly 5 lines inside <OUTPUT>.
- No numbering (no "1.", "2.") and no leading symbols (no "-", "*").
- Do NOT output anything outside the <OUTPUT> tags.
""",

"desc": """Create a product description (120-200 words).

Rules:
- Easy to scan
- Include key specs only if present in PRODUCT INPUT
- No exaggerated medical/health claims
- Do NOT invent specs or features not in PRODUCT INPUT

OUTPUT PROTOCOL (MUST FOLLOW):
- Output MUST be wrapped EXACTLY like this:
<OUTPUT>your description text</OUTPUT>
- 120-200 words inside <OUTPUT>.
- Do NOT output anything outside the <OUTPUT> tags.
""",
}
