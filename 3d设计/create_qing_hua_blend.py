import bpy, os, shutil
from mathutils import Vector

here = os.path.dirname(os.path.abspath(__file__))
source_stl = os.path.abspath(os.path.join(here, "..", "3d-upload", "qing_hua_integrated.stl"))
out_blend = os.path.join(here, "qing_hua_boolean_editable.blend")
out_stl = os.path.join(here, "qing_hua_boolean.stl")
if not os.path.isfile(source_stl):
    raise RuntimeError("Integrated visual-hull STL is missing: " + source_stl)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
if hasattr(bpy.ops.wm, "stl_import"):
    bpy.ops.wm.stl_import(filepath=source_stl)
else:
    bpy.ops.import_mesh.stl(filepath=source_stl)
mesh_obj = bpy.context.selected_objects[0] if bpy.context.selected_objects else bpy.context.active_object
if mesh_obj is None:
    raise RuntimeError("Blender failed to import the generated visual-hull mesh.")
mesh_obj.name = "QING_FRONT_HUA_SIDE_SINGLE_VISUAL_HULL"
mesh_obj.data.name = "Integrated_Calligraphic_Solid"
material = bpy.data.materials.new("Matte charcoal bronze")
material.diffuse_color = (0.20, 0.23, 0.25, 1)
mesh_obj.data.materials.append(material)
for poly in mesh_obj.data.polygons:
    poly.use_smooth = True

# Camera and lighting are preview aids only; no text or engraving objects are added.
bpy.ops.object.camera_add(location=(150, -150, 110))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 0)) - camera.location).to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.camera = camera
bpy.ops.object.light_add(type="AREA", location=(10, -100, 120))
light = bpy.context.object
light.data.energy = 14000
light.data.shape = "DISK"
light.data.size = 90
light.rotation_euler = (Vector((0, 0, 0)) - light.location).to_track_quat("-Z", "Y").to_euler()
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.resolution_percentage = 100
shutil.copyfile(source_stl, out_stl)
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
print("SAVED_BLEND", out_blend)
print("COPIED_STL", out_stl)
