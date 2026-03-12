# engine/engine.py
# 只负责流程控制和结果返回；不负责 retry / backoff / attempt 统计

from __future__ import annotations
import time
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .rate_limit import RateLimiter
from .provider_base import BaseProvider
from .renderer import render_prompt
from .types import ListingInput, GenTask, GenResult, RunReport
from listinggen.pipeline.postprocess import extract_output

class ListingEngine:
    def __init__(self, provider: BaseProvider, qps: float | None = None):
        self.provider = provider
        self._limiter = RateLimiter(qps) if qps is not None else None

    def run_once(
        self,
        listing: ListingInput,
        task: GenTask,
        context: dict[str, str] | None = None
    ) -> GenResult:
        system_prompt, user_prompt = render_prompt(listing, task, context)
        print("===TASK===", task.name)
        print(user_prompt[:800])  # 只看前800字符

        t0 = time.time()
        try:
            if self._limiter is not None:
                self._limiter.acquire()

            resp = self.provider.generate(system_prompt, user_prompt)

            total_latency_ms = int((time.time() - t0) * 1000)

            text = (getattr(resp, "text", "") or "").strip()
            if not text:
                raise RuntimeError("Empty model output")

            # enforce OUTPUT protocol
            text = extract_output(text)

            # 如果 provider 自己带了 meta，就透传；否则至少把总耗时带上
            meta = dict(getattr(resp, "meta", {}) or {})
            meta.setdefault("total_latency_ms", total_latency_ms)

            return GenResult(
                sku=listing.sku,
                task=task.name,
                output_text=text,
                ok=True,
                error="",
                meta=meta,
            )
        except Exception as e:
            total_latency_ms = int((time.time() - t0) * 1000)
            return GenResult(
                sku=listing.sku,
                task=task.name,
                output_text="",
                ok=False,
                error=str(e),
                meta={
                    "error_type": type(e).__name__,
                    "total_latency_ms": total_latency_ms,
                },
            )

    def run_batch(
        self,
        listings: list[ListingInput],
        task: GenTask,
        concurrency: int = 1,
        keep_order: bool = True,
    ) -> RunReport:
        t0 = time.time()
        total = len(listings)

        if total == 0:
            return RunReport(task=task.name, total=0, ok=0, failed=0, elapsed_s=0.0, results=[])

        # 串行
        if concurrency <= 1:
            results: list[GenResult] = []
            ok = 0
            failed = 0
            for item in listings:
                r = self.run_once(item, task)
                results.append(r)
                if r.ok:
                    ok += 1
                else:
                    failed += 1
            return RunReport(
                task=task.name,
                total=total,
                ok=ok,
                failed=failed,
                elapsed_s=time.time() - t0,
                results=results,
            )

        # 并发
        workers = min(concurrency, total)
        ok = 0
        failed = 0

        results_ordered: Optional[list[Optional[GenResult]]] = [None] * total if keep_order else None
        results_unordered: list[GenResult] = [] if not keep_order else []

        def _work(idx: int, item: ListingInput) -> tuple[int, GenResult]:
            return idx, self.run_once(item, task)

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(_work, i, item) for i, item in enumerate(listings)]
            for fut in as_completed(futures):
                idx, r = fut.result()

                if keep_order:
                    assert results_ordered is not None
                    results_ordered[idx] = r
                else:
                    results_unordered.append(r)

                if r.ok:
                    ok += 1
                else:
                    failed += 1

        if keep_order:
            assert results_ordered is not None
            final_results = [r for r in results_ordered if r is not None]
        else:
            final_results = results_unordered

        return RunReport(
            task=task.name,
            total=total,
            ok=ok,
            failed=failed,
            elapsed_s=time.time() - t0,
            results=final_results,
        )
