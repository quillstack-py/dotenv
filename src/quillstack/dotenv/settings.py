"""What was read, and how it is asked for."""

from __future__ import annotations

import os
from collections.abc import Iterator, Mapping
from typing import Any

from quillstack.dotenv.errors import ValueNotSetError

Value = str | bool | int | float | None


class Settings(Mapping[str, Value]):
    """The pairs from a file, kept where their types survive.

    They are not put into ``os.environ``. That holds strings and nothing else, so a `5432` would
    come back `'5432'` and a `false` would come back true — which is the bug this package exists
    to avoid. Ask ``export()`` for that behaviour where something else needs it.
    """

    def __init__(self, values: Mapping[str, Value]) -> None:
        self._values = dict(values)

    def __getitem__(self, key: str) -> Value:
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __repr__(self) -> str:
        return f"Settings({len(self._values)} keys)"

    def get(self, key: str, default: Any = None) -> Any:
        """The value, or the default where there is none."""
        return self._values.get(key, default)

    def required(self, key: str) -> Value:
        """The value, or a refusal naming the key.

        Where there is no sensible default, saying so here means finding out at boot rather
        than at midnight.
        """
        if key not in self._values:
            raise ValueNotSetError(f"Value not set for key: {key}")

        return self._values[key]

    def export(self, override: bool = False) -> None:
        """Puts the values in ``os.environ``, as the strings it can hold.

        For the sake of something else which reads the environment directly. What is exported
        is text: `True` goes out as `true`, because that is what it was in the file and what
        another reader expects to find.
        """
        for key, value in self._values.items():
            if not override and key in os.environ:
                continue

            os.environ[key] = _as_text(value)


def _as_text(value: Value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    return "" if value is None else str(value)
