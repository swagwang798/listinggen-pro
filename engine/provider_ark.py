# engine/provider_ark.py
# 负责与Ark API交互，不负责具体的实现
from __future__ import annotations
import json
import os
import time
from typing import Any, Dict, List, Optional
import requests
from .provider_base import BaseProvider
from .types import ProviderResponse
from listinggen.engine.retry_policy import RetryPolicy, RetryConfig, RetryableError, NonRetryableError
from listinggen.engine.retry_profiles import get_retry_config

class ArkProvider(BaseProvider):
    """
    Minimal, stable Ark chat provider.
    Input: system_prompt + user_prompt
    Output: ProviderResponse(text, model, latency_ms, usage)
    """
    def _post_json_once(self, payload: dict) -> dict:
        timeout = httpx.Timeout(self.timeout_s)
        proxies = None
        if not self.disable_proxy:
            # httpx 默认会读环境变量代理；你如果要显式支持代理再扩展
            proxies = None

        with httpx.Client(timeout=timeout, proxies=proxies) as client:
            resp = client.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            # 让 4xx/5xx 变成 HTTPStatusError，交给 retry 判断 429/5xx
            resp.raise_for_status()
            return resp.json()


    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        timeout_s: int = 60,
        max_retries: int = 2,
        disable_proxy: bool = True,
    ) -> None:
        # ⚠️ 注意：pytest 跑 smoke 的时候我们不会实例化 ArkProvider（用 FakeProvider）
        # 所以这里即使要求 env，也不会影响 smoke test
        self.api_key = (api_key or os.getenv("ARK_API_KEY", "")).strip()
        self.model = (model or os.getenv("ARK_MODEL", "")).strip()
        self.endpoint = (endpoint or os.getenv("ARK_ENDPOINT", "")).strip() or \
            "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

        if not self.api_key:
            raise RuntimeError("ARK_API_KEY is not set")
        if not self.model:
            raise RuntimeError("ARK_MODEL is not set")

        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.disable_proxy = disable_proxy

        self._session = requests.Session()
        self._proxies = {"http": None, "https": None} if disable_proxy else None

    def generate(self, system_prompt: str, user_prompt: str) -> ProviderResponse:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        t0 = time.time()
        text = self.chat(messages)
        latency_ms = int((time.time() - t0) * 1000)

        return ProviderResponse(
            text=text,
            raw=None,
            usage=None,
            model=self.model,
            latency_ms=latency_ms,
        )

    def chat(
    self,
    messages: List[Dict[str, Any]],
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    ) -> str:
        cfg = RetryConfig(max_retries=self.max_retries + 1)  # 你原来是 +1 次总尝试
        return call_with_retry(
            lambda: self._chat_once(messages, temperature=temperature, max_tokens=max_tokens),
            cfg=cfg,
            on_retry=lambda n, e, s: print(f"[ArkProvider] retry {n} in {s:.2f}s due to: {type(e).__name__}: {e}"),
        )
    def _chat_once(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        policy = RetryPolicy(
            RetryConfig(max_retries=self.max_retries),
            on_retry=lambda n, err, s: print(
                f"[retry] #{n} sleep={s:.2f}s err={type(err).__name__}: {err}"
            ),
        )

        def _do_call():
            try:
                resp = self._session.post(
                    self.endpoint,
                    headers=headers,
                    data=json.dumps(payload, ensure_ascii=False),
                    timeout=self.timeout_s,
                )
            except (requests.Timeout, requests.ConnectionError) as e:
                raise RetryableError(str(e))

            if resp.status_code in (400, 401, 403):
                raise NonRetryableError(f"{resp.status_code}: {resp.text[:200]}")

            if resp.status_code == 429 or (500 <= resp.status_code < 600):
                raise RetryableError(f"{resp.status_code}: {resp.text[:200]}")

            if not (200 <= resp.status_code < 300):
                raise NonRetryableError(f"{resp.status_code}: {resp.text[:200]}")

            return resp

        resp, retry_count, total_s = policy.run(_do_call)
        logger.debug(
        f"ark chat retry={retry_count}, latency={int(total_s*1000)}ms"
        )

        data = resp.json()
        text = data["choices"][0]["message"]["content"]

        return ProviderResponse(
            text=text,
            model=self.model,
            latency_ms=int(total_s * 1000),
            retry_count=retry_count,
            usage=data.get("usage"),
        )