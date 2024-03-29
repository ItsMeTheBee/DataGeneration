﻿import bpy
import random
import bmesh
import mathutils
import math
from . import Utils
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification

### Shuffle the rotation of an object using euler representation
class ShuffleRotEuler(Modification):
	def __init__(self, range=[-1, 1], objects=[], hide_on_intersection = False,  multi_range = False):
		self.hide = hide_on_intersection
		self.Range = range
		self.multiRange = multi_range
		super(ShuffleRotEuler, self).__init__(objects)
	
	def performAction(self):
		random.shuffle(self.Objects)
		object_check = list()
		for obj in self.Objects:
			self.Action(obj)
			if self.hide:
				for obj_check in object_check:
					check = self.are_objects_intersecting(obj, obj_check)
					if check:
						Utils.hide_obj_and_children(obj)
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

# Rotations is stored in rads: 2π = 360°
class ShuffleXRotEuler(ShuffleRotEuler):
	def Action(self, obj):
		obj.hide_render = False
		if self.multiRange:
			Range = random.choice(self.Range)
			if isinstance(Range, list): 
				obj.rotation_euler.x = math.radians(random.uniform(Range[0], Range[1]))
			else:
				obj.rotation_euler.x = math.radians(Range)
		else:
			obj.rotation_euler.x = math.radians(random.uniform(self.Range[0], self.Range[1]))
		bpy.context.view_layer.update()

class ShuffleYRotEuler(ShuffleRotEuler):
	def Action(self, obj):
		obj.hide_render = False
		if self.multiRange:
			Range = random.choice(self.Range)
			if isinstance(Range, list): 
				obj.rotation_euler.y = math.radians(random.uniform(Range[0], Range[1]))
			else:
				obj.rotation_euler.y = math.radians(Range)
		else:
			obj.rotation_euler.y = math.radians(random.uniform(self.Range[0], self.Range[1]))
		bpy.context.view_layer.update()

class ShuffleZRotEuler(ShuffleRotEuler):
	def Action(self, obj):
		obj.hide_render = False
		if self.multiRange:
			Range = random.choice(self.Range)
			if isinstance(Range, list): 
				obj.rotation_euler.z = math.radians(random.uniform(Range[0], Range[1]))
			else:
				obj.rotation_euler.z = math.radians(Range)
		else:
			obj.rotation_euler.z = math.radians(random.uniform(self.Range[0], self.Range[1]))
		bpy.context.view_layer.update()
