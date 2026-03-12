import listinggen.pipeline.pipeline as pl
import pytest
from types import SimpleNamespace
from listinggen.pipeline.pipeline import run_pipeline
from types import SimpleNamespace
from listinggen.pipeline.pipeline import run_pipeline

def _ok(text, lats=(10,)):
    return SimpleNamespace(ok=True, output_text=text, error=None, meta={"attempt_latencies_ms": list(lats)})

def _fail(err="boom", err_type="RuntimeError", lats=(5,)):
    return SimpleNamespace(
        ok=False,
        output_text="",
        error=err,
        meta={"attempt_latencies_ms": list(lats), "error_type": err_type},
    )

def test_non_required_fail_continues(mocker):
    tasks = [SimpleNamespace(name="title"), SimpleNamespace(name="bullets"), SimpleNamespace(name="desc")]
    listing = SimpleNamespace(sku="SKU2")

    engine = SimpleNamespace()
    engine.run_once = mocker.Mock(side_effect=[
        _ok("T"),
        _fail("bad bullets", "RuntimeError"),
        _ok("D"),
    ])

    result = run_pipeline(engine, listing, tasks, max_retries=0, required={"title"})  # bullets 非 required

    assert result.ok is False
    assert result.meta["tasks_run"] == ["title", "bullets", "desc"]
    assert result.outputs["title"] == "T"
    assert result.outputs["desc"] == "D"
    assert "bullets" in result.meta["tasks_failed"]
    assert result.meta["errors"]["bullets"] == "bad bullets"

def test_context_accumulates_and_is_passed(mocker):
    tasks = [SimpleNamespace(name="title"), SimpleNamespace(name="desc")]
    listing = SimpleNamespace(sku="SKU3")

    engine = SimpleNamespace()

    def fake_run_once(listing_arg, task_arg, *, context):
        if task_arg.name == "title":
            assert context == {}
            return _ok("TITLE_TEXT")
        if task_arg.name == "desc":
            assert context == {"title": "TITLE_TEXT"}
            return _ok("DESC_TEXT")
        raise AssertionError("unexpected task")

    engine.run_once = mocker.Mock(side_effect=fake_run_once)

    result = run_pipeline(engine, listing, tasks, max_retries=0)

    assert result.ok is True
    assert result.outputs == {"title": "TITLE_TEXT", "desc": "DESC_TEXT"}

def test_total_latency_ms_sum(mocker):
    tasks = [SimpleNamespace(name="title"), SimpleNamespace(name="desc")]
    listing = SimpleNamespace(sku="SKU4")

    engine = SimpleNamespace()
    engine.run_once = mocker.Mock(side_effect=[
        _ok("T", lats=(10, 20)),
        _ok("D", lats=(5,)),
    ])

    result = run_pipeline(engine, listing, tasks, max_retries=0)
    assert result.meta["total_latency_ms"] == 35

def test_retry_happens_for_retryable_error_and_sleep_is_mocked(mocker):
    task = SimpleNamespace(name="title")
    tasks = [task]
    listing = SimpleNamespace(sku="SKU5")
    engine = SimpleNamespace()

    # 第一次失败（可重试 RuntimeError），第二次成功
    engine.run_once = mocker.Mock(side_effect=[
        _fail("empty output", "RuntimeError", lats=(3,)),
        _ok("OK_TEXT", lats=(7,)),
    ])

    # 关键：mock 掉 sleep
    sleep_spy = mocker.patch.object(pl.time, "sleep")

    result = pl.run_pipeline(engine, listing, tasks, max_retries=1)

    assert result.ok is True
    assert engine.run_once.call_count == 2

    # 因为发生过一次重试，所以 sleep 应该被调用一次
    sleep_spy.assert_called_once()

    # attempts 和 attempt_latencies_ms 在 run_with_retry 汇总后写回
    r = result.results["title"]
    assert r.meta["attempts"] == 2
    assert r.meta["attempt_latencies_ms"] == [3, 7]


def test_retry_happens_for_retryable_error_and_sleep_is_mocked(mocker):
    task = SimpleNamespace(name="title")
    tasks = [task]
    listing = SimpleNamespace(sku="SKU5")
    engine = SimpleNamespace()

    engine.run_once = mocker.Mock(side_effect=[
        _fail(err="empty output", err_type="RuntimeError", lats=(3,)),
        _ok(text="OK_TEXT", lats=(7,)),
    ])

    sleep_spy = mocker.patch.object(pl.time, "sleep")

    result = pl.run_pipeline(engine, listing, tasks, max_retries=1)

    assert result.ok is True
    assert engine.run_once.call_count == 2
    sleep_spy.assert_called_once()

    r = result.results["title"]
    assert r.meta["attempts"] == 2
    assert r.meta["attempt_latencies_ms"] == [3, 7]

def test_no_retry_for_non_retryable_error(mocker):
    task = SimpleNamespace(name="title")
    tasks = [task]
    listing = SimpleNamespace(sku="SKU6")
    engine = SimpleNamespace()

    # ValueError 不在 RETRYABLE_ERRORS
    engine.run_once = mocker.Mock(side_effect=[
        _fail(err="bad", err_type="ValueError", lats=(4,)),
    ])

    sleep_spy = mocker.patch.object(pl.time, "sleep")

    result = pl.run_pipeline(engine, listing, tasks, max_retries=2)

    assert result.ok is False
    assert engine.run_once.call_count == 1
    sleep_spy.assert_not_called()

    r = result.results["title"]
    assert r.meta["attempts"] == 1
    assert r.meta["attempt_latencies_ms"] == [4]

def test_retry_exhausted_attempts_and_sleep_counts(mocker):
    task = SimpleNamespace(name="title")
    tasks = [task]
    listing = SimpleNamespace(sku="SKU7")
    engine = SimpleNamespace()

    engine.run_once = mocker.Mock(side_effect=[
        _fail(err="t1", err_type="RuntimeError", lats=(1,)),
        _fail(err="t2", err_type="RuntimeError", lats=(2,)),
        _fail(err="t3", err_type="RuntimeError", lats=(3,)),
    ])

    sleep_spy = mocker.patch.object(pl.time, "sleep")

    result = pl.run_pipeline(engine, listing, tasks, max_retries=2)

    assert result.ok is False
    assert engine.run_once.call_count == 3  # 2 retries -> 3 attempts
    assert sleep_spy.call_count == 2        # 重试两次才 sleep 两次

    r = result.results["title"]
    assert r.meta["attempts"] == 3
    assert r.meta["attempt_latencies_ms"] == [1, 2, 3]
