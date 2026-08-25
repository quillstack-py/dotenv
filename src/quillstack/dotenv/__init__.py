"""Reads a `.env` file.

Values keep the type they plainly have, and nothing is expanded unless you ask for it.
"""

from quillstack.dotenv.dotenv import Dotenv
from quillstack.dotenv.errors import DotenvError, MissingFileError, ValueNotSetError
from quillstack.dotenv.settings import Settings

__all__ = ["Dotenv", "DotenvError", "MissingFileError", "Settings", "ValueNotSetError"]
