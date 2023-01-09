# from https://blender.stackexchange.com/questions/38009/3x4-camera-matrix-from-blender-camera

import numpy


import bpy
import bpy_extras
from mathutils import Matrix
from mathutils import Vector

import bpy
from mathutils import Matrix, Vector

#---------------------------------------------------------------
# 3x4 P matrix from Blender camera
#---------------------------------------------------------------

# BKE_camera_sensor_size
def get_sensor_size_(sensor_fit, sensor_x, sensor_y):
    if sensor_fit == 'VERTICAL':
        return sensor_y
    return sensor_x

# BKE_camera_sensor_fit
def get_sensor_fit(sensor_fit, size_x, size_y):
    if sensor_fit == 'AUTO':
        if size_x >= size_y:
            return 'HORIZONTAL'
        else:
            return 'VERTICAL'
    return sensor_fit

def get_camera_data(camera):
    camd = camera.data
    f_in_mm = camd.lens
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = camd.sensor_width
    sensor_height_in_mm = camd.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
    if (camd.sensor_fit == 'VERTICAL'):
        # the sensor height is fixed (sensor fit is horizontal), 
        # the sensor width is effectively changed with the pixel aspect ratio
        s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio 
        s_v = resolution_y_in_px * scale / sensor_height_in_mm
    else: # 'HORIZONTAL' and 'AUTO'
        # the sensor width is fixed (sensor fit is horizontal), 
        # the sensor height is effectively changed with the pixel aspect ratio
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
        s_u = resolution_x_in_px * scale / sensor_width_in_mm
        s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm

    # Parameters of intrinsic calibration matrix K
    alpha_u = f_in_mm * s_u
    alpha_v = f_in_mm * s_v
    u_0 = resolution_x_in_px*scale / 2 + camd.shift_x * resolution_x_in_px
    v_0 = resolution_y_in_px*scale / 2 + camd.shift_y * resolution_x_in_px
    skew = 0 # only use rectangular pixels

    K = Matrix(
        ((alpha_u, skew,    u_0),
        (    0  ,  alpha_v, v_0),
        (    0  ,    0,      1 )))
    return K

def another_get_calibration_matrix_K_from_blender(mode='complete'):

    scene = bpy.context.scene

    scale = scene.render.resolution_percentage / 100
    width = scene.render.resolution_x * scale # px
    height = scene.render.resolution_y * scale # px

    camdata = scene.camera.data

    if mode == 'simple':

        aspect_ratio = width / height
        K = numpy.zeros((3,3), dtype=numpy.float32)
        K[0][0] = width / 2 / numpy.tan(camdata.angle / 2)
        K[1][1] = height / 2. / numpy.tan(camdata.angle / 2) * aspect_ratio
        K[0][2] = width / 2.
        K[1][2] = height / 2.
        K[2][2] = 1.

        K.transpose()
    
    if mode == 'complete':

        focal = camdata.lens # mm
        sensor_width = camdata.sensor_width # mm
        sensor_height = camdata.sensor_height # mm
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

        if (camdata.sensor_fit == 'VERTICAL'):
            # the sensor height is fixed (sensor fit is horizontal), 
            # the sensor width is effectively changed with the pixel aspect ratio
            s_u = width / sensor_width / pixel_aspect_ratio 
            s_v = height / sensor_height
        else: # 'HORIZONTAL' and 'AUTO'
            # the sensor width is fixed (sensor fit is horizontal), 
            # the sensor height is effectively changed with the pixel aspect ratio
            pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
            s_u = width / sensor_width
            s_v = height * pixel_aspect_ratio / sensor_height

        # parameters of intrinsic calibration matrix K
        alpha_u = focal * s_u
        alpha_v = focal * s_v
        u_0 = width / 2
        v_0 = height / 2
        skew = 0 # only use rectangular pixels

        K = numpy.array([
            [alpha_u,    skew, u_0],
            [      0, alpha_v, v_0],
            [      0,       0,   1]
        ], dtype=numpy.float32)
    
    return K

def simple_get_camera_data(camera):

    scene = bpy.context.scene

    scale = scene.render.resolution_percentage / 100
    width = scene.render.resolution_x * scale # px
    height = scene.render.resolution_y * scale # px

    camdata = camera.data

    aspect_ratio = width / height
    K = numpy.zeros((3,3), dtype=numpy.float32)
    K[0][0] = width / 2 / numpy.tan(camdata.angle / 2)
    K[1][1] = height / 2 / numpy.tan(camdata.angle / 2) * aspect_ratio
    K[0][2] = width / 2 + camdata.shift_x * width
    K[1][2] = height / 2 + camdata.shift_x * width
    K[2][2] = 1.

    K.transpose()
    
    cam_data = dict(
			K = K,
			Scale = scale
			)
    
    return cam_data

