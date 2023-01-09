
import sys
import os
from sys import platform

import bpy, os
from math import sin, cos, pi
import numpy as np
import sys
import random
from datetime import datetime
import toml

import yaml


base_dir = os.path.dirname(bpy.data.filepath)
dir = base_dir

if not dir in sys.path:
    sys.path.append(dir)

import boundingBox
import checkVisibility
import BOP
import GetCameraMatrixK
from Modifications import Utils

from Modifications.ShufflePos import ShuffleXPos, ShuffleYPos, ShuffleZPos
from Modifications.ShuffleRotEuler import ShuffleXRotEuler, ShuffleYRotEuler, ShuffleZRotEuler
from Modifications.ShuffleRotQuaternion import ShuffleRotQuaternion
from Modifications.ShuffleColor import ShuffleRGBColor, ShuffleBackground, ShuffleImageTexture, ShuffleColorSpace
from Modifications.Mask import  MaskComposition
from Modifications.VisibilityMods import HideInRGB
from Modifications.RandomMods import RandomDisappear
from Modifications.CameraMods import ShuffleFocalLength
from Modifications.ShuffleMaterial import ShuffleMaterials, ShuffleMaterialProperties
from Modifications.ShuffleVector import ShuffleVector

from Modifications.MeshMods import CreateHull

## Global variable for the location of the configuration file
base_config = "/home/vision/Work/DataGen/DataGeneration/config.toml"
#config = toml.load(base_config)


def hide_obj_and_children(obj):
	for child in obj.children:
		hide_obj_and_children(child)
	obj.hide_render = True

def show_obj_and_children(obj):
	for child in obj.children:
		show_obj_and_children(child)
	obj.hide_render = False

def calcVisibilityThresh(obj, config):
	visibility_thresh = config[obj.name]["visibility_thresh_factor"]
	factor = obj.location.z / 2 + visibility_thresh
	return min(factor, 0.8)


def hideInvisibleObjects(scene, camera_object, visibility_camera, mesh_objects, config):
	for object in mesh_objects:
		if object.hide_render == True:
			print(object.name + " is hidden - not labeling this and hiding all children!")
			hide_obj_and_children(object)
			continue

		if "visibility_thresh_factor" in config[object.name]:
			visibility = 0.0
			### Mute the visibility check because it spams everything
			with Utils.suppress_stdout():
				checkVisibility.select_camera_view(scene, visibility_camera, object)
				visibility = checkVisibility.check_visibility(scene, visibility_camera, object)
				checkVisibility.restore_camera(scene, camera_object)

			if visibility < config[object.name]["visibility_thresh_factor"]:
				print(object.name, "visibilitiy is ", visibility, " -> not visible in render - HIDING this and all children")
				hide_obj_and_children(object)

# ____________________________________________ Create image

def render(scene, camera_object, mesh_objects, path="/home/data/", file_prefix="rgb"):
	# Rendering
	# https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script

	filename = str(file_prefix)
	bpy.context.scene.render.filepath = os.path.join(path,  filename + '.png')
	bpy.ops.render.render(write_still=True)

# ____________________________________________ Create bbox labels in yolo format

def createYoloTxtFile(scene, camera_object, visibility_camera, mesh_objects, config, path="/home/data/", file_prefix="bbox", bounds=None):
	random.shuffle(mesh_objects)
	filename = str(file_prefix)

	path = os.path.join(path, filename + '.txt')
	with open(path, 'w+') as file:
		""" Get the bounding box coordinates for each mesh """
		for object in mesh_objects:
			if object.hide_render == False:
				if not object.name in config['Labels']:
					print(object.name + " has no label - not labeling this!")
					continue			

				name = config['Labels'][object.name]
				show_obj_and_children(object)
				bounding_box = boundingBox.camera_view_bounds_2d(scene, camera_object, object, bounds)
				if bounding_box:
					new_line = str(name) + " " + str(bounding_box[0])+ " " + str(bounding_box[1]) + " " + str(bounding_box[2]) + " " + str(bounding_box[3]) + '\n'
					file.write(new_line)

				else: 
					hide_obj_and_children(object)
					print("Hiding ", object.name, " and all children")


