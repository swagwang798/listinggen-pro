# engine/provider_fake.py
# 负责模拟Provider的行为，不负责具体的实现
from __future__ import annotations
import re

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .provider_base import BaseProvider
from .types import ProviderResponse


class FakeProvider(BaseProvider):
    """
    A deterministic provider for unit tests.
    - No network
    - Optional sleep to simulate latency (useful to see concurrency speedup)
    """

    def __init__(self, sleep_ms: int = 0, model: str = "fake") -> None:
        self.sleep_ms = int(sleep_ms)
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> ProviderResponse:
        if self.sleep_ms > 0:
            time.sleep(self.sleep_ms / 1000.0)

        # 1) 尝试从 prompt 里提取 "PREVIOUS OUTPUTS" 下的 TITLE
        injected_title = ""
        m = re.search(r"\[PREVIOUS OUTPUTS\].*?TITLE:\s*(.+)", user_prompt, flags=re.S)
        if m:
            injected_title = m.group(1).strip()
            # 别太长，防止污染输出（也让断言更稳定）
            injected_title = injected_title[:120]

        # 2) 构造稳定输出：包含头部片段 + 注入的 title 痕迹
        head = user_prompt[:80].replace("\n", " ")
        if injected_title:
            text = f"<OUTPUT>[FAKE:{self.model}] head={head} | injected_title={injected_title}</OUTPUT>"
        else:
            text = f"<OUTPUT>[FAKE:{self.model}] head={head}</OUTPUT>"

        return ProviderResponse(
            text=text,
            raw={"system_prompt_len": len(system_prompt), "user_prompt_len": len(user_prompt)},
            usage={"prompt_tokens": None, "completion_tokens": None, "total_tokens": None},
            model=self.model,
            latency_ms=self.sleep_ms,
        )
