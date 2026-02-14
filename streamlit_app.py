"""
Streamlit entrypoint for LangChainExpo.

Run:
  streamlit run streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_import_paths() -> None:
    """
    Ensure imports work on Streamlit Community Cloud.

    Streamlit runs the entry script with the repo root as the working directory,
    but Python import paths can differ across environments. We explicitly add:
      - repo root
      - `src/` itself (so modules under `src/` can be imported as top-level packages)
    """

    repo_root = Path(__file__).resolve().parent
    src_dir = repo_root / "src"

    sys.path.insert(0, str(repo_root))
    sys.path.insert(0, str(src_dir))


_ensure_import_paths()

from app.main import run  # type: ignore[reportMissingImports]  # noqa: E402

run()