# ____________________________________________ Create bop (6DoF) labels in yaml format
def createBopTxtFile(scene, camera_object, visibility_camera, mesh_objects, config, path="/home/data/", file_prefix="bop", bounds=None, store_in_one_file = True, K = None):
	filename = str(file_prefix)
		 
	if(store_in_one_file):
		ground_truth_file = os.path.join(path, 'gt.yml')
		camera_info_file = os.path.join(path, 'info.yml')
		
	else:
		ground_truth_file = os.path.join(path, str(file_prefix), '_gt.yml')
		camera_info_file = os.path.join(path, str(file_prefix),'_info.yml')

	if not os.path.isfile(ground_truth_file):
		f = open(ground_truth_file, 'w+')
		f.close

	if not os.path.isfile(camera_info_file):
		f = open(camera_info_file, 'w+')
		f.close

	# using int instead of string for efficientpose
	prefix = int(file_prefix)

	#Prepare to open the file with reading capabilities
	with open(ground_truth_file,'r') as infile:
		infile.seek(0)
		file_data = yaml.load(infile, Loader=yaml.Loader)
		if not file_data:
			file_data =  dict()

	for object in mesh_objects:
		if not object.name in config['Labels']:
			continue
		
		if object.hide_render == True:
			continue

		name = config['Labels'][object.name]

		pos = BOP.get_relative_object_position(scene, camera_object, object)
		pos = [round(element * 1000,2) for element in pos]
	
		rot = BOP.get_relative_object_rotation(scene, camera_object, object)
		rot_list = np.concatenate( rot.tolist(), axis=0 )
		
		new_data = dict(
				cam_R_m2c = rot_list.tolist(),
				cam_t_m2c = pos,
				obj_id = name
			)
		
		try: 
			file_data[prefix].append(new_data)
		except:
			file_data[prefix] =  list()
			file_data[prefix].append(new_data)
		

	with open(ground_truth_file, "w") as f:
		yaml.safe_dump(file_data, f, default_flow_style=False)

	print("Wrote ground truth to ", ground_truth_file)


	#Prepare to open the file with reading capabilities
	with open(camera_info_file,'r') as infile:
		infile.seek(0)
		file_data = yaml.load(infile, Loader=yaml.Loader)

	for object in mesh_objects:
		if not object.name in config['Labels']:
			continue

		name = config['Labels'][object.name]

		cam_data = GetCameraMatrixK.get_calibration_matrix_K_from_blender(camera_object.data)

		k_matrix = np.concatenate( cam_data, axis=0 )


		new_data = dict(
				cam_K = k_matrix.tolist(),
				depth_scale = 1
			)
	
		if not file_data:
				file_data =  dict()
			
		file_data[prefix] = new_data			

	with open(camera_info_file, "w") as f:
		yaml.safe_dump(file_data, f, default_flow_style=False)
	
	print("Wrote camera info to ", camera_info_file)


# ____________________________________________ Create Modifications

def createCameraMods(camera):
	mods = list()
	cameras = list()
	cameras.append(camera)
	#modFocalLength = ShuffleFocalLength([11, 38], cameras)
	#mods.append(modFocalLength)
	modZRot = ShuffleZRotEuler([0, 360], cameras, False)
	mods.append(modZRot)
	modXRot = ShuffleXRotEuler([0, 360], cameras, False)
	mods.append(modXRot)
	modYRot = ShuffleYRotEuler([0, 360], cameras, False)
	mods.append(modYRot)
	return mods

def createLightMods(lights):
	mods = list()
	modXPos = ShuffleXPos([-200, 200], lights, False)
	mods.append(modXPos)
	modYPos = ShuffleYPos([-200, 200], lights, False)
	mods.append(modYPos)
	return mods


