import sys
import numpy as np

def calculate_total_points(input_file):
    voxel_array = np.genfromtxt(input_file)
    return np.sum(voxel_array[:, 3])


def write_voxels_to_fds(filein, output, total_points):
    res = 0.1
    foliage_biomass = 40100
    particle_density = 514
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
        input = "norway_spruce_voxel_metrics.txt"

    with open("norway_spruce_voxel_metrics.txt", "r") as filein:
        total_points = calculate_total_points(filein)
    with open("norway_spruce_voxel_metrics.txt", "r") as filein:
        with open("output_tree.txt", 'w') as fileout:
            write_voxels_to_fds(filein, fileout, total_points)
