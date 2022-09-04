from __future__ import annotations

from typing import Optional


class Image:
    def __init__(
        self,
        name: str,
        entrypoint: Optional[list[str]] = None,
        env: dict = {},
        mount: list[tuple[str, str]] = [],
    ):
        self.name = name
        self.entrypoint = entrypoint
        self.env = env
        self.mount = mount
