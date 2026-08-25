"""Turning the text of a file into pairs."""

from __future__ import annotations

from quillstack.dotenv.values import typed

EXPORT = "export "


def parse(text: str) -> dict[str, str | bool | int | float | None]:
    """Every ``KEY=value`` in the text, with the value read as what it plainly is."""
    found: dict[str, str | bool | int | float | None] = {}

    for line in text.splitlines():
        pair = _pair(line)

        if pair is not None:
            found[pair[0]] = typed(pair[1])

    return found


def _pair(line: str) -> tuple[str, str] | None:
    stripped = line.strip()

    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None

    if stripped.startswith(EXPORT):
        stripped = stripped[len(EXPORT) :].lstrip()

    key, _, value = stripped.partition("=")

    return key.strip(), _without_comment(value.strip())


def _without_comment(value: str) -> str:
    """A `#` starts a comment where a shell would treat it as one.

    After whitespace, and outside quotes. `PASSWORD=hunter2#7` has no comment in it, and a hash
    inside quotes is part of the value — a parser which took every `#` would turn a password
    into a shorter password and say nothing.
    """
    quote = ""
    previous = ""

    for index, character in enumerate(value):
        if quote:
            if character == quote:
                quote = ""
        elif character in "\"'":
            quote = character
        elif character == "#" and (index == 0 or previous.isspace()):
            return value[:index].rstrip()

        previous = character

    return value
