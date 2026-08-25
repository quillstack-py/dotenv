# Quillstack Dotenv

[![Tests](https://github.com/quillstack-py/dotenv/actions/workflows/tests.yml/badge.svg)](https://github.com/quillstack-py/dotenv/actions/workflows/tests.yml)
[![Latest Version](https://img.shields.io/pypi/v/quillstack-dotenv.svg)](https://pypi.org/project/quillstack-dotenv/)
[![Downloads](https://img.shields.io/pypi/dm/quillstack-dotenv.svg)](https://pypi.org/project/quillstack-dotenv/)
[![Python Version](https://img.shields.io/pypi/pyversions/quillstack-dotenv)](https://pypi.org/project/quillstack-dotenv/)
[![CodeFactor](https://www.codefactor.io/repository/github/quillstack-py/dotenv/badge)](https://www.codefactor.io/repository/github/quillstack-py/dotenv)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_dotenv&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=quillstack-py_dotenv)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_dotenv&metric=coverage)](https://sonarcloud.io/summary/new_code?id=quillstack-py_dotenv)
[![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_dotenv&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=quillstack-py_dotenv)
[![Reliability](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_dotenv&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=quillstack-py_dotenv)
[![Security](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_dotenv&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=quillstack-py_dotenv)
[![License](https://img.shields.io/pypi/l/quillstack-dotenv)](https://github.com/quillstack-py/dotenv/blob/main/LICENSE)

Reads a `.env` file. Values keep the type they plainly have, and nothing is expanded unless you
ask for it.

## Why this exists

### It does not expand `${SOMETHING}`, and that is on purpose

Most `.env` libraries resolve one value from another out of the box. This one does not, and the
model it follows is JavaScript's.

**`dotenv` for Node is the most installed `.env` library anywhere, and it does not interpolate.**
Nor does `dotenv-java`. In that world, building values from other values is a second package,
because it is a second decision: it turns a list of pairs into a small language, with escaping
and ordering and undefined names to settle.

The same choice is made here, and by
[quillstack/dotenv](https://github.com/quillstack/dotenv) in PHP. A `.env` file which quietly
became a template is a `.env` file you have to read twice.

### A value keeps the type it has

```python
if settings["APP_DEBUG"]:
    ...
```

Read as text, `false` is a non-empty string and therefore true. That is a bug which looks like
working code, and it is the reason the values are typed rather than handed back as strings.

### The values do not go into `os.environ`

`os.environ` holds strings and nothing else, so a port put there comes back `'5432'` and a
`false` comes back true — the exact thing the typing avoids. What is read stays where its types
survive, and `export()` is there for when something else needs the environment set.

## Requirements

- Python 3.11 or newer

## Installation

```shell
pip install quillstack-dotenv
```

## Usage

```text
APP_DEBUG=true
APP_NAME=quillstack
DB_PORT=5432
```

```python
from quillstack.dotenv import Dotenv

settings = Dotenv(".env").load()

settings["APP_DEBUG"]    # True, a boolean
settings["APP_NAME"]     # 'quillstack'
settings["DB_PORT"]      # 5432, a number
```

It is a `Mapping`, so `len()`, `in`, iteration and unpacking all work on it.

### Saying you meant the text

Quote it:

```text
DB_PORT_TEXT="5432"
```

```python
settings["DB_PORT_TEXT"]   # '5432', a string
```

### Default values

```python
settings.get("MISSING", "a default")   # 'a default'
settings.get("MISSING")                # None
```

### Required keys

Where there is no sensible default, say so and find out at boot rather than at midnight:

```python
settings.required("DATABASE_HOST")
```

```text
ValueNotSetError: Value not set for key: DATABASE_HOST
```

### Comments after a value

A `#` starts a comment where a shell would treat it as one — after whitespace, and outside
quotes:

```text
COMMENTED=5432 # the default
PASSWORD=hunter2#7
QUOTED="a # inside quotes"
```

```python
settings["COMMENTED"]   # 5432
settings["PASSWORD"]    # 'hunter2#7'
settings["QUOTED"]      # 'a # inside quotes'
```

A parser which took every `#` would turn a password into a shorter password and say nothing
about it.

### Nothing is expanded

```text
URL=https://${APP_NAME}.org
```

```python
settings["URL"]   # 'https://${APP_NAME}.org'
```

### Setting the environment anyway

For the sake of something else which reads `os.environ` directly:

```python
settings.export()                 # leaves what is already set alone
settings.export(override=True)    # does not
```

What goes out is text: `True` is exported as `true`, because that is what it was in the file and
what another reader expects to find. A deployment which set a variable meant it, which is why
what is already there wins unless you say otherwise.

## Benchmark

Not measured against `python-dotenv`, which is the obvious comparison and not a fair one: it
hands back strings and this reads types, so the two are doing different amounts of work on
purpose. Timing them against each other would produce a number saying this is slower at a job it
is not doing.

Either way, a `.env` file is read once at boot and has perhaps thirty lines in it. Where an
application is slow to start, this is not why.

## Tests

```shell
uv run pytest
```

### Static analysis

```shell
uv run ruff check --no-cache
uv run mypy
```

`--no-cache` on purpose: a cached ruff result once said a Quillstack package was clean while CI
said it was not.

### Against the standard

```shell
uv run quillstack-standards .
```

## The rest of Quillstack

This is one component of [Quillstack](https://quillstack.org), the same way of building APIs in
more than one language.

- [quillstack-standards](https://github.com/quillstack-py/standards) — what keeps every package the same shape
- [quillstack/dotenv](https://github.com/quillstack/dotenv) — the same decisions in PHP
- [quillstack/dotenv-expand](https://github.com/quillstack/dotenv-expand) — values built from other values, where you want them

## License

MIT — see [LICENSE](https://github.com/quillstack-py/dotenv/blob/main/LICENSE).
