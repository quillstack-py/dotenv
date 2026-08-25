"""What this refuses to do quietly."""

from __future__ import annotations


class DotenvError(Exception):
    """Everything here raises this, or something which is one."""


class MissingFileError(DotenvError, FileNotFoundError):
    """The file is not where it was said to be.

    Both a `DotenvError` and a `FileNotFoundError`, because it is both: code which catches the
    built-in one for any missing file should catch this too, and code which cares that it was
    this package should be able to say so.
    """


class ValueNotSetError(DotenvError):
    """A key which has to be there is not.

    Asked for with ``required()``, which exists so that a missing setting is found at boot
    rather than at midnight by whoever is on call.
    """
