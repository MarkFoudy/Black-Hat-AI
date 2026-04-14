"""
Pytest configuration for Chapter 4.

Adds the chapter root to sys.path and clears any stale src.* imports
from other chapters so that `from src.xxx import ...` always resolves
to this chapter's code, regardless of which directory pytest was invoked
from.
"""

import sys
import os

_CHAPTER_ROOT = os.path.dirname(os.path.abspath(__file__))

# Flush stale src.* that may have been cached by a previously loaded chapter.
for _k in list(sys.modules):
    if _k == "src" or _k.startswith("src."):
        del sys.modules[_k]

sys.path.insert(0, _CHAPTER_ROOT)
