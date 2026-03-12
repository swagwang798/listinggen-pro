from listinggen.engine.engine import ListingEngine
from listinggen.engine.provider_ark import ArkProvider
from listinggen.engine.types import ListingInput, GenTask

def main():
    listings = [ListingInput(sku=f"A{i:03d}", source_title="x") for i in range(20)]
    task = GenTask(name="title")

    # 假设每次请求很快（sleep=0），我们只测限速器
    engine = ListingEngine(provider=ArkProvider(sleep_ms=0), max_retries=0, qps=5)

    r = engine.run_batch(listings, task, concurrency=20)
    print("total:", r.total, "elapsed:", round(r.elapsed_s, 2), "s")
if __name__ == "__main__":
    main()
