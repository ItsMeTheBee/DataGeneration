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
from Modifications.MaskBlackNWhite import MaskBlackNWhite

# ____________________________________________ Create image

def render(scene, camera_object, mesh_objects, file_prefix="render", folder="renders"):
	# Rendering
	# https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
	filename = str(file_prefix)
	bpy.context.scene.render.filepath = os.path.join(base_dir+ "/" + folder + "/", filename + '.png')
	bpy.ops.render.render(write_still=True)

# ____________________________________________ Create labels

def createYoloTxtFile(scene, camera_object, mesh_objects, config, file_prefix="render", bounds=None):
	#names_to_labels = { 'Cube': 0, 'Cube.001': 1, 'Cube.002': 2, 'Cube.003': 3, 'Cube.004': 4}
	print("Creating labels")
	print(bounds)
	filename = str(file_prefix)
	path = os.path.join(base_dir+'/labels/', filename + '.txt')
	with open(path, 'w+') as file:
		""" Get the bounding box coordinates for each mesh """
		for object in mesh_objects:
			print("labeling ", object.name)
			if object.hide_render is True:
				print(object.name + " is hidden - not labeling this!")
				continue
			name = config['Labels'][object.name]
			bounding_box = boundingBox.camera_view_bounds_2d(scene, camera_object, object, bounds)
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

# ____________________________________________ Apply every modification and create image + labels

def batch_render(scene, camera, lamp, objects, special, steps, config, bounds):
	mods = createMods(camera, lamp, objects, special)
	for k in range(0, steps):
		for mod in mods:
			mod.performAction()
		file_prefix=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		render(scene, camera, objects, file_prefix)
		print("render done")
		createYoloTxtFile(scene, camera, objects, config, file_prefix, bounds)
	print("DONE! =)")

# ____________________________________________ Loop through each frame and create image + labels 

def path_render(scene, camera, objects, steps, config, bounds):
	for i in range(scene.frame_start,scene.frame_end):
		if i > steps:
			print("done - reached desired image count")
			return
		scene.frame_current = i
		file_prefix=datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
		render(scene, camera, objects, file_prefix)
		createYoloTxtFile(scene, camera, objects, config, file_prefix, bounds)
	print("done - no frames left to render")

def mask_render(scene, camera, objects, steps, mod):
	print("rendering original images" )
	for i in range(scene.frame_start,scene.frame_end):
		if i > steps:
			print("done - reached desired image count")
			break
		scene.frame_current = i
		file_prefix=i
		render(scene, camera, objects, file_prefix)

	scene.frame_current = 0
	mod.performAction()

	print("rendering masked images" )
	for j in range(scene.frame_start,scene.frame_end):
		if j > steps:
			print("done - reached desired image count")
			break
		scene.frame_current = j
		file_prefix=j
		render(scene, camera, objects, file_prefix, "labels")

	print("done - no frames left to render")
	scene.frame_current = 0
	mod.restoreColor()

def load_objects(names, ignore_names=None, category=""):
	mesh_obj=list()
	if ignore_names is not None:
		available = [obj.name for obj in bpy.data.objects]
		mesh_names = [x for x in available if x not in ignore_names]

	elif names is not None:
		mesh_names = names.split(',')

	else:
		print("Unable to load ", category)
		return mesh_obj

	mesh_objects = [bpy.data.objects[name] for name in mesh_names]
	for mesh in mesh_objects:
		mesh_obj.append(mesh)
	return mesh_obj

# ____________________________________________ Read config values & Load objects

def main():
	config = configparser.ConfigParser(allow_no_value=True)
	config.read(os.path.join(base_dir, 'config_atWork.ini'))
	bpy.context.view_layer.update()

	scene = bpy.data.scenes[config['General']['Scene']]
	camera_object = bpy.data.objects[config['General']['Camera']]
	mode = config['General']['Mode']
	print("MODE: ",mode)
	steps = config['General']['Steps']
	bounds = config['General']['Boundaries'].split(',')
	bounds = list(map(float, bounds))
	print("BOUNDARIES ARE ",bounds)

	lamp_obj = list()
	special_obj = list()
	mesh_obj = list()

	lamp_obj = load_objects(config['Objects']['Lamps'], category="Lamps")
	mesh_obj = load_objects(config['Objects']['Names'], config['Objects']['Ignore'], "Objects")
	special_obj = load_objects(config['Objects']['Special'], category="Special")

	if mode != "Mask":
		if mode == "Mods":	 
			batch_render(scene, camera_object, lamp_obj, mesh_obj, special_obj, int(steps), config, bounds)
			return

		if mode == "Path":
			path_render(scene, camera_object, mesh_obj, int(steps), config, bounds)
			return

	if mode == "Mask":
		mask_true_obj = list()
		mask_false_obj = list()

		mask_true_obj = load_objects(config['Mask']['Mask_True_Objects'], category="Mask True Objects")
		mask_false_obj = load_objects(config['Mask']['Mask_False_Objects'], category="Mask False Objects")

		mask_true_material = config['Mask']['Mask_True_Mat']
		mask_false_material = config['Mask']['Mask_False_Mat']

		mask_false_color = config['Mask']['Mask_False_Color'].split(",")
		mask_false_color = list(map(int, mask_false_color))

		mask_true_color = config['Mask']['Mask_True_Color'].split(",")
		mask_true_color = list(map(int, mask_true_color))

		maskMod = MaskBlackNWhite(mask_true_obj, mask_false_obj, mask_true_color, mask_false_color, mask_true_material, mask_false_material)
		mask_render(scene, camera_object, mesh_obj, int(steps), maskMod)
		return

	else:
		print("Please select an available Mode")

if __name__ == '__main__':
	main()
