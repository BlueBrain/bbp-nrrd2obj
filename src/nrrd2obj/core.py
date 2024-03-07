import nrrd
import numpy as np
from skimage import measure
from scipy import ndimage
from simplify import simplify_mesh


def create_mask(arr, mask_values = None):
    mask = np.zeros_like(arr, dtype=np.float32)

    # Fill up the mask with the whole non-zero if mask_values is None
    if mask_values is None:
        mask[arr != 0] = 1.
    else:
        for val in mask_values:
          mask[arr == val] = 1.

    return mask



def mask_to_mesh_data(arr, sigma_smooth = 2):
    if sigma_smooth > 0:
        dilated = ndimage.binary_dilation(arr, iterations = 1).astype(np.float32)
        gaussian_blurred = ndimage.gaussian_filter(dilated - 0.5, sigma=sigma_smooth)

        # Make sure the final mesh has no side-of-box hole
        gaussian_blurred[:, :, 0] = -0.5
        gaussian_blurred[:, :, -1] = -0.5
        gaussian_blurred[:, 0, :] = -0.5
        gaussian_blurred[:, -1, :] = -0.5
        gaussian_blurred[0, :, :] = -0.5
        gaussian_blurred[-1, :, :] = -0.5

        vertices, triangles, normals, values = measure.marching_cubes(gaussian_blurred, gradient_direction="ascent")
        return (vertices, triangles)
    
    else:
        arr_float = arr.astype(np.float32)
        arr_float[:, :, 0] = -0.5
        arr_float[:, :, -1] = -0.5
        arr_float[:, 0, :] = -0.5
        arr_float[:, -1, :] = -0.5
        arr_float[0, :, :] = -0.5
        arr_float[-1, :, :] = -0.5
        vertices, triangles, normals, values = measure.marching_cubes(arr_float)
        return (vertices, triangles)


def export_obj(vertices, triangles, filepath, origin, transform_3x3, reverse_winding = False):
    """
        | xa  xb  xc |
    M = | ya  yb  yc |  --> M is transform_3x3
        | za  zb  zc |

        | x |
    O = | y |  --> O is origin
        | z |
    
    """

    ROUNDER = 4

    M_xa = transform_3x3[0][0]
    M_ya = transform_3x3[0][1]
    M_za = transform_3x3[0][2]

    M_xb = transform_3x3[1][0]
    M_yb = transform_3x3[1][1]
    M_zb = transform_3x3[1][2]

    M_xc = transform_3x3[2][0]
    M_yc = transform_3x3[2][1]
    M_zc = transform_3x3[2][2]

    O_x = origin[0]
    O_y = origin[1]
    O_z = origin[2]

    obj_str = ""

    for v in vertices:
        v_x = v[0]
        v_y = v[1]
        v_z = v[2]
        v_x_world = v_x * M_xa + v_y * M_xb + v_z * M_xc + O_x
        v_y_world = v_x * M_ya + v_y * M_yb + v_z * M_yc + O_y
        v_z_world = v_x * M_za + v_y * M_zb + v_z * M_zc + O_z

        obj_str += f"v {round(v_x_world, ROUNDER)} {round(v_y_world, ROUNDER)} {round(v_z_world, ROUNDER)}\n"

    for t in triangles:
        if reverse_winding:
            obj_str += f"f {str(int(t[0])+1)} {str(int(t[1])+1)} {str(int(t[2])+1)}\n"
        else:
            obj_str += f"f {str(int(t[2])+1)} {str(int(t[1])+1)} {str(int(t[0])+1)}\n"

    f = open(filepath, 'w')
    f.write(obj_str)
    f.close()


def process_from_path(nrrd_path, obj_path, mask_values = None, decimation = None, reverse_winding = False, sigma_smooth = 2):
    volume_data, volume_metadata = nrrd.read(nrrd_path)
    volume_data = np.ascontiguousarray(volume_data)

    origin = volume_metadata["space origin"]
    transform_3x3 = volume_metadata["space directions"]

    process(arr = volume_data, 
      origin = origin, 
      transform_3x3 = transform_3x3, 
      obj_path = obj_path, 
      mask_values = mask_values, 
      decimation = decimation, 
      reverse_winding = reverse_winding, 
      sigma_smooth = sigma_smooth)


def process(arr, origin, transform_3x3, obj_path, mask_values = None, decimation = None, reverse_winding = False, sigma_smooth = 2):
    mask = create_mask(arr, mask_values)
    vertices, triangles = mask_to_mesh_data(arr = mask, sigma_smooth = sigma_smooth)

    if decimation:
      vertices = vertices.astype(np.float64)
      triangles = triangles.astype(np.uint32)
      new_nb_vertices =  int(len(vertices) * decimation)
      print(f"decimating from {len(vertices)} to {new_nb_vertices} vertices...")
      vertices, triangles = simplify_mesh(vertices, triangles, new_nb_vertices)

    export_obj(vertices, triangles, obj_path, origin, transform_3x3, reverse_winding)