# engine/types.py
# 定义数据结构，不负责具体的实现
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
import time


@dataclass
class ListingInput:
    sku: str = ""
    source_title: str = ""
    bullets: str = ""
    description: str = ""
    keywords: str = ""
    category: str = ""
    brand: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenTask:
    # e.g. "title" / "bullets" / "desc"
    name: str


@dataclass
class ProviderResponse:
    text: str
    raw: Optional[Dict[str, Any]] = None
    usage: Optional[Dict[str, Any]] = None
    model: Optional[str] = None
    latency_ms: Optional[int] = None
    retry_count: int = 0  # 重试次数

@dataclass
class GenResult:
    sku: str
    task: str
    output_text: str
    ok: bool
    error: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunReport:
    task: str
    total: int
    ok: int
    failed: int
    elapsed_s: float
    results: List[GenResult]
