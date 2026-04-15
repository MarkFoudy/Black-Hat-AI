"""
Root-level pytest configuration for the Black Hat AI mono-repo.

Each chapter is a self-contained Python project that exports a package
named `src`. Running `pytest` from the repo root would normally cause
`src` to resolve to whichever chapter's directory landed first on
sys.path — making tests from other chapters import the wrong code.

This conftest solves that with a chapter-aware Module subclass and a
save/restore mechanism:

  * _ChapterModule.collect() fixes sys.path right before the test
    module is imported (the import happens inside collect(), not at
    makemodule time).

  * _activate_chapter() keeps a per-chapter snapshot of sys.modules
    entries for `src.*`.  When switching chapters it saves the outgoing
    snapshot and restores the incoming one.  This means:

    - Module objects (classes, functions) stay identical across
      collection → test-execution for the same chapter, so
      unittest.mock.patch() targets the right object and isinstance()
      checks pass.

    - Tests that do lazy `from src.X import Y` inside a function body
      find the correct chapter's package because the right snapshot is
      active before the test function runs (via pytest_runtest_setup).
"""

import os
import sys

from _pytest.python import Module as _BaseModule

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_CHAPTERS_DIR = os.path.join(_REPO_ROOT, "chapters")

# State shared by collection and execution hooks
_current_chapter = None
_chapter_modules = {}   # chapter_root -> snapshot of src.* sys.modules entries


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


def _activate_chapter(chapter_root):
    """
    Make *chapter_root* the active chapter for src.* imports.

    If chapter_root is already active this is a no-op.  Otherwise:
      1. Save the outgoing chapter's src.* module objects.
      2. Remove all src.* entries from sys.modules.
      3. Restore the incoming chapter's saved snapshot (if any), or
         leave sys.modules clear so a fresh import happens naturally.
      4. Put chapter_root at sys.path[0] and remove all other chapter
         roots so `import src` resolves unambiguously.
    """
    global _current_chapter
    if chapter_root == _current_chapter:
        return  # already active, nothing to do

    # --- save outgoing chapter's module state ---
    if _current_chapter is not None:
        _chapter_modules[_current_chapter] = {
            k: v for k, v in sys.modules.items()
            if k == "src" or k.startswith("src.")
        }

    _current_chapter = chapter_root

    # --- evict all src.* from sys.modules ---
    for k in list(sys.modules):
        if k == "src" or k.startswith("src."):
            del sys.modules[k]

    # --- restore incoming chapter's snapshot (may be empty first time) ---
    saved = _chapter_modules.get(chapter_root)
    if saved:
        sys.modules.update(saved)

    # --- fix sys.path ---
    sys.path = [chapter_root] + [
        p for p in sys.path
        if not (p.startswith(_CHAPTERS_DIR + os.sep) and p != chapter_root)
    ]


class _ChapterModule(_BaseModule):
    """Module collector that activates the right chapter before importing."""

    def collect(self):
        chapter_root = _chapter_root_for(self.path)
        if chapter_root is not None:
            _activate_chapter(chapter_root)
        return super().collect()


def pytest_pycollect_makemodule(module_path, parent):
    """Return a chapter-aware Module collector for every file under chapters/."""
    if _chapter_root_for(module_path) is not None:
        return _ChapterModule.from_parent(parent, path=module_path)
    return None  # not under chapters/; use default behaviour


def pytest_runtest_setup(item):
    """
    Activate the correct chapter before each test function runs.

    This matters for tests that do lazy imports (e.g. `from src.X import Y`
    inside a test method body) and for mock.patch() calls that look up
    the target module in sys.modules at patch-enter time.
    """
    chapter_root = _chapter_root_for(item.fspath)
    if chapter_root is not None:
        _activate_chapter(chapter_root)
