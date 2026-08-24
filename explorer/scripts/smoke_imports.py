"""Quick import smoke test — catches syntax errors before launching Streamlit.

Importing pages that call `st.set_page_config` outside Streamlit's runtime
will warn but not fail; we just check the modules parse and resolve.
"""

from __future__ import annotations

import importlib

modules = [
    "explorer",
    "explorer.data_access",
    "explorer.questions_access",
    "explorer.navigation",
    "explorer.search",
    "explorer.components",
    "explorer.components.kpi_cards",
    "explorer.components.pdf_preview",
    "explorer.components.hierarchy_tree",
]

failures: list[tuple[str, str]] = []
for name in modules:
    try:
        importlib.import_module(name)
        print(f"OK  {name}")
    except Exception as exc:
        print(f"FAIL {name}: {type(exc).__name__}: {exc}")
        failures.append((name, str(exc)))

if failures:
    raise SystemExit(1)
print("\nAll imports OK")
