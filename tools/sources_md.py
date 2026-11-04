#!/usr/bin/env python3
"""Render docs/sources.yaml as docs/sources.md: python3 -I tools/sources_md.py"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent
items = yaml.safe_load((ROOT / "docs" / "sources.yaml").read_text(encoding="utf-8"))
ORDER = ["in-db", "to-import", "reference", "private"]
HEAD = {
    "in-db": "In the database (`make db`)",
    "to-import": "Open licence, importer still to write",
    "reference": "Reference only (read, cite, do not copy)",
    "private": "Private (Hkka-private only)",
}
out = ["# Sources and documentation", "",
       "Generated from `docs/sources.yaml` by `tools/sources_md.py`; edit the YAML, not this file.", "",
       "Licences were checked on 2026-11-04. Check again before importing anything new.", ""]
for st in ORDER:
    group = [i for i in items if i["status"] == st]
    if not group:
        continue
    out += [f"## {HEAD[st]}", "", "| Resource | Accents | Use | Licence |", "|---|---|---|---|"]
    for i in group:
        acc = ", ".join(i.get("accents", []))
        out.append(f"| [{i['title']}]({i['url']}) — {i['publisher']} | {acc} | {', '.join(i.get('use', []))} | {i['licence']} |")
    out.append("")
    for i in group:
        out += [f"**{i['title']}** (`{i['id']}`, {i.get('format', '')}). {i.get('note', '').strip()}", ""]
(ROOT / "docs" / "sources.md").write_text("\n".join(out), encoding="utf-8")
print(f"{len(items)} sources → docs/sources.md")
