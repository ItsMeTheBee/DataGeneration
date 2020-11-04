""" https://blender.stackexchange.com/questions/7198/save-the-2d-bounding-box-of-an-object-in-rendered-image-to-a-text-file """

import bpy
import numpy as np
import bmesh
import time

def prepare_visibility_check(scene, camera_object):
    bpy.ops.object.mode_set(mode="OBJECT")
    for ob in bpy.context.scene.objects:
        if ob.hide_render == True:
            ob.hide_set(True)
        else:
            ob.hide_set(False)

    bpy.context.view_layer.objects.active = bpy.context.view_layer.objects.active
    bpy.ops.object.select_all(action='SELECT') 
    
    #bpy.context.view_layer.objects.active = mesh_objects
    #bpy.ops.object.mode_set(mode="EDIT") #Activating Edit mode
    bpy.ops.object.editmode_toggle()
   
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    view3dArea = area
                    view3dRegion = region
                    break

    override = bpy.context.copy()
    override['area'] = view3dArea
    override['region'] = view3dRegion
    view3dArea.spaces.active.region_3d.view_perspective = 'CAMERA'
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations = 1)
    view3dArea.spaces.active.shading.show_xray = False

    #bpy.ops.view3d.view_camera(override)
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    bpy.ops.view3d.select_box(override,  xmin=0, xmax=10000, ymin=0, ymax=10000, mode='SET')
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    bpy.ops.view3d.select_box(override,  xmin=-10000, xmax=0, ymin=-10000, ymax=0, mode='ADD')
    bpy.ops.object.editmode_toggle() 
    #bpy.ops.view3d.view_camera(override)

def check_visibility(scene, camera_object, mesh_object):
 
    if bpy.context.mode == 'EDIT_MESH':
        bm = bmesh.from_edit_mesh(mesh_object.data)
        verts = [ v.index for v in bm.verts if v.select ]
    else:
        verts = [ v.index for v in mesh_object.data.vertices if v.select ]
    #print(mesh_object.name)
    #print("SELECTED ", len(verts))
    #print("TOTAL ", len(mesh_object.data.vertices))
    return len(verts)/len(mesh_object.data.vertices)


if __name__ == '__main__':
    print("starting")
    scene = bpy.data.scenes['Scene']
    camera_object = bpy.data.objects['Camera']
    mesh_objects = list()
    mesh_objects.append(bpy.data.objects['Kellogs1'])
    mesh_objects.append(bpy.data.objects['Kellogs2'])
    mesh_objects.append(bpy.data.objects['Kellogs3'])
    mesh_objects.append(bpy.data.objects['Kellogs4'])
    mesh_object = bpy.data.objects['Kellogs1']
    prepare_visibility_check(scene, camera_object)
    for obj in mesh_objects:
        check_visibility(scene, camera_object, obj)
