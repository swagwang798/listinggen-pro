from __future__ import annotations
from dataclasses import dataclass

from .retry_policy import RetryConfig, BackoffConfig

# 你现在的 retry_policy.py 里如果 BackoffConfig 叫别的名字，按实际改一下

PROFILES: dict[str, RetryConfig] = {
    # 默认：稳一点但不拖
    "default": RetryConfig(
        max_retries=2,
        backoff=BackoffConfig(base_s=0.25, factor=2.0, jitter_s=0.15, max_sleep_s=3.0),
    ),
    # 激进：网络抖/限流多时更抗
    "aggressive": RetryConfig(
        max_retries=4,
        backoff=BackoffConfig(base_s=0.3, factor=2.0, jitter_s=0.2, max_sleep_s=6.0),
    ),
    # 快速失败：交互/调试用，不浪费时间
    "fast_fail": RetryConfig(
        max_retries=0,
        backoff=BackoffConfig(base_s=0.0, factor=1.0, jitter_s=0.0, max_sleep_s=0.0),
    ),
}

def get_retry_config(name: str | None) -> RetryConfig:
    if not name:
        return PROFILES["default"]
    return PROFILES.get(name, PROFILES["default"])
