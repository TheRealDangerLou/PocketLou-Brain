from __future__ import annotations

from abc import ABC, abstractmethod


class BaseMode(ABC):
    """Base class for all Pocket Lou operating modes."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def system_prompt_additions(self) -> str:
        return ""

    def pre_process(self, user_input: str) -> str:
        return user_input

    def post_process(self, response: str) -> str:
        return response
