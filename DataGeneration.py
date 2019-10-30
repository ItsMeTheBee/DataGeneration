import bpy, os
from math import sin, cos, pi
import numpy as np
import sys
import random
from datetime import datetime
import configparser

base_dir = os.path.dirname(bpy.data.filepath)
dir = base_dir

if not dir in sys.path:
    sys.path.append(dir)

import boundingBox
from Modifications.ShufflePos import ShuffleXPos, ShuffleYPos, ShuffleZPos
from Modifications.ShuffleRot import ShuffleXRot, ShuffleYRot, ShuffleZRot
from Modifications.ShuffleColor import ShuffleMaterial, ShuffleRGBColor

# ____________________________________________ Create image

def render(scene, camera_object, mesh_objects, file_prefix="render"):
	# Rendering
	# https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
	print("rendering")
	filename = str(file_prefix)
	bpy.context.scene.render.filepath = os.path.join(base_dir+'/renders/', filename + '.png')
	bpy.ops.render.render(write_still=True)

# ____________________________________________ Create labels

def createYoloTxtFile(scene, camera_object, mesh_objects, file_prefix="render"):
	#names_to_labels = { 'Cube': 0, 'Cube.001': 1, 'Cube.002': 2, 'Cube.003': 3, 'Cube.004': 4}
	filename = str(file_prefix)
	path = os.path.join(base_dir+'/labels/', filename + '.txt')
	with open(path, 'w+') as file:
		""" Get the bounding box coordinates for each mesh """
		for object in mesh_objects:
			if object.hide_render is True:
				print(object.name + " is hidden - not labeling this!")
				continue
			name = config['Labels'][object.name]
			bounding_box = boundingBox.camera_view_bounds_2d(scene, camera_object, object)
			if bounding_box:
				new_line = str(name) + " " + str(bounding_box[0])+ " " + str(bounding_box[1]) + " " + str(bounding_box[2]) + " " + str(bounding_box[3]) + '\n'
				file.write(new_line)

# ____________________________________________ Create Modifications

def createCameraMods(camera):
	mods = list()
	cameras = list()
	cameras.append(camera)
	modXPos = ShuffleXPos([5, 25], cameras, False)
	mods.append(modXPos)
	modYPos = ShuffleYPos([-12, 22], cameras, False)
	mods.append(modYPos)
	return mods

def createLightMods(lights):
	mods = list()
	modXPos = ShuffleXPos([-200, 200], lights, False)
	mods.append(modXPos)
	modYPos = ShuffleYPos([-200, 200], lights, False)
	mods.append(modYPos)
	return mods

def createObjectMods(objects):
	mods = list()
	modXPos = ShuffleXPos([-5, 30], objects, True)
	mods.append(modXPos)
	modYPos = ShuffleYPos([-20, 36], objects, True)
	mods.append(modYPos)
	modZRot = ShuffleZRot([0, 360], objects, True)
	mods.append(modZRot)
	return mods

def createSpecialObjectMods(special):
	mods = list()
	modMaterial= ShuffleMaterial(special)
	mods.append(modMaterial)
	modColor= ShuffleRGBColor(special)
	mods.append(modColor)
	return mods

def createMods(camera, lamp, objects, special):
	mods = list()
	mods.extend(createCameraMods(camera))
	mods.extend(createLightMods(lamp))
	mods.extend(createSpecialObjectMods(special))
	mods.extend(createObjectMods(objects))
	return mods

# ____________________________________________ Main Loop

def batch_render(scene, camera, lamp, objects, special, steps):
	mods = createMods(camera, lamp, objects, special)
	for k in range(0, steps):
		for mod in mods:
			mod.performAction()
		file_prefix=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		render(scene, camera, objects, file_prefix)
		createYoloTxtFile(scene, camera, objects, file_prefix)
	print("DONE! =)")

# ____________________________________________ Read config values & Load objects

if __name__ == '__main__':
	config = configparser.ConfigParser()
	config.read(os.path.join(base_dir, 'config.ini'))

	scene = bpy.data.scenes[config['Objects']['Scene']]
	camera_object = bpy.data.objects[config['Objects']['Camera']]

	lamp_names = config['Objects']['Lamps'].split(',')
	lamp_obj = [bpy.data.objects[name] for name in lamp_names]

	bpy.context.scene.update()
	special_names = config['Objects']['Special'].split(',')

	ignore_names = config['Objects']['Ignore'].split(',')
	if ignore_names:
		print("ignoring ", ignore_names)
		available = [obj.name for obj in bpy.data.objects]
		mesh_names = [x for x in available if x not in ignore_names]
	else: 
		mesh_names = config['DEFAULT']['Names'].split(',')

	mesh_obj = list()
	mesh_objects = [bpy.data.objects[name] for name in mesh_names]
	for mesh in mesh_objects:
		mesh_obj.append(mesh)

	special_obj = list()
	special_objects = [bpy.data.objects[name] for name in special_names]
	for mesh in special_objects:
		special_obj.append(mesh)

	steps = config['General']['Steps']

	batch_render(scene, camera_object, lamp_obj, mesh_obj, special_obj, int(steps))
