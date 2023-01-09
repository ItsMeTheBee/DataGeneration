﻿import bpy
import random
import bmesh
import mathutils
import math
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification
from . import Utils


class ShuffleRot(Modification):
	def __init__(self, range=[-1, 1], objects=[], hide_on_intersection = False,  multi_range = False):
		self.hide = hide_on_intersection
		self.Range = range
		self.multiRange = multi_range
		super(ShuffleRot, self).__init__(objects)
	
	def performAction(self):
		random.shuffle(self.Objects)
		object_check = list()
		for obj in self.Objects:
			self.Action(obj)
			if self.hide:
				Utils.hide_on_intersection(obj, object_check)	

# Rotations is stored in rads: 2π = 360°
class ShuffleXRot(ShuffleRot):
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

class ShuffleYRot(ShuffleRot):
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

class ShuffleZRot(ShuffleRot):
	def Action(self, obj):
		obj.hide_render = False
		if self.multiRange:
			Range = random.choice(self.Range)
			if isinstance(Range, list): 
				obj.rotation_euler.z = math.radians(random.uniform(Range[0], Range[1]))
				print("Set rotation of ", obj.name, " to ", obj.rotation_euler.z)
			else:
				obj.rotation_euler.z = math.radians(Range)
		else:
			obj.rotation_euler.z = math.radians(random.uniform(self.Range[0], self.Range[1]))
		bpy.context.view_layer.update()
