import bpy, os, math
from mathutils import Vector
out=os.path.dirname(bpy.data.filepath) or os.getcwd()
stl=os.path.join(out,'qing_hua_boolean.stl')
blend=os.path.join(out,'qing_hua_boolean_editable.blend')
for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
def mat(n,c):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); return m
silver=mat('Matte Silver Gray',(.42,.46,.50)); guide=mat('Construction Guide',(.05,.12,.2))
def cube(n,m):
 bpy.ops.mesh.primitive_cube_add(); o=bpy.context.object; o.name=n; o.dimensions=(100,100,100); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); return o
def glyph(n,ch,side):
 bpy.ops.object.text_add(); o=bpy.context.object; o.name=n; o.data.body=ch; o.data.align_x='CENTER'; o.data.align_y='CENTER'; o.data.size=80; o.data.bevel_depth=.25
 if side=='front': o.rotation_euler=(math.radians(-90),0,0); o.location=(0,-50,0)
 else: o.rotation_euler=(0,math.radians(90),0); o.location=(-50,0,0)
 bpy.context.view_layer.objects.active=o; bpy.ops.object.convert(target='MESH'); bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS'); d=o.dimensions; span=max(d.x,d.z) if side=='front' else max(d.y,d.z); o.scale=(86/span,)*3; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return o
def cut(a,b,n):
 m=a.modifiers.new(n,'BOOLEAN'); m.operation='INTERSECT'; m.solver='EXACT'; m.object=b; bpy.context.view_layer.objects.active=a; bpy.ops.object.modifier_apply(modifier=m.name); bpy.data.objects.remove(b,do_unlink=True); return a
mother=cube('01_MOTHER_CUBE_100mm',guide); mother.hide_viewport=True; mother.hide_render=True
front=cut(cube('02_FRONT_KEEP_QING',silver),glyph('CUTTER_QING','清','front'),'02_KEEP_FRONT_QING'); front.name='02_RESULT_FRONT_QING'
final=cut(front,glyph('CUTTER_HUA','华','side'),'03_KEEP_SIDE_HUA'); final.name='04_FINAL_QING_HUA_BOOLEAN_RESULT'; final.data.materials.clear(); final.data.materials.append(silver)
bpy.ops.mesh.primitive_plane_add(size=240,location=(0,0,-53)); bpy.context.object.name='DISPLAY_GROUND'
bpy.ops.object.camera_add(location=(175,-175,135)); cam=bpy.context.object; bpy.context.scene.camera=cam; cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=blend); bpy.context.view_layer.objects.active=final; final.select_set(True)
try: bpy.ops.wm.stl_export(filepath=stl,export_selected_objects=True)
except: pass
print('SAVED',blend,stl)
