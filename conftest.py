"""
Root-level pytest configuration for the Black Hat AI mono-repo.

Each chapter is a self-contained Python project that exports a package
named `src`. Running `pytest` from the repo root would normally cause
`src` to resolve to whichever chapter's directory landed first on
sys.path — making tests from other chapters import the wrong code.

This conftest uses a custom Module subclass whose `collect()` method
fixes sys.path immediately before the test module is imported (i.e. the
import happens inside `collect()`, so fixing sys.path right before
`super().collect()` is called is exactly the right moment).

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

from _pytest.python import Module as _BaseModule

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_CHAPTERS_DIR = os.path.join(_REPO_ROOT, "chapters")


def _chapter_root_for(path):
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


def _fix_path_for_chapter(chapter_root):
    """Flush stale src.* from sys.modules and set sys.path to chapter_root."""
    stale = [k for k in list(sys.modules) if k == "src" or k.startswith("src.")]
    for k in stale:
        del sys.modules[k]
    sys.path = [chapter_root] + [
        p for p in sys.path
        if not (p.startswith(_CHAPTERS_DIR + os.sep) and p != chapter_root)
    ]


class _ChapterModule(_BaseModule):
    """Module collector that fixes sys.path right before importing the module."""

    def collect(self):
        chapter_root = _chapter_root_for(self.path)
        if chapter_root is not None:
            _fix_path_for_chapter(chapter_root)
        return super().collect()


def pytest_pycollect_makemodule(module_path, parent):
    """Return a chapter-aware Module collector for every file under chapters/."""
    if _chapter_root_for(module_path) is not None:
        return _ChapterModule.from_parent(parent, path=module_path)
    return None  # not under chapters/; use default behaviour
