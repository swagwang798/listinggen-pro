import pytest
from listinggen.pipeline.pipeline import run_pipeline
from listinggen.engine.types import GenTask

def test_pipeline_context_injection(fake_engine, sample_listing):
    tasks = [
        GenTask("title"),
        GenTask("bullets"),
    ]

    res = run_pipeline(
        fake_engine,
        sample_listing,
        tasks,
        required={"title"},
    )

    assert res.results["title"].ok
    assert res.results["bullets"].ok

    # 关键断言：bullets 的 meta 或 output 来自 title
    bullets_output = res.outputs["bullets"]
    title_output = res.outputs["title"]

    assert title_output[:20] in bullets_output or title_output in bullets_output
