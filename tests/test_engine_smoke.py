# tests/test_engine_smoke.py
# 测试ListingEngine的基本功能
from listinggen.engine.engine import ListingEngine
from listinggen.engine.provider_fake import FakeProvider
from listinggen.engine.types import ListingInput, GenTask
from listinggen.engine.engine import ListingEngine
from listinggen.engine.provider_fake import FakeProvider
from listinggen.engine.types import ListingInput, GenTask

engine1 = ListingEngine(provider=FakeProvider(sleep_ms=200))
listings = [ListingInput(sku=f"A{i:03d}", source_title="x") for i in range(20)]
task = GenTask(name="title")

r_serial = engine1.run_batch(listings, task, concurrency=1)
r_conc = engine1.run_batch(listings, task, concurrency=10)

print("serial:", r_serial.elapsed_s)
print("conc10:", r_conc.elapsed_s)

def test_engine_smoke():
    engine = ListingEngine(provider=FakeProvider())

    listings = [
        ListingInput(sku="A001", source_title="Women's winter beanie hat", keywords="beanie,winter"),
        ListingInput(sku="A002", source_title="Stainless steel water bottle 1L", keywords="bottle,steel,1L"),
    ]

    task = GenTask(name="title")
    report = engine.run_batch(listings, task)

    assert report.total == 2
    assert report.ok + report.failed == 2
    assert report.ok >= 1  # fake provider 一般都会 ok=2
    assert len(report.results) == 2
    assert all(r.sku for r in report.results)