def createObjectMods(objects, config):
	mods = list()	
	for obj in objects:
			obj_list = list()
			obj_list.append(obj)

			if "Rotation" in config[obj.name]:
				try:
					if config[obj.name]["Rotation"]["mode"] == "Quaternion":
						modQuatRot = ShuffleRotQuaternion(config[obj.name]["Rotation"]["X"],config[obj.name]["Rotation"]["Y"], config[obj.name]["Rotation"]["Z"], obj_list, False)
						mods.append(modQuatRot)
						print("Using quaternions for ", obj.name)
				except:
					modZRot = ShuffleZRotEuler(config[obj.name]["Rotation"]["Z"], obj_list, False)
					mods.append(modZRot)
					modYRot = ShuffleYRotEuler(config[obj.name]["Rotation"]["Y"], obj_list, False)
					mods.append(modYRot)
					modXRot = ShuffleXRotEuler(config[obj.name]["Rotation"]["X"], obj_list, False)
					mods.append(modXRot)
					print("Using axis rotation for ", obj.name)

			if "Position" in config[obj.name]:				
				modZPos = ShuffleZPos(config[obj.name]["Position"]["Z"], obj_list, False, False, config[obj.name]["Position"]["Z_normed_to_1m"])
				mods.append(modZPos)
				modXPos = ShuffleXPos(config[obj.name]["Position"]["X"], obj_list, False, False, config[obj.name]["Position"]["X_normed_to_1m"])
				mods.append(modXPos)
				modYPos = ShuffleYPos(config[obj.name]["Position"]["Y"], obj_list, True, False, config[obj.name]["Position"]["Y_normed_to_1m"])
				mods.append(modYPos)
				print("Shuffling X Y Z pose for ", obj.name)

			if "PrincipledBSDF" in config[obj.name]:			
				modMetallic = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Metallic", config[obj.name]["PrincipledBSDF"]["Metallic"])
				mods.append(modMetallic)

				modSpecular = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Specular", config[obj.name]["PrincipledBSDF"]["Specular"])
				mods.append(modSpecular)

				modSpecularTint = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Specular Tint", config[obj.name]["PrincipledBSDF"]["SpecularTint"])
				mods.append(modSpecularTint)

				modRoughness = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Roughness", config[obj.name]["PrincipledBSDF"]["Roughness"])
				mods.append(modRoughness)

				modAnisotropic = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Anisotropic", config[obj.name]["PrincipledBSDF"]["Anisotropic"])
				mods.append(modAnisotropic)

				modAnisotropicRotation = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Anisotropic Rotation", config[obj.name]["PrincipledBSDF"]["AnisotropicRotation"])
				mods.append(modAnisotropicRotation)

				modClearcoat = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Clearcoat", config[obj.name]["PrincipledBSDF"]["Clearcoat"])
				mods.append(modClearcoat)

				modClearcoatRoughness = ShuffleMaterialProperties(obj_list, "Principled BSDF", "Clearcoat Roughness", config[obj.name]["PrincipledBSDF"]["ClearcoatRoughness"])
				mods.append(modClearcoatRoughness)
				print("Principled BSDF for ", obj.name)

			if "BrickTexture" in config[obj.name]:
				for key in config[obj.name]["BrickTexture"]:
					modBrickTexture = ShuffleMaterialProperties(obj_list, "Brick Texture", config[obj.name]["BrickTexture"][key]["PropertyName"], config[obj.name]["BrickTexture"][key]["value"])
				mods.append(modBrickTexture)
				print("BrickTexture for ", obj.name)


			if "Mapping" in config[obj.name]:
				for key in config[obj.name]["Mapping"]:
					modMapping = ShuffleVector(obj_list, "Mapping", key, config[obj.name]["Mapping"][key])
				mods.append(modMapping)
				print("Mapping for ", obj.name)

			if "ShuffleMaterials" in config[obj.name]:
				modShuffleMaterials = ShuffleMaterials(obj_list)
				mods.append(modShuffleMaterials)
				print("Shuffling materials for ", obj.name)
		
			if "ShuffleMaterialConfig" in config[obj.name]:
				for key in config[obj.name]["ShuffleMaterialConfig"]:
					sub_config  = config[obj.name]["ShuffleMaterialConfig"][key]
					mod = ShuffleMaterialProperties(obj_list, sub_config["NodeName"], sub_config["PropertyName"], sub_config["value"], sub_config["material_name"])
					mods.append(mod)
					print("Shuffling material config for ", obj.name)
			
			if "Color" in config[obj.name]:
				try:
					for key in config[obj.name]["Color"]:
						color_config  = config[obj.name]["Color"][key]
						modShuffleColor = ShuffleRGBColor(obj_list, color_config["NodeName"], color_config["PropertyName"], color_config["value1"],color_config["value2"],color_config["value3"], color_config["mode"], color_config["material_name"])
						mods.append(modShuffleColor)
						print("Shuffling color with keys for ", obj.name)
				except:
					color_config  = config[obj.name]["Color"]
					modShuffleColor = ShuffleRGBColor(obj_list, color_config["NodeName"], color_config["PropertyName"], color_config["value1"],color_config["value2"],color_config["value3"], color_config["mode"], color_config["material_name"])
					mods.append(modShuffleColor)
					print("Shuffling color for ", obj.name)

			if "Disappear" in config[obj.name]:
				modDisappear = RandomDisappear(obj_list, config[obj.name]["Disappear"]["value"])
				mods.append(modDisappear)

			#else:
				#print("no color config for ", obj.name)

	
	return mods

