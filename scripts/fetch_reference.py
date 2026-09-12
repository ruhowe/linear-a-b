#!/usr/bin/env python3
"""Fetch the openly licensed reference data the etymological line needs.

    .venv/bin/python scripts/fetch_reference.py            # everything below
    .venv/bin/python scripts/fetch_reference.py --only strongs,frequencywords
    .venv/bin/python scripts/fetch_reference.py --dest /some/other/dir

Everything lands under ``~/.cache/linear-a-b/reference/`` (``--dest`` overrides), the
folder the loaders in ``src/hypotheses/lexicons.py``, ``src/semitic_null/lexicon.py``
and ``scripts/unrelated_controls.py`` read from. Nothing is written into the repository:
these are third-party lexicons and the licensing invariants in
``docs/ai_context/corpus-sources.md`` keep them out of git. Files already present are
left alone.

What is fetched, and why each is needed:

- ``strongs-hebrew.json``: Open Scriptures' Strong's Hebrew dictionary (public domain),
  the lexicon behind ``src/semitic_null/`` and the Hebrew rows of F-008 to F-014.
- ``freq_{fi,tr,hu,eu,he,ar}_50k.txt``: FrequencyWords 2018 top-50,000 lists
  (OpenSubtitles-derived; hermitdave), the unrelated-language controls of F-013.
- ``kaikki-hittite.jsonl``: kaikki.org's Wiktionary extract for Hittite, the Hittite
  proxy of F-013.
- ``oracc/{saao,rinap,ribo}.zip``: ORACC project glossaries (CC0), the Akkadian citation
  forms of F-011 and F-012; ``oracc/epsd2-literary.zip`` for the Sumerian control.
- ``cuc/DT-UCPH-cuc-03a334e/lexicon_and_grammar/ugaritic_lexicon.txt``: the Copenhagen
  Ugaritic Corpus lemma list (CC BY-NC per the repository README), the Ugaritic rows of
  F-011 and F-012. Pinned to commit 03a334e, the version the findings used.
- ``ya-diktu-di-mino-v5.pdf`` (``--only dimino``, off by default): the di Mino 2026
  preprint, CC BY 4.0, for reading. No script reads it; ``scripts/audit_di_mino.py``
  works from the corpus alone.

Not fetched here because it needs nothing from you: the three corpora (pyaegean fetches
them on first ``aegean.load``), the Perseus Greek texts (pyaegean, first use of the Greek
lexicon builds a ~270 MB index once), and the per-spike caches, which each spike's
``run.py`` or ``fetch.py`` builds itself.

If a URL below has moved, the ``Source`` column of the summary says where to look by
hand; put the file at the path shown and the loaders will find it. Downloads go through
Python's ``urllib``; when a server's certificate chain is incomplete (ORACC's was, on
2026-09-12) the script falls back to the system ``curl``, which verifies against the
operating system's trust store. Verification is never switched off.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DEST = Path.home() / ".cache" / "linear-a-b" / "reference"
UA = {"User-Agent": "linear-a-b/fetch_reference (https://github.com; research use)"}
TIMEOUT = 120


@dataclass
class Item:
    name: str
    target: Path
    source: str
    fetch: object  # callable(dest: Path) -> None
    default: bool = True


def _get(url: str) -> bytes:
    """GET ``url``; on a certificate-chain failure fall back to the system ``curl``.

    ORACC's server (checked 2026-09-12) sends an incomplete certificate chain, which
    Python's OpenSSL rejects and the operating system's trust store accepts. Verification
    is never disabled: ``curl`` verifies against the system store instead.
    """
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:  # noqa: S310
            return resp.read()
    except urllib.error.URLError as exc:
        if not isinstance(exc.reason, ssl.SSLCertVerificationError) or not shutil.which("curl"):
            raise
        print(f"  certificate chain rejected by Python for {url}; using curl", flush=True)
        out = subprocess.run(
            ["curl", "-fsSL", "--max-time", str(TIMEOUT * 4), "-A", UA["User-Agent"], url],
            capture_output=True, check=False,
        )
        if out.returncode != 0:
            raise RuntimeError(f"curl failed ({out.returncode}): {out.stderr.decode(errors='replace')[:200]}") from exc
        return out.stdout


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(data)
    tmp.replace(path)


# --- Strong's Hebrew ---------------------------------------------------------------

STRONGS_URL = (
    "https://raw.githubusercontent.com/openscriptures/strongs/master/hebrew/"
    "strongs-hebrew-dictionary.js"
)


def fetch_strongs(dest: Path) -> None:
    raw = _get(STRONGS_URL).decode("utf-8")
    obj = raw[raw.index("{") : raw.rindex("}") + 1]
    entries = json.loads(obj)
    if len(entries) < 8000 or not any("lemma" in v for v in entries.values()):
        raise ValueError(f"unexpected shape: {len(entries)} entries")
    _write(dest / "strongs-hebrew.json", raw.encode("utf-8"))


# --- FrequencyWords ---------------------------------------------------------------

FREQ_LANGS = ("fi", "tr", "hu", "eu", "he", "ar")
FREQ_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/{lang}/{lang}_50k.txt"


def fetch_frequencywords(dest: Path) -> None:
    for lang in FREQ_LANGS:
        target = dest / f"freq_{lang}_50k.txt"
        if target.exists():
            continue
        data = _get(FREQ_URL.format(lang=lang))
        lines = data.count(b"\n")
        if lines < 40_000:
            raise ValueError(f"{lang}: only {lines} lines")
        _write(target, data)


# --- kaikki Hittite ---------------------------------------------------------------

KAIKKI_URL = "https://kaikki.org/dictionary/Hittite/kaikki.org-dictionary-Hittite.jsonl"


def fetch_kaikki(dest: Path) -> None:
    data = _get(KAIKKI_URL)
    first = data.split(b"\n", 1)[0]
    json.loads(first)  # one JSON object per line
    _write(dest / "kaikki-hittite.jsonl", data)


# --- ORACC glossaries ---------------------------------------------------------------

ORACC_PROJECTS = ("saao", "rinap", "ribo", "epsd2-literary")
ORACC_URL = "http://oracc.museum.upenn.edu/json/{project}.zip"


def fetch_oracc(dest: Path) -> None:
    for project in ORACC_PROJECTS:
        target = dest / "oracc" / f"{project}.zip"
        if target.exists():
            continue
        data = _get(ORACC_URL.format(project=project))
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            if zf.testzip() is not None:
                raise ValueError(f"{project}.zip is corrupt")
            if not any(n.endswith(".json") and "/gloss-" in n for n in zf.namelist()):
                raise ValueError(f"{project}.zip carries no glossary")
        _write(target, data)


# --- Copenhagen Ugaritic Corpus ----------------------------------------------------------

CUC_COMMIT = "03a334e"
CUC_GITHUB_URL = f"https://github.com/DT-UCPH/cuc/archive/{CUC_COMMIT}.zip"
CUC_ZENODO_API = "https://zenodo.org/api/records?q=conceptrecid:10695308&sort=mostrecent&size=1"
CUC_REL = Path("lexicon_and_grammar") / "ugaritic_lexicon.txt"


def fetch_cuc(dest: Path) -> None:
    target = dest / "cuc" / f"DT-UCPH-cuc-{CUC_COMMIT}" / CUC_REL
    if target.exists():
        return
    try:
        data = _get(CUC_GITHUB_URL)
        note = ""
    except urllib.error.URLError:
        record = json.loads(_get(CUC_ZENODO_API))
        files = record["hits"]["hits"][0]["files"]
        zips = [f for f in files if f["key"].endswith(".zip")]
        if not zips:
            raise
        data = _get(zips[0]["links"]["self"])
        note = " (Zenodo's latest release, not the pinned commit; counts may differ slightly)"
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        members = [n for n in zf.namelist() if n.endswith(str(CUC_REL).replace("\\", "/"))]
        if not members:
            raise ValueError("ugaritic_lexicon.txt not in the archive")
        _write(target, zf.read(members[0]))
    if note:
        print(f"  cuc: fetched{note}")


# --- di Mino 2026 (optional) -----------------------------------------------------------

DIMINO_API = "https://zenodo.org/api/records/22129502"


def fetch_dimino(dest: Path) -> None:
    record = json.loads(_get(DIMINO_API))
    pdfs = [f for f in record["files"] if f["key"].lower().endswith(".pdf")]
    if not pdfs:
        raise ValueError("no PDF on the Zenodo record")
    _write(dest / "ya-diktu-di-mino-v5.pdf", _get(pdfs[0]["links"]["self"]))


# --- driver ------------------------------------------------------------------------------


def items(dest: Path) -> list[Item]:
    return [
        Item("strongs", dest / "strongs-hebrew.json", "github.com/openscriptures/strongs", fetch_strongs),
        Item("frequencywords", dest / "freq_fi_50k.txt", "github.com/hermitdave/FrequencyWords (content/2018)", fetch_frequencywords),
        Item("kaikki", dest / "kaikki-hittite.jsonl", "kaikki.org/dictionary/Hittite", fetch_kaikki),
        Item("oracc", dest / "oracc" / "saao.zip", "oracc.museum.upenn.edu/json/<project>.zip", fetch_oracc),
        Item("cuc", dest / "cuc" / f"DT-UCPH-cuc-{CUC_COMMIT}" / CUC_REL, "github.com/DT-UCPH/cuc, commit 03a334e (Zenodo 10.5281/zenodo.10695308)", fetch_cuc),
        Item("dimino", dest / "ya-diktu-di-mino-v5.pdf", "doi.org/10.5281/zenodo.22129502", fetch_dimino, default=False),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST, help=f"target folder (default {DEFAULT_DEST})")
    ap.add_argument("--only", help="comma-separated subset: strongs,frequencywords,kaikki,oracc,cuc,dimino")
    args = ap.parse_args()

    wanted = set(args.only.split(",")) if args.only else None
    rows: list[tuple[str, str, str]] = []
    failed = 0
    for item in items(args.dest):
        if wanted is not None and item.name not in wanted:
            continue
        if wanted is None and not item.default:
            continue
        if item.target.exists():
            rows.append((item.name, "present", item.source))
            continue
        print(f"fetching {item.name} ...", flush=True)
        try:
            item.fetch(args.dest)
            rows.append((item.name, "fetched", item.source))
        except Exception as exc:  # noqa: BLE001
            failed += 1
            rows.append((item.name, f"FAILED: {exc}", item.source))

    width = max(len(r[0]) for r in rows) if rows else 8
    print()
    print(f"{'item'.ljust(width)}  status                      source")
    for name, status, source in rows:
        print(f"{name.ljust(width)}  {status[:26].ljust(26)}  {source}")
    if failed:
        print(f"\n{failed} item(s) failed. Fetch by hand from the source shown and place the file at the path in the docstring.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