def set_calibration_matrix_K_from_blender(K, camd, width = 0, height = 0):

    if height == 0:
        height = K[1][2] * 2

    if width == 0:    
        width = K[0][2] * 2

    scene = bpy.context.scene

    scale = scene.render.resolution_percentage / 100

    scene.render.resolution_x = width / scale
    scene.render.resolution_y = height / scale

    angle = 2 * numpy.arctan((width / K[0][0]) / 2)

    camd.data.angle = angle

    shift_x = K[0][2] - (width / 2)
    shift_y = K[1][2] - (height / 2)

    fac_x = shift_x / width
    fac_y = shift_y / width

    camd.data.shift_x = fac_x
    camd.data.shift_y = fac_y

    print("Setting shift x to ", fac_x, " and shift y to ", fac_y)

    #aspect_ratio1 = K[1][1] / (height / 2. / numpy.tan(angle / 2))

    #aspect_ratio2 = width / height

def set_intrinsics_from_K_matrix(K, cam_ob,  image_width: int, image_height: int,
                                 clip_start: float = None, clip_end: float = None):
    cam = cam_ob.data

    fx, fy = K[0][0], K[1][1]
    cx, cy = K[0][2], K[1][2]

    # If fx!=fy change pixel aspect ratio
    pixel_aspect_x = pixel_aspect_y = 1
    if fx > fy:
        pixel_aspect_y = fx / fy
    elif fx < fy:
        pixel_aspect_x = fy / fx

    # sensor size in mm, view in px
    pixel_aspect_ratio = pixel_aspect_y / pixel_aspect_x
    view_fac_in_px = get_view_fac_in_px(cam, pixel_aspect_x, pixel_aspect_y, image_width, image_height)
    sensor_size_in_mm = get_sensor_size(cam)

    f_in_mm = fx * sensor_size_in_mm / view_fac_in_px

    shift_x = (cx - (image_width - 1) / 2) / -view_fac_in_px
    shift_y = (cy - (image_height - 1) / 2) / view_fac_in_px * pixel_aspect_ratio

    print("here")

    # set intrinsics
    cam.shift_x = shift_x
    cam.shift_y = shift_y
    cam.lens = f_in_mm


def get_sensor_size(cam: bpy.types.Camera) -> float:
    if cam.sensor_fit == 'VERTICAL':
        sensor_size_in_mm = cam.sensor_height
    else:
        sensor_size_in_mm = cam.sensor_width
    return sensor_size_in_mm


def get_view_fac_in_px(cam: bpy.types.Camera, pixel_aspect_x: float, pixel_aspect_y: float,
                       resolution_x_in_px: int, resolution_y_in_px: int) -> int:
    # Determine the sensor fit mode to use
    if cam.sensor_fit == 'AUTO':
        if pixel_aspect_x * resolution_x_in_px >= pixel_aspect_y * resolution_y_in_px:
            sensor_fit = 'HORIZONTAL'
        else:
            sensor_fit = 'VERTICAL'
    else:
        sensor_fit = cam.sensor_fit

    # Based on the sensor fit mode, determine the view in pixels
    pixel_aspect_ratio = pixel_aspect_y / pixel_aspect_x
    if sensor_fit == 'HORIZONTAL':
        view_fac_in_px = resolution_x_in_px
    else:
        view_fac_in_px = pixel_aspect_ratio * resolution_y_in_px

    return view_fac_in_px




# Build intrinsic camera parameters from Blender camera data
#
# See notes on this in 
# blender.stackexchange.com/questions/15102/what-is-blenders-camera-projection-matrix-model
# as well as
# https://blender.stackexchange.com/a/120063/3581
def get_calibration_matrix_K_from_blender(camd):
    if camd.type != 'PERSP':
        raise ValueError('Non-perspective cameras not supported')
    scene = bpy.context.scene
    f_in_mm = camd.lens
    scale = scene.render.resolution_percentage / 100
    resolution_x_in_px = scale * scene.render.resolution_x
    resolution_y_in_px = scale * scene.render.resolution_y
    sensor_size_in_mm = get_sensor_size_(camd.sensor_fit, camd.sensor_width, camd.sensor_height)
    sensor_fit = get_sensor_fit(
        camd.sensor_fit,
        scene.render.pixel_aspect_x * resolution_x_in_px,
        scene.render.pixel_aspect_y * resolution_y_in_px
    )
    pixel_aspect_ratio = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x
    if sensor_fit == 'HORIZONTAL':
        view_fac_in_px = resolution_x_in_px
    else:
        view_fac_in_px = pixel_aspect_ratio * resolution_y_in_px
    pixel_size_mm_per_px = sensor_size_in_mm / f_in_mm / view_fac_in_px
    s_u = 1 / pixel_size_mm_per_px
    s_v = 1 / pixel_size_mm_per_px / pixel_aspect_ratio

    # Parameters of intrinsic calibration matrix K
    u_0 = resolution_x_in_px / 2 - camd.shift_x * view_fac_in_px
    v_0 = resolution_y_in_px / 2 + camd.shift_y * view_fac_in_px / pixel_aspect_ratio
    skew = 0 # only use rectangular pixels

    K = Matrix(
        ((s_u, skew, u_0),
        (   0,  s_v, v_0),
        (   0,    0,   1)))
    return K

