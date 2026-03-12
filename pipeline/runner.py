# listinggen/pipeline/runner.py
import time
from listinggen.engine.engine import Engine
from listinggen.engine.types import ListingInput, GenTask, GenResult

BACKOFF_S = [0.5, 1.0, 2.0]

class Runner:
    def __init__(self, engine: Engine, max_retries: int = 2):
        self.engine = engine
        self.max_retries = max_retries

    def run_one(self, listing: ListingInput, task: GenTask) -> GenResult:
        return self.engine.run_once(listing, task)

    def should_retry(self, r: GenResult) -> bool:
        # 先用你原来的 RETRYABLE_ERRORS 判断
        err_type = (r.meta or {}).get("error_type", "")
        return err_type in {"TimeoutError", "RateLimitError", "ConnectionError", "RuntimeError"}

    def backoff(self, attempt: int) -> None:
        time.sleep(BACKOFF_S[min(attempt, len(BACKOFF_S) - 1)])
