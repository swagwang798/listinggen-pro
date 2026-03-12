# listinggen/engine/retry.py
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar

import requests

T = TypeVar("T")


@dataclass(frozen=True)
class RetryConfig:
    max_retries: int = 3          # 最多尝试次数（总次数）
    base_delay_s: float = 0.5
    max_delay_s: float = 6.0
    jitter_ratio: float = 0.2


def _backoff_seconds(cfg: RetryConfig, attempt: int) -> float:
    delay = cfg.base_delay_s * (2 ** attempt)
    delay = min(delay, cfg.max_delay_s)
    jitter = delay * cfg.jitter_ratio * (random.random() * 2 - 1)  # [-ratio, +ratio]
    return max(0.0, delay + jitter)


def is_retryable_exception(exc: Exception) -> bool:
    # 网络/超时：可重试
    if isinstance(exc, (requests.Timeout, requests.ConnectionError)):
        return True

    # 我们会在 provider 抛出 RuntimeError("Ark HTTP xxx: ...")
    # 这里兜底识别 429/5xx（简单但够用）
    if isinstance(exc, RuntimeError):
        msg = str(exc)
        # 你当前的错误格式： "Ark HTTP {code}: ..."
        if msg.startswith("Ark HTTP "):
            try:
                code = int(msg.split()[2].rstrip(":"))
            except Exception:
                return False
            if code == 429:
                return True
            if 500 <= code <= 599:
                return True
        return False

    return False


def call_with_retry(
    fn: Callable[[], T],
    cfg: RetryConfig,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
) -> T:
    last_exc: Optional[Exception] = None

    for attempt in range(cfg.max_retries):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            if not is_retryable_exception(exc):
                raise
            last_exc = exc
            if attempt == cfg.max_retries - 1:
                break
            sleep_s = _backoff_seconds(cfg, attempt)
            if on_retry:
                on_retry(attempt + 1, exc, sleep_s)
            time.sleep(sleep_s)

    assert last_exc is not None
    raise last_exc
