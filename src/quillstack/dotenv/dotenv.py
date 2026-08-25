"""Reading a file."""

from __future__ import annotations

from pathlib import Path

from quillstack.dotenv.errors import MissingFileError
from quillstack.dotenv.parser import parse
from quillstack.dotenv.settings import Settings


class Dotenv:
    """A `.env` file, and what is in it.

    Nothing here expands ``${SOMETHING}``. That is the model JavaScript's `dotenv` follows —
    the most installed `.env` library anywhere — and `dotenv-java` too: building values from
    other values is a second decision, with escaping and ordering and undefined names to
    settle, so it is a second package.
    """

    def __init__(self, path: str | Path = ".env") -> None:
        self.path = Path(path)

    def load(self) -> Settings:
        """Everything in the file, read as what it plainly is."""
        if not self.path.is_file():
            raise MissingFileError(f"No .env file at: {self.path}")

        return Settings(parse(self.path.read_text(encoding="utf-8")))
