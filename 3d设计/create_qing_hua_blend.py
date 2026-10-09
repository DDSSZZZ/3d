import bpy, os, math
from mathutils import Vector

out = os.path.dirname(bpy.data.filepath) or os.getcwd()
stl = os.path.join(out, "qing_hua_boolean.stl")
blend = os.path.join(out, "qing_hua_boolean_editable.blend")

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def mat(name, color):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1)
    return material

silver = mat("Matte Silver Gray", (0.42, 0.46, 0.50))
dark = mat("Engraving Dark", (0.08, 0.10, 0.13))

font_candidates = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]
cjk_font = None
for font_path in font_candidates:
    if os.path.exists(font_path):
        try:
            cjk_font = bpy.data.fonts.load(font_path)
            break
        except Exception:
            pass

if cjk_font is None:
    raise RuntimeError("No usable Chinese font found; refusing to create a blank or incorrect model.")

def make_cube():
    bpy.ops.mesh.primitive_cube_add(size=100, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = "FINAL_CUBE_QING_FRONT_HUA_SIDE"
    obj.data.materials.append(silver)
    return obj

def make_glyph_cutter(name, char, side):
    bpy.ops.object.text_add()
    obj = bpy.context.object
    obj.name = name
    obj.data.body = char
    obj.data.font = cjk_font
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = 80
    # Shallow extrusion: carve the glyph into the cube surface, not intersect two full solids.
    obj.data.extrude = 8
    obj.data.bevel_depth = 0.0
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    dims = obj.dimensions
    span = max(dims.x, dims.z) if side == "front" else max(dims.y, dims.z)
    if span <= 0:
        raise RuntimeError(f"Glyph {char!r} has no geometry.")
    obj.scale = (86.0 / span,) * 3
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Reposition AFTER scaling so the cutter starts exactly at the cube face.
    if side == "front":
        obj.rotation_euler = (math.radians(-90), 0, 0)
        obj.location = (0, -50, 0)  # extrudes inward along +Y
    else:
        obj.rotation_euler = (0, math.radians(90), 0)
        obj.location = (-50, 0, 0)  # extrudes inward along +X
    return obj

def engrave(base, cutter, modifier_name):
    bpy.context.view_layer.objects.active = base
    base.select_set(True)
    mod = base.modifiers.new(modifier_name, "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return base

final = make_cube()
final = engrave(final, make_glyph_cutter("CUTTER_QING_FRONT", "清", "front"), "ENGRAVE_QING_FRONT")
final = engrave(final, make_glyph_cutter("CUTTER_HUA_SIDE", "华", "side"), "ENGRAVE_HUA_SIDE")
final.name = "FINAL_CUBE_QING_FRONT_HUA_SIDE"

# Add a contrasting material to the object for a neutral preview; geometry remains one cube with engraved glyphs.
bevel = final.modifiers.new("Tiny edge softening", "BEVEL")
bevel.width = 0.35
bevel.segments = 2
normal = final.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")

bpy.ops.mesh.primitive_plane_add(size=240, location=(0, 0, -51))
bpy.context.object.name = "DISPLAY_GROUND"

bpy.ops.object.camera_add(location=(175, -175, 135))
camera = bpy.context.object
bpy.context.scene.camera = camera
camera.rotation_euler = (Vector((0, 0, 0)) - camera.location).to_track_quat("-Z", "Y").to_euler()

bpy.ops.object.light_add(type="AREA", location=(30, -100, 120))
light = bpy.context.object
light.data.energy = 18000
light.data.shape = "DISK"
light.data.size = 100
light.rotation_euler = (Vector((0, 0, 0)) - light.location).to_track_quat("-Z", "Y").to_euler()

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "BLENDER_EEVEE_NEXT") else "BLENDER_EEVEE"
scene.render.resolution_x = 1000
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100

bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.context.view_layer.objects.active = final
final.select_set(True)
try:
    if hasattr(bpy.ops.wm, "stl_export"):
        bpy.ops.wm.stl_export(filepath=stl, export_selected_objects=True)
    else:
        bpy.ops.export_mesh.stl(filepath=stl, use_selection=True)
except Exception as exc:
    print("STL_EXPORT_WARNING", repr(exc))

print("SAVED_BLEND", blend)
print("SAVED_STL", stl)