# Returns camera rotation and translation matrices from Blender.
# 
# There are 3 coordinate systems involved:
#    1. The World coordinates: "world"
#       - right-handed
#    2. The Blender camera coordinates: "bcam"
#       - x is horizontal
#       - y is up
#       - right-handed: negative z look-at direction
#    3. The desired computer vision camera coordinates: "cv"
#       - x is horizontal
#       - y is down (to align to the actual pixel coordinates 
#         used in digital images)
#       - right-handed: positive z look-at direction
def get_3x4_RT_matrix_from_blender(cam):
    # bcam stands for blender camera
    R_bcam2cv = Matrix(
        ((1, 0,  0),
        (0, -1, 0),
        (0, 0, -1)))

    # Transpose since the rotation is object rotation, 
    # and we want coordinate rotation
    # R_world2bcam = cam.rotation_euler.to_matrix().transposed()
    # T_world2bcam = -1*R_world2bcam @ location
    #
    # Use matrix_world instead to account for all constraints
    location, rotation = cam.matrix_world.decompose()[0:2]
    R_world2bcam = rotation.to_matrix().transposed()

    # Convert camera location to translation vector used in coordinate changes
    # T_world2bcam = -1*R_world2bcam @ cam.location
    # Use location from matrix_world to account for constraints:     
    T_world2bcam = -1*R_world2bcam @ location

    # Build the coordinate transform matrix from world to computer vision camera
    R_world2cv = R_bcam2cv@R_world2bcam
    T_world2cv = R_bcam2cv@T_world2bcam

    # put into 3x4 matrix
    RT = Matrix((
        R_world2cv[0][:] + (T_world2cv[0],),
        R_world2cv[1][:] + (T_world2cv[1],),
        R_world2cv[2][:] + (T_world2cv[2],)
        ))
    return RT

def get_3x4_P_matrix_from_blender(cam):
    K = get_calibration_matrix_K_from_blender(cam.data)
    RT = get_3x4_RT_matrix_from_blender(cam)
    return K@RT, K, RT

# ----------------------------------------------------------

if __name__ == "__main__":
    cam = bpy.data.objects['Camera']
    print(get_calibration_matrix_K_from_blender(cam.data))

    new_K = numpy.array([
            [1837,    0, 619.5],
            [      0, 1837, 325.5],
            [      0,       0,   1]
        ], dtype=numpy.float32)

    #set_intrinsics_from_K_matrix(new_K, cam, 1240, 652)

    #print(get_calibration_matrix_K_from_blender(cam.data))




if __name__ == "__mayn__":
    # Insert your camera name here
    cam = bpy.data.objects['Camera']
    
    P, K, RT = get_3x4_P_matrix_from_blender(cam)
    print("K")
    print(K)
    """print("RT")
    print(RT)
    print("P")
    print(P)"""

    """new_K = numpy.zeros((3,3), dtype=numpy.float32)
    new_K[0][0] = 1837
    new_K[1][1] = 0
    new_K[0][2] = 325.5 # 619.5
    new_K[1][2] = 1837.
    new_K[2][2] = 619.5 # 325.5

    new_K.transpose()"""


    new_K = numpy.array([
            [1837,    0, 619.5],
            [      0, 1837, 325.5],
            [      0,       0,   1]
        ], dtype=numpy.float32)

    set_calibration_matrix_K_from_blender(new_K, cam, 1240, 652)

    #print(get_3x4_RT_matrix_from_blender(cam))


    print(get_calibration_matrix_K_from_blender(cam.data))

    # Bonus code: save the 3x4 P matrix into a plain text file
    # Don't forget to import numpy for this
    #numpy = numpy.matrix(P)
    #numpy.savetxt("/tmp/P3x4.txt", numpy)  # to select precision, use e.g. fmt='%.2f'


