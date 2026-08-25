"""What a line's value plainly is."""

from __future__ import annotations

TRUE = {"true", "yes", "on"}
FALSE = {"false", "no", "off"}
NOTHING = {"null", "none", ""}


def typed(value: str) -> str | bool | int | float | None:
    """The type the text plainly has.

    ``APP_DEBUG=true`` is a boolean, so ``if settings["APP_DEBUG"]`` means what it reads as
    rather than being true because ``"false"`` is a non-empty string. A port is a number. Text
    which is only text stays text.

    Quoting is how you say you meant the text: ``PORT="5432"`` is a string.
    """
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]

    folded = value.strip().lower()

    if folded in TRUE:
        return True

    if folded in FALSE:
        return False

    if folded in NOTHING:
        return None

    return _number(value.strip())


def _number(value: str) -> str | int | float:
    """A number where the text is one and nothing else.

    `int()` accepts underscores and surrounding whitespace, and `float()` accepts `inf` and
    `nan`, none of which anybody writing a `.env` file means by them.
    """
    if not value or not value.lstrip("-+").replace(".", "", 1).isdigit():
        return value

    if "." in value:
        return float(value)

    return int(value)
