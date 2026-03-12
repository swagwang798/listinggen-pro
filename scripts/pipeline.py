from listinggen.engine.types import ListingInput, GenTask, GenResult
import time

BACKOFF_S = [0.2, 0.5, 1.0]

RETRYABLE_ERRORS = {
    "TimeoutError",
    "ConnectionError",
    "RuntimeError",  # 如果你把一些临时错误包装成 RuntimeError
    # "RateLimitError",
}

def should_retry(result: GenResult) -> bool:
    if result.ok:
        return False
    err_type = (result.meta or {}).get("error_type", "")
    return err_type in RETRYABLE_ERRORS


def run_with_retry(runner, listing: ListingInput, task: GenTask) -> GenResult:
    last_result: GenResult | None = None

    for attempt in range(runner.max_retries + 1):
        result = runner.run_one(listing, task)
        last_result = result

        if result.ok:
            return result

        # 不可重试错误：直接返回失败结果（别浪费钱）
        if not should_retry(result):
            return result

        # 走到这里 = 这次失败且可重试，且还没用完次数 → backoff
        if attempt < runner.max_retries:
            time.sleep(BACKOFF_S[min(attempt, len(BACKOFF_S) - 1)])

    # 理论上不会是 None（至少跑一次），但保守一点更工程
    assert last_result is not None
    return last_result
