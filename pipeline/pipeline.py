# listinggen/pipeline/pipeline.py
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List

from listinggen.engine.types import ListingInput, GenTask, GenResult


# 你 scripts/pipeline.py 里应该已有这些
RETRYABLE_ERRORS = {
    "TimeoutError",
    "ConnectionError",
    "RuntimeError",     # 你现在 Empty model output 是 RuntimeError
    # "RateLimitError", # 如果你 limiter/ provider 有这个错误类型再加
}

BACKOFF_S = [0.5, 1.0, 2.0]

def should_retry(result: GenResult) -> bool:
    if result.ok:
        return False
    err_type = (result.meta or {}).get("error_type", "")
    return err_type in RETRYABLE_ERRORS


def run_with_retry(engine, listing, task, *, context: dict[str, str], max_retries=2) -> GenResult:
    """
    用 Engine.run_once 做 runner。
    重点：把每次 attempt 的 latency 汇总成一个列表，写回 meta。
    """
    last: GenResult | None = None
    attempt_latencies_all: list[int] = []

    for attempt in range(max_retries + 1):
        r = engine.run_once(listing, task, context=context)
        last = r

        # engine.run_once 每次返回的 meta 里 attempt_latencies_ms 只有一次调用的耗时
        lat_list = (r.meta or {}).get("attempt_latencies_ms", [])
        if isinstance(lat_list, list):
            attempt_latencies_all.extend(int(x) for x in lat_list if isinstance(x, (int, float)))

        if r.ok:
            r.meta = dict(r.meta or {})
            r.meta["attempt_latencies_ms"] = attempt_latencies_all
            r.meta["attempts"] = attempt + 1
            return r

        if not should_retry(r):
            r.meta = dict(r.meta or {})
            r.meta["attempt_latencies_ms"] = attempt_latencies_all
            r.meta["attempts"] = attempt + 1
            return r

        # 可重试且没用完次数：backoff
        if attempt < max_retries:
            time.sleep(BACKOFF_S[min(attempt, len(BACKOFF_S) - 1)])

    assert last is not None
    last.meta = dict(last.meta or {})
    last.meta["attempt_latencies_ms"] = attempt_latencies_all
    last.meta["attempts"] = max_retries + 1
    return last


@dataclass
class PipelineResult:
    sku: str
    ok: bool
    outputs: Dict[str, str]          # task.name -> output_text
    results: Dict[str, GenResult]    # task.name -> GenResult
    meta: Dict[str, Any]             # 汇总错误、耗时等


def run_pipeline(
    engine,
    listing: ListingInput,
    tasks: List[GenTask],
    *,
    max_retries: int = 2,
    required: set[str] | None = None,
) -> PipelineResult:
    required = required or set()

    outputs = {}
    results = {}
    errors = {}

    context: dict[str, str] = {}   # ✅ 新增：跨 task 上下文

    total_latency_ms = 0
    ok_all = True

    for task in tasks:
        # ✅ 关键变化：把 context 传进去
        r = run_with_retry(engine, listing, task, context=context, max_retries=max_retries)

        results[task.name] = r

        lat = (r.meta or {}).get("attempt_latencies_ms", [])
        if isinstance(lat, list):
            total_latency_ms += sum(lat)

        if r.ok:
            outputs[task.name] = r.output_text
            context[task.name] = r.output_text   # ✅ 写入 context
        else:
            ok_all = False
            errors[task.name] = r.error
            if task.name in required:
                break
    meta = {
    "errors": errors,
    "total_latency_ms": total_latency_ms,
    "tasks_run": list(results.keys()),
    "tasks_ok": [k for k, v in results.items() if v.ok],
    "tasks_failed": [k for k, v in results.items() if not v.ok],
    }
    return PipelineResult(
        sku=listing.sku,
        ok=ok_all,
        outputs=outputs,
        results=results,
        meta=meta,
    )