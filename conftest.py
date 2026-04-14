"""
Root-level pytest configuration for the Black Hat AI mono-repo.

Each chapter is a self-contained Python project that exports a package
named `src`. Running `pytest` from the repo root would normally cause
`src` to resolve to whichever chapter's directory landed first on
sys.path — making tests from other chapters import the wrong code.

This conftest uses the `pytest_pycollect_makemodule` hook, which fires
immediately before each test *module* is imported. At that point we:

  1. Identify which chapter directory the test file lives in.
  2. Clear any stale `src.*` entries from sys.modules (cached from a
     previous chapter's imports).
  3. Put the correct chapter root at sys.path[0] and remove all other
     chapter roots so that `import src` resolves unambiguously.

This lets `pytest chapters/` (or bare `pytest`) work correctly from the
repo root without renaming packages or installing chapters as packages.
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_CHAPTERS_DIR = os.path.join(_REPO_ROOT, "chapters")


def _chapter_root_for(path) -> str | None:
    """Return the chapter root directory that contains *path*, or None."""
    path_str = str(path)
    try:
        entries = os.scandir(_CHAPTERS_DIR)
    except FileNotFoundError:
        return None
    with entries:
        for entry in entries:
            if entry.is_dir() and path_str.startswith(entry.path + os.sep):
                return entry.path
    return None


def pytest_pycollect_makemodule(module_path, parent):
    """Fix sys.path before each test module is imported."""
    chapter_root = _chapter_root_for(module_path)
    if chapter_root is None:
        return None  # not under chapters/; use default behaviour

    # 1. Flush stale `src.*` from sys.modules so Python re-imports
    #    from the correct chapter, not from a cached previous chapter.
    stale = [k for k in list(sys.modules) if k == "src" or k.startswith("src.")]
    for k in stale:
        del sys.modules[k]

    # 2. Remove all other chapter roots; put this chapter's root first.
    sys.path = [chapter_root] + [
        p for p in sys.path
        if not (p.startswith(_CHAPTERS_DIR + os.sep) and p != chapter_root)
    ]

    return None  # use pytest's default Module class
