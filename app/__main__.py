# app/__main__.py
from __future__ import annotations
import argparse

from engine.engine import ListingEngine
from engine.types import GenTask
from engine.provider_fake import FakeProvider  # 先用 fake 跑通
from storage.readers import read_csv
from storage.writers import write_report_csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_path", required=True, help="input csv path")
    parser.add_argument("--out", dest="out_path", required=True, help="output csv path")
    parser.add_argument("--task", dest="task", required=True, choices=["title", "bullets", "desc"])
    parser.add_argument("--limit", dest="limit", type=int, default=None)
    parser.add_argument("--provider", choices=["fake", "ark"], default="fake")
    args = parser.parse_args()

    listings = read_csv(args.in_path, limit=args.limit)

    if args.provider == "fake":
        provider = FakeProvider()
    else:
        from listinggen.engine.provider_ark import ArkProvider
        provider = ArkProvider()

        
    engine = ListingEngine(provider=provider, max_retries=1)

    report = engine.run_batch(listings, GenTask(name=args.task))
    write_report_csv(args.out_path, report)

    print(f"[DONE] task={report.task} total={report.total} ok={report.ok} failed={report.failed} elapsed={report.elapsed_s:.2f}s")
    if report.failed:
        print("[WARN] Some items failed. Check output CSV for errors.")


if __name__ == "__main__":
    main()

# 如果有失败，打印前3条错误，省得总去翻csv
if report.failed:
    print("\n[FAILURES] showing up to 3 errors:")
    shown = 0
    for r in report.results:
        if not r.ok:
            print(f"- sku={r.sku} error={r.error}")
            shown += 1
            if shown >= 3:
                break
