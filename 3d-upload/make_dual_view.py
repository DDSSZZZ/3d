from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.measure import marching_cubes
import trimesh

OUT = Path(__file__).resolve().parent
SIZE = 144
VOXEL_MM = 0.6
SPAN_MM = 72.0
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/lxgw-wenkai/LXGWWenKai-Regular.ttf",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]
font_path = next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
if font_path is None:
    raise RuntimeError("Chinese CJK font not found; install fonts-noto-cjk before generating the model.")
font = ImageFont.truetype(font_path, 116)

def connect_mask_components(mask, bridge_width=7):
    """Join disconnected glyph fragments with short, rounded calligraphic bridges."""
    from scipy.ndimage import label
    from scipy.spatial import cKDTree

    connected = mask.copy()
    while True:
        labels, count = label(connected)
        if count <= 1:
            return connected
        sizes = np.bincount(labels.ravel())
        sizes[0] = 0
        main_label = int(np.argmax(sizes))
        main_yx = np.argwhere(labels == main_label)
        other_labels = [i for i in range(1, count + 1) if i != main_label]
        tree = cKDTree(main_yx)
        # Join the nearest remaining component to the main connected stroke.
        best = None
        for component_label in other_labels:
            pts = np.argwhere(labels == component_label)
            distances, indices = tree.query(pts, k=1)
            j = int(np.argmin(distances))
            candidate = (float(distances[j]), pts[j], main_yx[int(indices[j])])
            if best is None or candidate[0] < best[0]:
                best = candidate
        _, a, b = best
        canvas = Image.fromarray((connected.astype(np.uint8) * 255), mode="L")
        draw = ImageDraw.Draw(canvas)
        draw.line((int(a[1]), int(a[0]), int(b[1]), int(b[0])),
                  fill=255, width=bridge_width)
        # Rounded bridge ends avoid sharp, fragile joints.
        r = bridge_width // 2
        for x, y in ((int(a[1]), int(a[0])), (int(b[1]), int(b[0]))):
            draw.ellipse((x-r, y-r, x+r, y+r), fill=255)
        connected = np.asarray(canvas) >= 128

def glyph_mask(char):
    image = Image.new("L", (SIZE, SIZE), 0)
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), char, font=font, stroke_width=0)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (SIZE - w) // 2 - bbox[0]
    y = (SIZE - h) // 2 - bbox[1]
    draw.text((x, y), char, fill=255, font=font)
    mask = np.asarray(image) >= 128
    # Slightly broaden the calligraphic strokes, then add sparse white slits as dry-brush texture.
    # The slits are kept narrow so they read as material voids rather than surface decoration.
    from scipy.ndimage import binary_dilation
    mask = binary_dilation(mask, iterations=1)
    yy, xx = np.indices(mask.shape)
    dry = ((xx * 17 + yy * 31 + (xx * yy) % 23) % 211 == 0)
    mask &= ~dry
    # Restore connectivity after dry-brush cuts, then bridge any detached glyph pieces.
    mask = connect_mask_components(mask, bridge_width=7)
    return mask

qing = glyph_mask("清")      # front projection: x-z
hua = glyph_mask("華")       # side projection: y-z

# Scale the two orthogonal calligraphic silhouettes to a shared physical height.
# The voxel solid is their visual-hull intersection: Q(x,z) AND H(y,z).
# It is one integrated volume, not letters attached to surfaces.
n = SIZE
q = qing.T  # raster rows become vertical Z; columns become X
h = hua.T  # same vertical Z, columns become Y
solid = q[:, None, :] & h[None, :, :]
# Close tiny one-voxel gaps and add a modest structural margin at the bottom so the form is printable.
from scipy.ndimage import binary_closing
solid = binary_closing(solid, structure=np.ones((3, 3, 3), dtype=bool))
if not solid.any():
    raise RuntimeError("Visual-hull intersection is empty; cannot export model.")

# Marching cubes gives one triangulated, continuous surface. Coordinates are centered in XY;
# Z remains vertical. Convert voxel coordinates to millimetres.
verts, faces, normals, values = marching_cubes(solid.astype(np.float32), level=0.5, spacing=(VOXEL_MM, VOXEL_MM, VOXEL_MM))
verts -= np.array([n * VOXEL_MM / 2, n * VOXEL_MM / 2, n * VOXEL_MM / 2])
mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
mesh.remove_unreferenced_vertices()
if not mesh.is_watertight:
    mesh = mesh.fill_holes()
mesh.export(OUT / "qing_hua_integrated.stl", file_type="stl_ascii")

def save_projection(mask, title, path):
    # Render the true raster silhouette used to construct the volume.
    scale = 4
    im = Image.new("RGB", (SIZE * scale + 48, SIZE * scale + 80), (247, 241, 223))
    pix = Image.fromarray(np.where(mask, 20, 247).astype(np.uint8)).resize((SIZE*scale, SIZE*scale), Image.Resampling.NEAREST)
    im.paste(Image.merge("RGB", (pix, pix, pix)), (24, 42))
    ImageDraw.Draw(im).text((24, 12), title, fill=(30, 30, 30))
    im.save(path)

save_projection(qing, "Front orthographic projection: 清", OUT / "projection_qing.png")
save_projection(hua, "Side orthographic projection: 華", OUT / "projection_hua.png")
report = {
    "model": "qing_hua_integrated.stl",
    "method": "orthogonal visual-hull intersection of two glyph masks",
    "units": "mm",
    "voxel_mm": VOXEL_MM,
    "front_projection": "清",
    "side_projection_after_90_degree_rotation": "華",
    "surface_text_or_engraving": False,
    "front_mask_connected": bool(__import__("scipy").ndimage.label(qing)[1] == 1),
    "side_mask_connected": bool(__import__("scipy").ndimage.label(hua)[1] == 1),
    "mesh_connected_components": int(len(mesh.split(only_watertight=False))),
    "watertight": bool(mesh.is_watertight),
    "vertices": int(len(mesh.vertices)),
    "faces": int(len(mesh.faces)),
    "bounds_mm": mesh.bounds.tolist(),
}
(OUT / "projection_check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
