"""What a `.env` file means, and what it does not."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from quillstack.dotenv import Dotenv, MissingFileError, Settings, ValueNotSetError


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / ".env"
    path.write_text(text, encoding="utf-8")

    return path


def load(tmp_path: Path, text: str) -> Settings:
    return Dotenv(write(tmp_path, text)).load()


def test_a_value_keeps_the_type_it_plainly_has(tmp_path: Path) -> None:
    """`if settings["APP_DEBUG"]` should mean what it reads as.

    Read as text, `false` is a non-empty string and therefore true, which is the bug this is
    here to avoid.
    """
    settings = load(
        tmp_path,
        "APP_DEBUG=true\nAPP_QUIET=false\nDB_PORT=5432\nRATIO=0.25\nAPP_NAME=quillstack\n",
    )

    assert settings["APP_DEBUG"] is True
    assert settings["APP_QUIET"] is False
    assert settings["DB_PORT"] == 5432
    assert settings["RATIO"] == 0.25
    assert settings["APP_NAME"] == "quillstack"


def test_quoting_is_how_you_say_you_meant_the_text(tmp_path: Path) -> None:
    settings = load(tmp_path, 'PORT="5432"\nFLAG=\'true\'\n')

    assert settings["PORT"] == "5432"
    assert settings["FLAG"] == "true"


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("DB_PORT=5432 # the default", 5432),
        ("PASSWORD=hunter2#7", "hunter2#7"),
        ('QUOTED="a # inside quotes"', "a # inside quotes"),
        ("EMPTY=   # nothing but a comment", None),
    ],
)
def test_a_hash_starts_a_comment_where_a_shell_would_say_so(
    tmp_path: Path, line: str, expected: object
) -> None:
    """A parser which took every `#` would turn a password into a shorter password and say
    nothing about it."""
    settings = load(tmp_path, line + "\n")

    assert next(iter(settings.values())) == expected


def test_nothing_is_expanded(tmp_path: Path) -> None:
    """The defining decision, and the reason there is a second package.

    JavaScript's `dotenv` — the most installed anywhere — does not interpolate either. Building
    values from other values is a small language, with escaping and ordering and undefined
    names to settle, and that is a second decision rather than a default.
    """
    settings = load(tmp_path, "HOST=example.com\nURL=https://${HOST}/api\n")

    assert settings["URL"] == "https://${HOST}/api"


def test_a_missing_key_can_have_a_default(tmp_path: Path) -> None:
    settings = load(tmp_path, "APP_NAME=quillstack\n")

    assert settings.get("MISSING", "a default") == "a default"
    assert settings.get("MISSING") is None


def test_a_required_key_says_which_one_is_missing(tmp_path: Path) -> None:
    settings = load(tmp_path, "APP_NAME=quillstack\n")

    with pytest.raises(ValueNotSetError, match="DATABASE_HOST"):
        settings.required("DATABASE_HOST")

    assert settings.required("APP_NAME") == "quillstack"


def test_blank_lines_comments_and_export_are_understood(tmp_path: Path) -> None:
    settings = load(
        tmp_path,
        "\n# a comment\n\nexport APP_NAME=quillstack\n   \nNOT_A_PAIR\n",
    )

    assert dict(settings) == {"APP_NAME": "quillstack"}


def test_a_file_which_is_not_there_says_so(tmp_path: Path) -> None:
    with pytest.raises(MissingFileError, match=re.escape("No .env file at")):
        Dotenv(tmp_path / "nowhere").load()


def test_it_is_a_mapping(tmp_path: Path) -> None:
    settings = load(tmp_path, "A=1\nB=2\n")

    assert len(settings) == 2
    assert sorted(settings) == ["A", "B"]
    assert "A" in settings


def test_exporting_puts_text_where_the_environment_can_hold_it(tmp_path: Path) -> None:
    """`os.environ` holds strings and nothing else, which is why the values do not live there.

    What is exported is what was in the file, so something else reading the environment finds
    what it expects rather than Python's spelling of it.
    """
    settings = load(tmp_path, "QS_DEBUG=true\nQS_PORT=5432\nQS_NOTHING=null\n")

    for key in ("QS_DEBUG", "QS_PORT", "QS_NOTHING"):
        os.environ.pop(key, None)

    settings.export()

    assert os.environ["QS_DEBUG"] == "true"
    assert os.environ["QS_PORT"] == "5432"
    assert os.environ["QS_NOTHING"] == ""

    for key in ("QS_DEBUG", "QS_PORT", "QS_NOTHING"):
        del os.environ[key]


def test_exporting_leaves_what_is_already_set_alone(tmp_path: Path) -> None:
    """A real environment beats a file, unless told otherwise. A deployment which sets a
    variable meant it."""
    os.environ["QS_KEEP"] = "from the environment"
    settings = load(tmp_path, "QS_KEEP=from the file\n")

    settings.export()
    assert os.environ["QS_KEEP"] == "from the environment"

    settings.export(override=True)
    assert os.environ["QS_KEEP"] == "from the file"

    del os.environ["QS_KEEP"]