def createMaskMods(objects, path, config):
	mods = list()

	index_dict = {}
	for obj in objects:
			index_dict[obj.name] = config[obj.name]["id"]
	
	modMask = MaskComposition(objects, index_dict, path = path)
	mods.append(modMask)

	for obj in objects:
			obj_list = list()
			obj_list.append(obj)
			try:
				if config[obj.name]["hide_in_rgb"]:
					#print("Hiding ", obj.name, " in RGB ", config[obj.name]["hide_in_rgb"])
					print("Hiding ", obj.name, " in RGB ")
					modHideInRgb = HideInRGB(obj_list)
					mods.append(modHideInRgb)
			except:
				pass
	return mods

def createWorldMods(config):
	world_obj= list()
	world_mods= list()
	if config['General']['ShuffleWorld']:
		world_obj.append(bpy.context.scene.world)
		#world_mods.append(ShuffleBackground(world_obj, config['World']['Backgrounds'], True, shuffle_strength=[0.8, 1.2]))
		world_mods.append(ShuffleBackground(world_obj, config['World']['Backgrounds'], True, shuffle_strength=[config['World']['Strength']['Min'], config['World']['Strength']['Min']]))
	return world_mods

def createMods(camera, lamp, objects, decoys, special, config):
	mods = list()
	mods.extend(createWorldMods(config))
	mods.extend(createCameraMods(camera))
	mods.extend(createLightMods(lamp))
	mods.extend(createObjectMods(objects, config))
	mods.extend(createObjectMods(decoys, config))
	mods.extend(createObjectMods(special, config))
	return mods


def get_latest_index(render_path):
	numbers = list()
	for filename in os.listdir(render_path):
		if filename.endswith(".png"):
			number = int(filename[:-4])
			numbers.append(number)
	
	if not numbers:
		return 1
	else:	
		max_num = max(numbers)
		print("Resuming rendering at ", max_num)
		return max_num


# ____________________________________________ Apply every modification and create image + labels

