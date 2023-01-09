import bpy
import random
import bmesh
import mathutils
import math
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification
from scipy.spatial.transform import Rotation as R

def hide_obj_and_children(obj):
    for child in obj.children:
        hide_obj_and_children(child)
        obj.hide_render = True


class ShuffleRotQuaternion(Modification):
	def __init__(self, range_x=[-1, 1], range_y=[-1, 1], range_z=[-1, 1], objects=[], hide_on_intersection = False,  multi_range = False):
		self.hide = hide_on_intersection
		self.RangeX = range_x
		self.RangeY = range_y
		self.RangeZ = range_z
		self.Ranges = [self.RangeX, self.RangeY, self.RangeZ]
		self.multiRange = multi_range
		#print("INIT QUAT SUFFLE WITH ", self.Ranges)
		super(ShuffleRotQuaternion, self).__init__(objects)
	
	def performAction(self):
		random.shuffle(self.Objects)
		object_check = list()
		for obj in self.Objects:
			self.Action(obj)
			if self.hide:
				for obj_check in object_check:
					check = self.are_objects_intersecting(obj, obj_check)
					if check:
						hide_obj_and_children(obj)
						#for child in obj.children:
						#	child.hide_render = True
						bpy.context.view_layer.update()
				if obj.hide_render is False:
					object_check.append(obj)

	def are_objects_intersecting(self, obj1, obj2):
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

	def Action(self, obj):
		obj.hide_render = False
		rot_values = list()
		for cur_range in self.Ranges:
			if self.multiRange:
				Range = random.choice(cur_range)
				if isinstance(Range, list): 
					#rotation_mode    rotation_quaternion
					rot_values.append( random.uniform(Range[0], Range[1]) )
				else:
					rot_values.append( Range )
			else:
				rot_values.append( random.uniform(cur_range[0], cur_range[1]) )

		print("ROT VALUES ARE ", rot_values)
		rot = R.from_euler('xyz', rot_values, degrees = True)

		bpy.data.objects[obj.name].rotation_mode = 'QUATERNION'
		obj.rotation_quaternion.w = rot.as_quat()[3]
		obj.rotation_quaternion.x = rot.as_quat()[0]
		obj.rotation_quaternion.y = rot.as_quat()[1]
		obj.rotation_quaternion.z = rot.as_quat()[2]
		
		bpy.context.view_layer.update()