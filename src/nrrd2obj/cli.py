import argparse
import sys
import nrrd2obj.core as core
from nrrd2obj import __version__


def parse_args(args):
    parser = argparse.ArgumentParser(description="Create a mesh out of a volume, with option to group voxels by values.")

    parser.add_argument(
        "--version",
        action="version",
        version="nrrd2obj {ver}".format(ver=__version__))

    parser.add_argument(
        "--nrrd",
        dest="nrrd",
        required=True,
        metavar="FILE PATH",
        help="The volume file (input .nrrd)",
    )

    parser.add_argument(
        "--obj",
        dest="obj",
        required=True,
        metavar="FILE PATH",
        help="The mesh file (input .obj)",
    )

    parser.add_argument(
        "--mask-values",
        dest="mask_values",
        required=False,
        nargs="+",
        metavar="INTEGERS",
        type=int,
        help="The values of voxel to include in the output mesh. ",
    )

    parser.add_argument(
        "--decimation",
        dest="decimation",
        required=False,
        metavar="FLOAT",
        type=float,
        help="The ratio of original mesh vertices to conserve in [0,0, 1.0]. (default: no decimation)",
    )

    parser.add_argument(
        "--sigma-smooth",
        dest="sigma_smooth",
        required=False,
        metavar="FLOAT",
        type=float,
        default=2.,
        help="The standard deviation of the gaussian kernel applied for smoothing the mesh. The higher the smoother. 0 means no smoothing (default: 2)",
    )

    parser.add_argument(
        "--reverse-winding",
        dest="reverse_winding",
        required=False,
        action="store_true",
        help="Reversing the winding will result in normal vectors pointing the opposite direction (default: no reverse winding)",
    )

    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])
    core.process_from_path(nrrd_path = args.nrrd, 
      obj_path = args.obj, 
      mask_values = args.mask_values, 
      decimation = args.decimation, 
      reverse_winding = args.reverse_winding, 
      sigma_smooth = args.sigma_smooth)
