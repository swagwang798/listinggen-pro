# engine/renderer.py
from __future__ import annotations
from typing import Tuple
from .types import ListingInput, GenTask
from .prompts import SYSTEM_PROMPT, TASK_PROMPTS
DEPENDENCIES = {
    "title": [],
    "bullets": ["title"],   
    "desc": ["title", "bullets"],
}

def render_prompt(
    listing: ListingInput,
    task: GenTask,
    context: dict[str, str] | None = None
) -> tuple[str, str]:
    """
    Returns: (system_prompt, user_prompt)
    """
    task_prompt = TASK_PROMPTS.get(task.name)
    context = context or {}
    history = ""
    if context:
        history = "\n\n[PREVIOUS OUTPUTS]\n"
        deps = DEPENDENCIES.get(task.name, [])
        for k in deps:
            if k in context:
                history += f"{k.upper()}:\n{context[k]}\n"


    if not task_prompt:
        raise ValueError(f"Unknown task: {task.name}")

    # 你后续可以把这块做成更精致的模板
    user_prompt = f"""
    {task_prompt}
    {history}
    
[PRODUCT INPUT]
SKU: {listing.sku}
Title: {listing.source_title}
Bullets: {listing.bullets}          
Description: {listing.description}
Keywords: {listing.keywords}
Category: {listing.category}
Brand: {listing.brand}

[OUTPUT]
Follow the OUTPUT PROTOCOL in the task instructions exactly.
""".strip()

    return SYSTEM_PROMPT.strip(), user_prompt