def batch_render(config_dict):

	print("RENDER PWTH ", config_dict["render_path"])
	print("BBOX PWTH ", config_dict["bbox_path"])
	print("SEG PWTH ", config_dict["seg_path"])
	print("BOP PWTH ", config_dict["bop_path"])

	scene = config_dict["scene"]

	mods = createMods(config_dict["camera"], config_dict["lamp_objs"], config_dict["label_objs"], config_dict["decoy_objs"],
	config_dict["special_objs"], config_dict["config"])
	maskMods = list()

	if config_dict["seg_mask"]:
		maskMods = createMaskMods(config_dict["label_objs"], config_dict["seg_path"], config_dict["config"])
		for maskMod in maskMods:
			maskMod.performPreProcessing()
	
	#available_steps = range(get_latest_index(render_path), steps+1)
	available_steps = range(get_latest_index(config_dict["render_path"]), config_dict["steps"]+1)
	if config_dict["path"]:
		available_steps = range(scene.frame_start,scene.frame_end)

	for k in available_steps:
		print("\n _____________________ \n")
		print("Starting image no.", k)

		for obj in config_dict["label_objs"]:
			show_obj_and_children(obj)

		if config_dict["path"]: 
			scene.frame_current = k

		for mod in mods:
			mod.performAction()


		#file_prefix=datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]
		file_prefix = f'{k:06}'

		hideInvisibleObjects(scene, config_dict["camera"], config_dict["visibility_camera"], config_dict["label_objs"], config_dict["config"])

		if config_dict["yolo_labels"]:
			createYoloTxtFile(scene, config_dict["camera"], config_dict["visibility_camera"], config_dict["label_objs"], config_dict["config"], config_dict["bbox_path"], file_prefix, config_dict["bounds"])
		
		if config_dict["bop_labels"]:
			createBopTxtFile(scene, config_dict["camera"], config_dict["visibility_camera"], config_dict["label_objs"], config_dict["config"], config_dict["bop_path"], file_prefix, config_dict["bounds"])
		
		if config_dict["seg_mask"]:
			for maskMod in maskMods:
				maskMod.performAction(file_prefix)  

			render.use_compositing = True
			render.use_sequencer = False      
			
			render(scene, config_dict["camera"], config_dict["label_objs"], config_dict["render_path"], file_prefix)

			for maskMod in maskMods:
				maskMod.performPostProcessing()	

	print("DONE! =)")


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
			print("Loaded " , mesh.name, " class ", category)
	except:
		print("Error loading objects of ", category)
	return mesh_obj

# ____________________________________________ Helper methods

def hideAllObjects(Objs):
	for obj in Objs:
		hide_obj_and_children(obj)


