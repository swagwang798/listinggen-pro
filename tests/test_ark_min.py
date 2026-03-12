# listinggen/tests/test_ark_min.py
from __future__ import annotations

from listinggen.engine.provider_ark import ArkProvider


def main() -> None:
    # 故意把 timeout 调到极小，强制触发超时 -> 触发 retry
    p = ArkProvider(timeout_s=0.001, max_retries=2)

    text = p.chat(
        messages=[{"role": "user", "content": "ping"}],
        temperature=0.2,
    )
    print(text)


if __name__ == "__main__":
    main()
