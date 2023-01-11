import bpy
import random
import bmesh
import mathutils
from mathutils.bvhtree import BVHTree
from Modifications.Modification import Modification
from . import Utils

# currently hide_on_intersection works on all other children of the same parent - change that to accept other objects
class ShufflePos(Modification):
	def __init__(self, range=[], objects=[],  hide_on_intersection = True, multi_range = False, scale_with = ""):
		self.hide = hide_on_intersection
		self.Range = range
		self.multiRange = multi_range
		self.scale_with = scale_with
		super(ShufflePos, self).__init__(objects)


### Randomizes objects, makes them visible, sets a randomized location value and hides the objects if it intersects with another object
### If the object has a parent object, its children will be used for the intersection check
	def performAction(self):
		random.shuffle(self.Objects)

		for obj in self.Objects:
			self.Action(obj)

			parent =  obj.parent
			if parent is None:
				object_check = self.Objects
			else:
				object_check = parent.children

			if self.hide:
				Utils.hide_on_intersection(obj, object_check)	


### The same for all axes - kept it separate in case of special behaviour
### If scaleing is active get the current location at the axis to scale with
### Generate a random number from the given range and scale it
### Either by using a random number from a list of numbers, a random numbers from a list of Ranges or a random number from a single Range
### Set the new location and update the view layer		

class ShuffleXPos(ShufflePos):
	def Action(self, obj):
		obj.hide_render = False
		used_range = list(self.Range)
		scale = 1

		if (self.scale_with == "X"):
			scale = abs(obj.location.x)
		if (self.scale_with == "Y"):
			scale = abs(obj.location.y)
		if (self.scale_with == "Z"):
			scale = abs(obj.location.z)
		
		for idx, item in enumerate(used_range):
			used_range[idx] = item * scale

		if self.multiRange:
			used_range = random.choice(used_range)
			if isinstance(Range, list): 
				obj.location.x =  random.uniform((used_range[0], used_range[1]))
			else:
				obj.location.x = used_range
			bpy.context.view_layer.update()
		else:
			obj.location.x = random.uniform(used_range[0], used_range[1])
			bpy.context.view_layer.update()

class ShuffleYPos(ShufflePos):
	def Action(self, obj):
		obj.hide_render = False
		used_range = list(self.Range)
		scale = 1

		if (self.scale_with == "X"):
			scale = abs(obj.location.x)
		if (self.scale_with == "Y"):
			scale = abs(obj.location.y)
		if (self.scale_with == "Z"):
			scale = abs(obj.location.z)
		
		for idx, item in enumerate(used_range):
			used_range[idx] = item * scale

		if self.multiRange:
			used_range = random.choice(used_range)
			if isinstance(Range, list): 
				obj.location.y =  random.uniform((used_range[0], used_range[1]))
			else:
				obj.location.y = used_range
			bpy.context.view_layer.update()
		else:
			obj.location.y = random.uniform(used_range[0], used_range[1])
			bpy.context.view_layer.update()

class ShuffleZPos(ShufflePos):
	def Action(self, obj):
		obj.hide_render = False
		used_range = list(self.Range)
		scale = 1

		if (self.scale_with == "X"):
			scale = abs(obj.location.x)
		if (self.scale_with == "Y"):
			scale = abs(obj.location.y)
		if (self.scale_with == "Z"):
			scale = abs(obj.location.z)
		
		for idx, item in enumerate(used_range):
			used_range[idx] = item * scale
			
		if self.multiRange:
			used_range = random.choice(used_range)
			if isinstance(Range, list): 
				obj.location.z =  random.uniform((used_range[0], used_range[1]))
			else:
				obj.location.z = used_range
			bpy.context.view_layer.update()
		else:
			obj.location.z = random.uniform(used_range[0], used_range[1])
			bpy.context.view_layer.update()
