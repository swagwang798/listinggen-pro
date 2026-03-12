# provider_base.py
# 定义所有 Provider 必须遵守的统一接口（抽象基类）
# 负责约束：如何调用模型、如何返回原始结果
# 不处理业务流程，不生成最终结果
from __future__ import annotations
from abc import ABC, abstractmethod
from .types import ProviderResponse

class BaseProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> ProviderResponse:
        raise NotImplementedError