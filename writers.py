# io/writers.py
from __future__ import annotations
import csv
from typing import List
from engine.types import RunReport


def write_report_csv(path: str, report: RunReport) -> None:
    fieldnames = ["sku", "task", "ok", "output_text", "error", "latency_ms", "model"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in report.results:
            w.writerow({
                "sku": r.sku,
                "task": r.task,
                "ok": r.ok,
                "output_text": r.output_text,
                "error": r.error,
                "latency_ms": r.meta.get("latency_ms", ""),
                "model": r.meta.get("model", ""),
            })