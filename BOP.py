""" https://blender.stackexchange.com/questions/7198/save-the-2d-bounding-box-of-an-object-in-rendered-image-to-a-text-file """

import bpy
import numpy as np
import bmesh
from math import degrees, pi
from scipy.spatial.transform import Rotation as R


def get_relative_object_position(scene, camera_object, mesh_object):
    """
    if (mesh_object in  camera_object.children):
        #print("object is a child of the camera - no calculation required")
        #matrix = camera_object.matrix_world.normalized().inverted()
        x_lin = mesh_object.location[0] 
        y_lin = mesh_object.location[1] #-mesh_object.location[1] 
        z_lin = mesh_object.location[2] 

        #world_diff = mesh_object.matrix_world

    else:
        #matrix = camera_object.matrix_world.normalized().inverted()
        x_lin = mesh_object.location[0] - camera_object.location[0]
        y_lin = (mesh_object.location[1] - camera_object.location[1]) #-(mesh_object.location[1] - camera_object.location[1])
        z_lin = mesh_object.location[2] - camera_object.location[2]

        world_diff = mesh_object.matrix_world - camera_object.matrix_world
        print(world_diff)

    print(" x lin ", x_lin)
    print(" y lin ", y_lin)
    print(" z lin ", z_lin)
    print(type(x_lin))
    """
    world = mesh_object.matrix_world.to_translation()
    #print(world)

    matrix = camera_object.matrix_world
    R = np.array([
        [matrix[0][0],matrix[0][1],matrix[0][2]],
        [matrix[1][0],matrix[1][1],matrix[1][2]],
        [matrix[2][0],matrix[2][1],matrix[2][2]]])

    world = np.dot(world, R)

    x_lin = float(world[0])
    y_lin = float(world[1])
    z_lin = float(world[2])

    #world_diff = mesh_object.matrix_world - camera_object.matrix_world
    #print(world_diff)

    #print(" x lin ", x_lin)
    #print(" y lin ", y_lin)
    #print(" z lin ", z_lin)
    
    #print(type(x_lin))

    ### siemens
    #trans_vec = (-x_lin, z_lin, -y_lin)
    trans_vec = (-x_lin, y_lin, z_lin)

    ### non siemens
    #trans_vec = (x_lin, y_lin, z_lin)
    return trans_vec

def get_relative_object_rotation(scene, camera_object, mesh_object):
    
    axis = camera_object.matrix_world.to_quaternion()
    q = mesh_object.matrix_world.to_quaternion()
    rotdif = axis.rotation_difference(q)
    #print("\n _____ quat")
    #print(rotdif)
    #print(q)

    #print("\n _____ matrix")
    #print(camera_object.matrix_world - mesh_object.matrix_world)
    #print(mesh_object.matrix_local)

    #print((rotdif.to_euler().x, rotdif.to_euler().y, rotdif.to_euler().z))

    #print( mesh_object.matrix_local)

    """

    R = np.array([
        [matrix[0][0],matrix[0][1],matrix[0][2]],
        [matrix[1][0],matrix[1][1],matrix[1][2]],
        [matrix[2][0],matrix[2][1],matrix[2][2]]])

    print(R)

    return R"""

    #print(mesh_object.matrix_local.Rotation())

    ### debug
    #mat = R.from_quat([0, 0, 0, 1])

    ### for siemens
        #mat = euler_to_rotMat(rotdif.to_euler().x, -rotdif.to_euler().y, -rotdif.to_euler().z)
    mat = R.from_quat([rotdif.x, -rotdif.y, -rotdif.z, rotdif.w])
    #return mat
    
    # non siemens
        #mat = euler_to_rotMat(rotdif.to_euler().x, rotdif.to_euler().y, rotdif.to_euler().z)
    #mat = R.from_quat([rotdif.x, rotdif.y, rotdif.z, rotdif.w])

    return mat.as_matrix()
   


def euler_to_rotMat(roll, pitch, yaw):
    Rz_yaw = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw),  np.cos(yaw), 0],
        [          0,            0, 1]])
    Ry_pitch = np.array([
        [ np.cos(pitch), 0, np.sin(pitch)],
        [             0, 1,             0],
        [-np.sin(pitch), 0, np.cos(pitch)]])
    Rx_roll = np.array([
        [1,            0,             0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll),  np.cos(roll)]])
    # R = RzRyRx

    #rotMat = np.dot(Rx_roll, np.dot(Ry_pitch, Rz_yaw))

    ### for siemens
    rotMat = np.dot(Rz_yaw, np.dot(Ry_pitch, Rx_roll))

    #print(rotMat)
    return rotMat
    

if __name__ == '__main__':
	print("starting")
	scene = bpy.data.scenes['Scene']
	camera_object = bpy.data.objects['Camera']
	mesh_object = bpy.data.objects['Palette']
	print(get_relative_object_position(scene, camera_object, mesh_object))
