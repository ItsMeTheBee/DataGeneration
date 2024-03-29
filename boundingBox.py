""" https://blender.stackexchange.com/questions/7198/save-the-2d-bounding-box-of-an-object-in-rendered-image-to-a-text-file """

import bpy
import numpy as np
import bmesh


### These functions are used to figure out the bounding box of every object
### The object is transformed to the camera coordinate system
### Then the vertices of the object are iterated and normalized themm to the camera view frame
### The min and max functions obtain the normalized extreme points of the object 
### The values are then clipped to be inside 0.0 and 1.0 ( = inside the camera frame)
### For the YOLO format these can be used directly instead of calculating the pixel values of these normalized values

def camera_view_bounds_2d(scene, camera_object, mesh_object, bounds=None):
    """
    Returns camera space bounding box of the mesh object.

    Gets the camera frame bounding box, which by default is returned without any transformations applied.
    Create a new mesh object based on mesh_object and undo any transformations so that it is in the same space as the
    camera frame. Find the min/max vertex coordinates of the mesh visible in the frame, or None if the mesh is not in view.

    :param scene:
    :param camera_object:
    :param mesh_object:
    :return:
    """

    """ Get the inverse transformation matrix. """

    
    matrix = camera_object.matrix_world.normalized().inverted()
    """ Create a new mesh data block, using the inverse transform matrix to undo any transformations. """
    #mesh = mesh_object.to_mesh(scene, True, 'RENDER')
    mesh = mesh_object.to_mesh()
    mesh.transform(mesh_object.matrix_world)
    mesh.transform(matrix)

    """ Get the world coordinates for the camera frame bounding box, before any transformations. """
    frame = [-v for v in camera_object.data.view_frame(scene=scene)[:3]]

    lx = []
    ly = []

    for v in mesh.vertices:
        co_local = v.co
        z = -co_local.z

        if z <= 0.0:
            """ Vertex is behind the camera; ignore it. """
            continue
        else:
            """ Perspective division """
            frame = [(v / (v.z / z)) for v in frame]

        min_x, max_x = frame[1].x, frame[2].x
        min_y, max_y = frame[0].y, frame[1].y

        x = (co_local.x - min_x) / (max_x - min_x)
        y = (co_local.y - min_y) / (max_y - min_y)

        lx.append(x)
        ly.append(y)

    #mesh.to_mesh_clear()

    """ Image is not in view if all the mesh verts were ignored """
    if not lx or not ly:
        return None

    min_x = min(lx) #np.clip(min(lx), 0.0, 1.0)
    min_y = min(ly) #np.clip(min(ly), 0.0, 1.0)
    max_x = max(lx) #np.clip(max(lx), 0.0, 1.0)
    max_y = max(ly) #np.clip(max(ly), 0.0, 1.0)

    """ Figure out the rendered image size - not needed right now
    render = scene.render
    fac = render.resolution_percentage * 0.01
    dim_x = render.resolution_x * fac
    dim_y = render.resolution_y * fac """

    # Only return a bounding boy of the object is within the given bounds
    if bounds:
        if min_x < bounds[0]:
            #print("Bounding box of ", mesh_object.name ," outside of boundaries - min_x is ", min_x, " boundary is ", bounds[0])
            return None
        if min_y < bounds[1]:
            #print("Bounding box of ", mesh_object.name ," outside of boundaries - min_y is ", min_y, " boundary is ", bounds[1])
            return None
        if max_x > bounds[2]:
            #print("Bounding box of ", mesh_object.name ," outside of boundaries - max_x is ", max_x, " boundary is ", bounds[2])
            return None
        if max_y > bounds[3]:
            #print("Bounding box of ", mesh_object.name ," outside of boundaries - max_y is ", max_y, " boundary is ", bounds[3])
            return None

    
    min_x = np.clip(min_x, 0.0, 1.0)
    min_y = np.clip(min_y, 0.0, 1.0)
    max_x = np.clip(max_x, 0.0, 1.0)
    max_y = np.clip(max_y, 0.0, 1.0)

    """ Image is not in view if both bounding points exist on the same side """
    if min_x == max_x or min_y == max_y:
        #print("Bounding box of ", mesh_object.name ," outside of view")
        return None

    # we use yolo format -> x and y of bounding box center, width and height of bounding box - everything in % of total picture size
    #return (min_x, min_y), (max_x, max_y)
    mid_x = (min_x + max_x) / 2
    width = (max_x - min_x) 
    #blender output: 1 top, 0 bottom - we need it the other way round
    mid_y = 1- ((min_y + max_y) / 2)
    height = (max_y - min_y) 

    #print ("\n", 'mid x ',mid_x, ' mid y ', mid_y, 'width ',width, ' height ', height)

    return ([mid_x, mid_y, width, height])

if __name__ == '__main__':
	print("starting")
	scene = bpy.data.scenes['Scene']
	camera_object = bpy.data.objects['Camera']
	mesh_object = bpy.data.objects['Cube']
	camera_view_bounds_2d(scene, camera_object, mesh_object)
