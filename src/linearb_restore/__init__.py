"""Linear B restoration baseline — reproduce and calibrate the published BiRNN infilling result.

Built against DĀMOS (Aurora 2015, CC BY-NC-SA 4.0) via pyaegean, not against the
Patras group's released Zenodo file. See ``docs/ai_context/linearb-restoration.md``
for the extraction contract, the three DĀMOS traps this package works around, and
the evaluation protocol.

**Derived data never lives in the repo.** Extracted sequences, masked datasets and
split manifests are derivatives of NonCommercial-licensed corpus content and are
written to ``~/.cache/linear-a-b/`` (override with ``LINEARB_RESTORE_CACHE``).
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["cache_dir"]


def cache_dir() -> Path:
    """Where DĀMOS-derived artifacts go — outside the repo, by licence obligation.

    DĀMOS content is CC BY-NC-SA 4.0. Anything derived from it (sequences, masked
    items, split manifests) inherits NonCommercial + ShareAlike, so it is kept out
    of the repository the same way pyaegean keeps fetched corpora in
    ``~/.cache/pyaegean/``. Only code, aggregate metrics and counts belong in the repo.
    """
    override = os.environ.get("LINEARB_RESTORE_CACHE")
    path = Path(override) if override else Path.home() / ".cache" / "linear-a-b"
    path.mkdir(parents=True, exist_ok=True)
    return path
