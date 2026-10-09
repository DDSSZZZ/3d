#!/usr/bin/env python3
"""Dependency-free sanity checks for the generated model outputs."""
from pathlib import Path
import json
import math
import re
import sys

HERE = Path(__file__).resolve().parent
stl_path = HERE / "qing_hua_integrated.stl"
svg_paths = [HERE / "projection_qing.svg", HERE / "projection_hua.svg"]
report_path = HERE / "projection_check.json"

def fail(message):
    print("FAIL:", message)
    raise SystemExit(1)

for path in [stl_path, *svg_paths, report_path]:
    if not path.is_file():
        fail(f"missing output: {path.name}")
    if path.stat().st_size == 0:
        fail(f"empty output: {path.name}")

vertices = []
facet_count = 0
vertex_re = re.compile(r"^\s*vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*$")
with stl_path.open("r", encoding="ascii") as stream:
    first = stream.readline().strip().lower()
    if not first.startswith("solid"):
        fail("STL does not start with an ASCII 'solid' header")
    for line in stream:
        if line.lstrip().startswith("facet normal"):
            facet_count += 1
        match = vertex_re.match(line)
        if match:
            point = tuple(float(value) for value in match.groups())
            if not all(math.isfinite(value) for value in point):
                fail("STL contains a non-finite vertex")
            vertices.append(point)

if facet_count == 0:
    fail("STL contains no facets")
if len(vertices) != facet_count * 3:
    fail(f"expected 3 vertices per facet; got {len(vertices)} vertices for {facet_count} facets")

degenerate = 0
for index in range(0, len(vertices), 3):
    a, b, c = vertices[index:index + 3]
    ab = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    ac = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
    cross = (ab[1]*ac[2]-ab[2]*ac[1],
             ab[2]*ac[0]-ab[0]*ac[2],
             ab[0]*ac[1]-ab[1]*ac[0])
    if sum(component*component for component in cross) < 1e-12:
        degenerate += 1
if degenerate:
    fail(f"found {degenerate} zero-area/degenerate facets")

mins = [min(point[axis] for point in vertices) for axis in range(3)]
maxs = [max(point[axis] for point in vertices) for axis in range(3)]
if any(maxs[i] - mins[i] <= 0 for i in range(3)):
    fail("STL has a zero-size dimension")

try:
    report = json.loads(report_path.read_text(encoding="utf-8"))
except (json.JSONDecodeError, OSError) as exc:
    fail(f"invalid JSON report: {exc}")
if report.get("triangle_count") != facet_count:
    fail(f"report triangle_count={report.get('triangle_count')} but STL has {facet_count} facets")

print("PASS: required outputs exist and are non-empty")
print(f"PASS: ASCII STL parsed; facets={facet_count}; vertices={len(vertices)}")
print("PASS: no zero-area facets; all vertices are finite")
print("Measured STL bounds (mm):")
for axis, low, high in zip("xyz", mins, maxs):
    print(f"  {axis}: {low:.4f} .. {high:.4f} (size {high-low:.4f})")
print("NOTE: this does not test watertightness, self-intersections, manifoldness, or printability.")
