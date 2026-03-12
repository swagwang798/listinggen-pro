# io/readers.py
from __future__ import annotations
import csv
from typing import List
from engine.types import ListingInput


def read_csv(path: str, limit: int | None = None) -> List[ListingInput]:
    items: List[ListingInput] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit is not None and i >= limit:
                break
            items.append(
                ListingInput(
                    sku=row.get("sku", "") or row.get("SKU", "") or "",
                    source_title=row.get("title", "") or row.get("source_title", "") or "",
                    bullets=row.get("bullets", "") or "",
                    description=row.get("description", "") or "",
                    keywords=row.get("keywords", "") or "",
                    category=row.get("category", "") or "",
                    brand=row.get("brand", "") or "",
                    extra={k: v for k, v in row.items()},
                )
            )
    return items
