import bpy
import random
import bmesh
import mathutils
from mathutils.bvhtree import BVHTree
from contextlib import contextmanager
import sys, os

### Some functions multiple classes use

### Function to mute console output
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


### Hides an object and all its children in the render
def hide_obj_and_children(obj):
    for child in obj.children:
        hide_obj_and_children(child)
    obj.hide_render = True

### Un-hides an object and all its children in the render
def show_obj_and_children(obj):
	for child in obj.children:
		show_obj_and_children(child)
	obj.hide_render = False

### Checks if objects are intersecting
def are_objects_intersecting(obj1, obj2):
		BMESH_1 = bmesh.new()
		BMESH_1.from_mesh(obj1.data)
		BMESH_1.transform(obj1.matrix_world)
		BVHtree_1 = BVHTree.FromBMesh(BMESH_1)

		BMESH_2 = bmesh.new()
		BMESH_2.from_mesh(obj2.data)
		BMESH_2.transform(obj2.matrix_world)
		BVHtree_2 = BVHTree.FromBMesh(BMESH_2)

		inter = BVHtree_1.overlap(BVHtree_2)
			#if list is empty, no objects are touching
		if inter != []:
			return True
		else:
			return False

### Hides an object if it intersects with one of the given object list object_check
def hide_on_intersection(obj, object_check):
    for obj_check in object_check:
        if obj_check.hide_render == False and obj_check.name != obj.name and obj_check.type != 'CAMERA' :
            check = are_objects_intersecting(obj, obj_check)
            if check:
                hide_obj_and_children(obj)
                print("\n ____ Hiding ", obj.name, " because it intersects with ", obj_check.name, " ! \n")
                bpy.context.view_layer.update()
                continue
        #if obj.hide_render == False:
            #object_check.append(obj)
    bpy.context.view_layer.update()


### conversion between srgb color and linear color
def srgb2lin(s):
    if s <= 0.0404482362771082:
        lin = s / 12.92
    else:
        lin = pow(((s + 0.055) / 1.055), 2.4)
    return lin


def lin2srgb(lin):
    if lin > 0.0031308:
        s = 1.055 * (pow(lin, (1.0 / 2.4))) - 0.055
    else:
        s = 12.92 * lin
    return s


