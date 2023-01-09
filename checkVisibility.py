""" https://blender.stackexchange.com/questions/7198/save-the-2d-bounding-box-of-an-object-in-rendered-image-to-a-text-file """

import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d

import numpy as np
import bmesh
import time
import toml


def zoom_to_g(scene, camera, object):
    camera.location, foo = camera.camera_fit_coords(scene, [co for corner in object.bound_box for co in corner])

def check_visibility(scene, camera_object, mesh_object, use_vertices = True, use_faces = False, use_edges = False):
    bpy.ops.object.mode_set(mode="OBJECT")
    if bpy.context.mode == 'EDIT_MESH':
        bm = bmesh.from_edit_mesh(mesh_object.data)
        verts = [ v.index for v in bm.verts if v.select ]
        faces = [ f.index for f in bm.polygons if f.select ]
        edges = [ e.index for e in bm.edges if e.select ]
    else:
        verts = [ v.index for v in mesh_object.data.vertices if v.select ]
        faces = [ f.index for f in mesh_object.data.polygons if f.select ]
        edges = [ e.index for e in mesh_object.data.edges if e.select ]
    #print(mesh_object.name)
    vert_visibility = len(verts)/len(mesh_object.data.vertices)
    face_visibility = len(faces)/len(mesh_object.data.polygons)
    edge_visibility = len(edges)/len(mesh_object.data.edges)
    #print("PERCENTAGE VERTS ", vert_visibility)
    #print("PERCENTAGE FACES ", face_visibility)
    #print("PERCENTAGE EDGES ", edge_visibility)
    num = 0
    overall_visibility = 0
    if use_vertices:
        overall_visibility = overall_visibility + vert_visibility
        num  = num + 1
    if use_faces:
        overall_visibility = overall_visibility + face_visibility
        num  = num + 1
    if use_edges:
        overall_visibility = overall_visibility + edge_visibility
        num  = num + 1
    overall_visibility = overall_visibility / num
    #print("--> overall visibility ", overall_visibility , "\n")
    return overall_visibility

############################### modified from https://blenderartists.org/t/select-all-faces-visible-from-camera/1210826
def view3d_find():
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    return region, rv3d
    return None, None

def view3d_camera_border(scene):
    obj = scene.camera
    #cam = obj.data

    #frame = cam.view_frame(scene)
    frame = bpy.context.scene.camera.data.view_frame(scene=bpy.context.scene)

    # move from object-space into world-space 
    frame = [obj.matrix_world @ v for v in frame]

    # move into pixelspace
    region, rv3d = view3d_find()
    #print(region, rv3d)
    frame_px = [location_3d_to_region_2d(region, rv3d, v) for v in frame]
    return frame_px
#'''

def getView3dAreaAndRegion(context):
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    return area, region


def select_border(context, corners, extend=True):
    override = getOverride(context)
    bpy.ops.view3d.select_box(override, wait_for_input=False, xmin=corners[0], xmax=corners[1], ymin=corners[2], ymax=corners[3], mode='SET')
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    bpy.ops.view3d.select_box(override, wait_for_input=False, xmin=corners[0], xmax=corners[1], ymin=corners[2], ymax=corners[3], mode='ADD')    
    return True

def prepareForSelection(override):
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action='DESELECT') 
    for ob in bpy.context.scene.objects:
        if ob.hide_render == True:
            ob.hide_set(True)
        else:
            ob.hide_set(False)

    bpy.context.view_layer.objects.active = bpy.context.view_layer.objects.active
    bpy.ops.object.select_all(action='SELECT') 
    bpy.ops.object.editmode_toggle()

    override['area'].spaces.active.region_3d.view_perspective = 'CAMERA'
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations = 1)
    override['area'].spaces.active.shading.show_xray = False
    


def getOverride(context):
    view3dArea, view3dRegion = getView3dAreaAndRegion(context)
    override = context.copy()
    override['area'] = view3dArea
    override['region'] = view3dRegion
    return override

def getCorners(cam_corners):
    '''
    returns xmin,xmax,ymin,ymax
    '''
    print(cam_corners)
    return [cam_corners[2][0],cam_corners[0][0],cam_corners[2][1],cam_corners[0][1]]

def prepare_camera(scene, cam, obj):
    scene.camera = cam
    cam.constraints["Track To"].target = obj
    lens = 1 / max(obj.dimensions) - obj.location.z
    print(lens)
    bpy.data.cameras[cam.name].lens = lens

def restore_camera(scene, cam):
    scene.camera = cam

def select_camera_view(scene, camera_object, mesh_object):
    mesh_object.select_set(True) 
    bpy.context.view_layer.objects.active = mesh_object
    prepare_camera(scene, camera_object, mesh_object)
    # go to editmode
    bpy.ops.object.mode_set(mode="EDIT")
    vertex, edge, face = True, True, True
    bpy.context.tool_settings.mesh_select_mode = (vertex, edge, face)

    # set camera view
    override = getOverride(bpy.context)
    bpy.ops.view3d.view_camera(override)
    prepareForSelection(override)

    # get camera borders in view coordinates
    cam_corners = getCorners(view3d_camera_border(bpy.context.scene))
    
    # select stuff in borders
    select_border(bpy.context, cam_corners, extend = False)

################

def load_objects(names, ignore_names=None, category=""):
	mesh_obj=list()
	if ignore_names != "" and ignore_names is not None:
		available = [obj.name for obj in bpy.data.objects]
		mesh_names = [x for x in available if x not in ignore_names]

	elif names is not None:
		mesh_names = names

	else:
		print("Unable to load ", category)
		return mesh_obj
	try:
		mesh_objects = [bpy.data.objects[name] for name in mesh_names]
		for mesh in mesh_objects:
			mesh_obj.append(mesh)
	except:
		print("Error loading objects")
	return mesh_obj

if __name__ == '__main__':
    print("starting")
    config = toml.load("/home/sally/work/DataGen/DataGenAtWork/configTableDecoy.toml")
    bpy.context.view_layer.update()
    scene = bpy.data.scenes[config['General']['Scene']]
    camera_object = bpy.data.objects[config['General']['Camera']]
    mode = config['General']['Mode']
    print("MODE: ",mode)
    steps = config['General']['Steps']
    bounds = config['General']['Boundaries']
    print("BOUNDARIES ARE ",bounds)		

    lamp_obj = list()
    special_obj = list()
    mesh_obj = list()

    lamp_obj = load_objects(config['Objects']['Lamps'], category="Lamps")
    mesh_obj = load_objects(config['Objects']['Names'], config['Objects']['Ignore'], "Objects")
    special_obj = load_objects(config['Objects']['Special'], category="Special")
    decoy_obj = load_objects(config['Objects']['Decoy'], category="Decoy")

    scn = bpy.context.scene
    cam = bpy.data.objects['Camera.001']
    obj = bpy.data.objects['bearing']
    #restore_camera(camera_object)
    #check_visibility(scene, camera_object, mesh_obj.first())
    for obj in mesh_obj:
        print("SELECTING ", obj.name)
        select_camera_view(scene, cam, obj)
        check_visibility(scene, cam, obj)
        time.sleep(2)
    restore_camera(scene, camera_object)

    print("DONE")

