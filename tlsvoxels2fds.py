"""
Updated 11/25

This script takes in an input file (on the command line or specified in the main function) consisting of a table of
voxel XYZ coordinates as well as a column with the number of points contained in each voxel. It then writes to a file
containing an &INIT PART line for each voxel at the specified coordinate with the proportional amount of biomass.

In addition to the &INIT PART, the script also writes the &PART definition, but the assumption is that the contents of
the output file will by copy/pasted into a full FDS file with the necessary &SURF and &MATL definitions for whatever
foliage or thermally thin components you're dealing with.

- Anthony Marcozzi
"""

import sys
import numpy as np

def calculate_total_points(input_file):
    """
    Calculates the total number of points in a voxel data table (for calculating density)
    :param input_file: voxel data table with a number of points for each voxel
    :return: the total number of points across all voxels
    """
    voxel_array = np.genfromtxt(input_file)
    return np.sum(voxel_array[:, 3])


def write_voxels_to_fds(filein, output, total_points):
    """
    Function takes in a voxel data table with XYZ voxel location and the number of points in each voxel. The user
    provides voxel resolution, foliage biomass, and particle density parameters within this function.
    #TODO: Read in these parameters from some sort of
    :param filein: data table with XYZ coordinate of center of the voxel and # of points in the voxel
    :param output: output .txt file to write to
    :param total_points: The total number of points across al voxels (for calculating density)
    """
    res = 0.05                      # resolution of the voxel (in meters)
    foliage_biomass = 40100         # in kg
    particle_density = 514          # density of fuel in a unit volume of fuel kg/m^3
    # total_points = calculate_total_points(filein)

    # Write commend to FDS file with copy/paste instructions
    output.write("! Copy and paste the following into your FDS input file\n")
    # Write foliage part ID to the FDS input file
    part_line_out = f"&PART ID='foliage'\n\tSURF_ID='foliage'\n\tDRAG_COEFFICIENT=2.8\n\tSHAPE_FACTOR=0.25\n\t" \
                    f"SAMPLING_FACTOR=10\n\t" \
                    f"QUANTITIES='PARTICLE TEMPERATURE','PARTICLE MASS'\n\tSTATIC=.TRUE\n\tCOLOR='FOREST GREEN' /\n\n"
    output.write(str(part_line_out))

    for line in filein:
        segs = line.split()
        X = float(segs[0])
        Y = float(segs[1])
        Z = float(segs[2])
        voxel_density = float(segs[3]) / total_points
        voxel_bulk_density = voxel_density * foliage_biomass
        packing_ratio = voxel_bulk_density / particle_density
        init_line_out = f"&INIT PART_ID='foliage', XB={X-res/2:.4f},{X+res/2:.4f}," \
                        f"{Y-res/2:.4f},{Y+res/2:.4f}," \
                        f"{Z-res/2:.4f},{Z+res/2:.4f}, " \
                        f"N_PARTICLES_PER_CELL=1, CELL_CENTERED=.TRUE., PACKING_RATIO={packing_ratio:.8f} /\n"
        output.write(str(init_line_out))


if __name__ == '__main__':
    if len(sys.argv) > 1:  # pass the input_file file through the command line
        input = sys.argv[1]
    else:
        # raise Exception("Please pass a voxel_metrics data table through the command line")
        # input = "norway_spruce_voxel_metrics.txt"
        input = "norway_spruce_voxel_metrics_005res.txt"

    with open(input, "r") as filein:
        total_points = calculate_total_points(filein)
    with open(input, "r") as filein:
        with open("output_tree.txt", 'w') as fileout:
            write_voxels_to_fds(filein, fileout, total_points)
