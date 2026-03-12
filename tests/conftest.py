import pytest

from listinggen.engine.engine import ListingEngine
from listinggen.engine.provider_fake import FakeProvider
from listinggen.engine.types import ListingInput, GenTask


@pytest.fixture
def fake_engine():
    # 这里不传 max_retries（ENGINE-RETRY-SPLIT）
    provider = FakeProvider()
    return ListingEngine(provider=provider, qps=None)


@pytest.fixture
def sample_listing():
    return ListingInput(
        sku="SKU123",
        source_title="Wireless Earbuds Bluetooth 5.3 Noise Cancelling",
        bullets="Long battery life; Comfortable fit; Clear calls",
        description="High quality wireless earbuds with ENC for calls, charging case included.",
        keywords="wireless earbuds, bluetooth earbuds, noise cancelling",
    )


@pytest.fixture
def sample_task():
    # 如果你的 GenTask 是 Enum，就按你项目里实际的写法改一下
    # 这里先假设 GenTask 接受 name 字段或是 Enum 成员
    # 你项目里若是 Enum：return GenTask.TITLE / GenTask.BULLETS 之类
    return GenTask(name="title")
