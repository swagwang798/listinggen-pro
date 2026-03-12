# listinggen/scripts/bench_concurrency.py
# 测试不同并发度下的性能
from listinggen.engine.engine import ListingEngine
from listinggen.engine.provider_fake import FakeProvider
from listinggen.engine.types import ListingInput, GenTask


listings = [ListingInput(sku=f"A{i:03d}", source_title="x") for i in range(40)]
task = GenTask(name="title")

for c in [1, 2, 5, 10, 20]:
    engine = ListingEngine(FakeProvider(sleep_ms=200), max_retries=0)    
    r = engine.run_batch(listings, task, concurrency=c)
    print(f"concurrency={c:>2}  elapsed={r.elapsed_s:.2f}s")