# ____________________________________________ Read config values & Load objects
def parse_config_and_render(config):
	out_dict = dict()

	out_dict["config"] = config
	out_dict["scene"] = bpy.data.scenes[config['General']['Scene']]
	out_dict["camera"] = bpy.data.objects[config['General']['Camera']]
	out_dict["visibility_camera"] = bpy.data.objects[config['General']['Visibility_Check']]
	out_dict["steps"] = config['General']['Steps']
	out_dict["bounds"] = None

	if 'Boundaries' in config['General']:
		out_dict["bounds"] = config['General']['Boundaries']

	#print("BOUNDARIES ARE ",bounds)		

	out_dict["yolo_labels"] = config['General']['CreateYoloLabels']
	out_dict["bop_labels"] = config['General']['CreateBOPLabels']
	out_dict["seg_mask"] = config['General']['CreateSegmentationMask']
	out_dict["path"] = config['General']['AnimateAlongPath']



	out_dict["lamp_objs"] = load_objects(config['Objects']['Lamps'], category="Lamps")
	label_objects = load_objects(config['Objects']['Names'], config['Objects']['Ignore'], "Objects")
	out_dict["label_objs"] = label_objects
	out_dict["decoy_objs"] = load_objects(config['Objects']['Decoy'], category="Decoy")
	out_dict["special_objs"] = load_objects(config['Objects']['Special'], category="Special")


	if config['General']['SingleObjects']:
		for obj in label_objects:
			if obj.name in config['Labels']:

				"""render_path = os.path.join(base_dir, config['Files']['Folder'], str(config['Labels'][obj.name]), "renders")
				bbox_path = os.path.join(base_dir, config['Files']['Folder'], str(config['Labels'][obj.name]), "bbox_labels")
				bop_path = os.path.join(base_dir, config['Files']['Folder'], str(config['Labels'][obj.name]), "bop_labels")
				seg_path = os.path.join(base_dir, config['Files']['Folder'], str(config['Labels'][obj.name]), "seg_labels")"""

				out_dict["render_path"] = os.path.join(base_dir, config['Files']['Folder'], str(config['Labels'][obj.name]), "rgb")
				out_dict["bbox_path"] = os.path.join(base_dir, config['Files']['Folder'], str(config['Labels'][obj.name]), "bbox_labels")
				out_dict["bop_path"] = os.path.join(base_dir, config['Files']['Folder'], str(config['Labels'][obj.name]), "")
				out_dict["seg_path"] = os.path.join(base_dir, config['Files']['Folder'], str(config['Labels'][obj.name]), "merged_masks")

				if not os.path.exists(out_dict["render_path"]):
					os.makedirs(out_dict["render_path"])

				if not os.path.exists(out_dict["bbox_path"]):
					os.makedirs(out_dict["bbox_path"])	

				if not os.path.exists(out_dict["bop_path"] ):
					os.makedirs(out_dict["bop_path"] )	

				if not os.path.exists(out_dict["seg_path"]):
					os.makedirs(out_dict["seg_path"])	


				hideAllObjects(mesh_obj)
				current_obj = list()
				current_obj.append(obj)

				out_dict["single_object"] = True
				out_dict["current_object"] = current_obj

				#out_dict["label_objects"] = current_obj
				batch_render(out_dict)
			else:
				continue

	else:

		folder = config['Files']['Folder']

		"""render_path = os.path.join(base_dir, config['Files']['Folder'], "renders")
		bbox_path = os.path.join(base_dir, config['Files']['Folder'], "bbox_labels")
		bop_path = os.path.join(base_dir, config['Files']['Folder'], "bop_labels")
		seg_path = os.path.join(base_dir, config['Files']['Folder'], "seg_labels")"""

		out_dict["render_path"]  = os.path.join(base_dir, config['Files']['Folder'], "rgb")
		out_dict["bbox_path"] = os.path.join(base_dir, config['Files']['Folder'], "bbox_labels")
		out_dict["bop_path"] = os.path.join(base_dir, config['Files']['Folder'], "")
		out_dict["seg_path"] = os.path.join(base_dir, config['Files']['Folder'], "merged_masks")

		if not os.path.exists(out_dict["render_path"]):
			os.makedirs(out_dict["render_path"])

		if not os.path.exists(out_dict["bbox_path"]):
			os.makedirs(out_dict["bbox_path"])	

		if not os.path.exists(out_dict["bop_path"] ):
			os.makedirs(out_dict["bop_path"] )	

		if not os.path.exists(out_dict["seg_path"]):
			os.makedirs(out_dict["seg_path"])	
		
		batch_render(out_dict)


def main():
	bpy.context.view_layer.update()

	config = toml.load(base_config)

	if config['Config']['MultiConfig']:
		for file in os.listdir(os.path.join(base_dir+ "/" + config['Config']['Folder'])):
			if file.endswith(".toml"):
				print("found additional config ", file)
				addition = toml.load(os.path.join(base_dir, config['Config']['Folder'] ,file))
				new_config = toml.load([base_config, os.path.join(base_dir, config['Config']['Folder'], file)])
				config = new_config

	parse_config_and_render(config)

	

if __name__ == '__main__':
	main()
