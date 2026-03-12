from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Optional, TypeVar, Tuple

T = TypeVar("T")


# 你可以按需扩展，但今天先够用
class RetryableError(Exception):
    """瞬时失败：可重试（超时/429/网络抖动等）"""


class NonRetryableError(Exception):
    """确定性失败：禁止重试（参数错/鉴权错/输入非法等）"""


@dataclass(frozen=True)
class BackoffConfig:
    base_s: float = 0.25
    factor: float = 2.0
    jitter_s: float = 0.15
    max_sleep_s: float = 3.0


@dataclass(frozen=True)
class RetryConfig:
    max_retries: int = 2
    backoff: BackoffConfig = BackoffConfig()


def _sleep_seconds(cfg: BackoffConfig, attempt: int) -> float:
    # attempt: 0 表示第一次失败后的等待
    delay = cfg.base_s * (cfg.factor ** attempt)
    delay += random.uniform(0, cfg.jitter_s)
    return min(delay, cfg.max_sleep_s)


class RetryPolicy:
    """
    把“重试”工程化：
    - 只重试你允许的错误类型
    - 指数退避 + 抖动
    - 每次尝试/等待都能打点
    """

    def __init__(
        self,
        config: RetryConfig,
        *,
        is_retryable: Optional[Callable[[BaseException], bool]] = None,
        on_retry: Optional[Callable[[int, BaseException, float], None]] = None,
        on_giveup: Optional[Callable[[int, BaseException], None]] = None,
    ) -> None:
        self.config = config
        self.is_retryable = is_retryable or self._default_is_retryable
        self.on_retry = on_retry
        self.on_giveup = on_giveup

    @staticmethod
    def _default_is_retryable(err: BaseException) -> bool:
        return isinstance(err, RetryableError)

    def run(self, fn: Callable[[], T]) -> Tuple[T, int, float]:
        """
        返回：(结果, 重试次数, 总耗时)
        """
        start = time.time()
        retries = 0

        # max_retries=2 => 最多尝试 1(初次) + 2(重试) = 3 次
        for attempt in range(self.config.max_retries + 1):
            try:
                out = fn()
                total = time.time() - start
                return out, retries, total
            except BaseException as e:
                # 确定性失败：立刻抛
                if isinstance(e, NonRetryableError):
                    raise

                # 不可重试：立刻抛
                if not self.is_retryable(e):
                    raise

                # 可重试：看是否还有次数
                if attempt >= self.config.max_retries:
                    if self.on_giveup:
                        self.on_giveup(retries, e)
                    raise

                sleep_s = _sleep_seconds(self.config.backoff, attempt)
                retries += 1
                if self.on_retry:
                    self.on_retry(retries, e, sleep_s)
                time.sleep(sleep_s)

        # 理论上不会走到这
        raise RuntimeError("RetryPolicy.run fell through unexpectedly")
