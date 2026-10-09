#!/usr/bin/env python3
"""Sanity checks for the integrated dual-view sculpture."""
from pathlib import Path
import json, math, re

HERE = Path(__file__).resolve().parent
stl_path = HERE / "qing_hua_integrated.stl"
required = [stl_path, HERE / "projection_qing.png", HERE / "projection_hua.png", HERE / "projection_check.json"]
for path in required:
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"FAIL: missing or empty output: {path.name}")

vertices = []
facets = 0
rx = re.compile(r"^\s*vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*$")
with stl_path.open("r", encoding="ascii") as f:
    if not f.readline().strip().lower().startswith("solid"):
        raise SystemExit("FAIL: expected ASCII STL")
    for line in f:
        if line.lstrip().startswith("facet normal"):
            facets += 1
        m = rx.match(line)
        if m:
            p = tuple(float(v) for v in m.groups())
            if not all(math.isfinite(v) for v in p):
                raise SystemExit("FAIL: non-finite vertex")
            vertices.append(p)
if not facets or len(vertices) != facets * 3:
    raise SystemExit(f"FAIL: malformed STL facets={facets}, vertices={len(vertices)}")
report = json.loads((HERE / "projection_check.json").read_text(encoding="utf-8"))
if report.get("faces") != facets:
    raise SystemExit(f"FAIL: report face count {report.get('faces')} does not match STL facets {facets}")
if report.get("surface_text_or_engraving") is not False:
    raise SystemExit("FAIL: model metadata does not confirm no surface text/engraving")
print("PASS: STL and both orthogonal projection images exist.")
print(f"PASS: ASCII STL facets={facets}; vertices={len(vertices)}; no non-finite coordinates.")
print(f"PASS: visual-hull report; watertight={report.get('watertight')}; bounds={report.get('bounds_mm')}")
