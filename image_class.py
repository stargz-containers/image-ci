from __future__ import annotations

from typing import Optional


class Image:
    def __init__(
        self,
        name: str,
        entrypoint: Optional[list[str]] = None,
        env: dict = {},
        mount: list[tuple[str, str]] = [],
        copy_only: bool = False,
    ):
        if copy_only and (entrypoint is not None or env or mount):
            raise ValueError(
                f"{name}: entrypoint, env and mount are not used with copy_only"
            )
        self.name = name
        self.entrypoint = entrypoint
        self.env = env
        self.mount = mount
        self.copy_only = copy_only
