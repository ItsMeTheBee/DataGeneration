import bpy
import random
import bmesh
import mathutils
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification

class ShufflePos(Modification):
	def __init__(self, range=[-5, 5], objects=[], hide_on_intersection = False):
		self.hide = hide_on_intersection
		self.Range = range
		super(ShufflePos, self).__init__(objects)

	def performAction(self):
		print("performing action")
		random.shuffle(self.Objects)
		object_check = list()
		for obj in self.Objects:
			self.Action(obj)
			if self.hide:
				for obj_check in object_check:
					check = self.are_objects_intersecting(obj, obj_check)
					if check:
						obj.hide_render = True
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

class ShuffleXPos(ShufflePos):
	def Action(self, obj):
		obj.hide_render = False
		obj.location.x = 0.01 * random.randrange(self.Range[0], self.Range[1])
		bpy.context.view_layer.update()

class ShuffleYPos(ShufflePos):
	def Action(self, obj):
		obj.hide_render = False
		obj.location.y = 0.01 * random.randrange(self.Range[0], self.Range[1])
		bpy.context.view_layer.update()

class ShuffleZPos(ShufflePos):
	def Action(self, obj):
		print("shuffling Z")
		obj.hide_render = False
		obj.location.z = 0.01 * random.randrange(self.Range[0], self.Range[1])
		bpy.context.view_layer.update()
