from listinggen.pipeline.pipeline import run_pipeline
from listinggen.engine.engine import ListingEngine
from listinggen.engine.types import ListingInput, GenTask
from listinggen.engine.provider_fake import FakeProvider  # ✅ 先用假的

def main():
    # 1) 造一个假的 provider（不花钱）
    provider = FakeProvider()

    # 2) 造 engine
    engine = ListingEngine(provider=provider, qps=None)

    # 3) 造 listing 输入
    listing = ListingInput(
        sku="SKU123",
        source_title="Wireless Earbuds Bluetooth 5.3 Noise Cancelling",
        bullets="Long battery life; Comfortable fit; Clear calls",
        description="High quality wireless earbuds with ENC for calls, charging case included.",
        keywords="wireless earbuds, bluetooth earbuds, noise cancelling",
        category="Electronics",
        brand="DemoBrand",
    )

    tasks = [GenTask("title"), GenTask("bullets"), GenTask("desc")]

    res = run_pipeline(engine, listing, tasks, required={"title"})
    print("OK:", res.ok)
    print("OUTPUTS:", res.outputs)
    print("META:", res.meta)

if __name__ == "__main__":
    main()