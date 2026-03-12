from listinggen.pipeline.pipeline import run_pipeline
from listinggen.engine.types import GenTask, ListingInput

tasks = [GenTask("title"), GenTask("bullets"), GenTask("desc")]

listing = ListingInput(
    sku="SKU123",
    source_title="Original title ...",
    bullets="...",
    description="...",
    keywords="...",
    category="...",
    brand="...",
)

res = run_pipeline(engine, listing, tasks, max_retries=2, required={"title"})
print(res.ok)
print(res.outputs)
print(res.meta)
