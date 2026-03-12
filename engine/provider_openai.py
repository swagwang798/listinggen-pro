# engine/provider_openai.py
from __future__ import annotations

import os
import time

from engine.provider_base import BaseProvider
from engine.types import ProviderResponse

# 需要：pip install openai
from openai import OpenAI


class OpenAIProvider(BaseProvider):
    def __init__(self, model: str | None = None, timeout_s: int = 30):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout_s = timeout_s

    def generate(self, system_prompt: str, user_prompt: str) -> ProviderResponse:
        t0 = time.time()

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            timeout=self.timeout_s,
        )

        latency_ms = int((time.time() - t0) * 1000)
        text = resp.choices[0].message.content or ""

        usage = {}
        if getattr(resp, "usage", None):
            usage = {
                "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
                "completion_tokens": getattr(resp.usage, "completion_tokens", None),
                "total_tokens": getattr(resp.usage, "total_tokens", None),
            }

        return ProviderResponse(
            text=text,
            raw=resp.model_dump() if hasattr(resp, "model_dump") else None,
            usage=usage,
            model=self.model,
            latency_ms=latency_ms,
        )
