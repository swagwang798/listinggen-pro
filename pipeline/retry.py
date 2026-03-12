from __future__ import annotations
from typing import Optional

from listinggen.engine.types import ListingInput, GenTask, GenResult
from listinggen.engine.engine import ListingEngine


def run_with_retry(
    engine: ListingEngine,
    listing: ListingInput,
    task: GenTask,
    max_retries: int,
) -> GenResult:
    """
    策略层：决定重试
    - max_retries=0 表示只跑一次
    """
    attempt_latencies: list[int] = []
    last: Optional[GenResult] = None

    for attempt in range(max_retries + 1):
        r = engine.run_once(listing, task)
        last = r

        # 聚合每次 latency
        lat = (r.meta or {}).get("attempt_latencies_ms", [])
        if isinstance(lat, list):
            attempt_latencies.extend(lat)

        if r.ok:
            # 成功：把“策略信息”写进 meta（这是 pipeline 的权力）
            r.meta = dict(r.meta or {})
            r.meta.update(
                {
                    "retry_count": attempt,
                    "attempt_latencies_ms": attempt_latencies,
                }
            )
            return r

    # 全失败：同样把策略信息写进去
    assert last is not None
    last.meta = dict(last.meta or {})
    last.meta.update(
        {
            "retry_count": max_retries + 1,
            "attempt_latencies_ms": attempt_latencies,
        }
    )
    return last
