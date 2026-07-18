import ansys.mapdl.core as pymapdl
import numpy as np
from scipy.interpolate import RegularGridInterpolator

#Material number
AISI_4140 = 1

#File i/o locations
input_file=r"C:\DiMSL\Pressure loads for PyANSYS\pressure_load_spatially_varied.txt"
output_file=r"C:\DiMSL\Deformation Results\Spatially varied deformations\Spatially varied deformation due to sinusodal wave load.txt"

#Lists are created for initial data storage, but are not suitable for numerical analysis yet
x_values = []
y_values = []
pressure_vals = []

#Populate initial data lists from MATLAB-generated x,y,P file
with open(input_file, "r") as input:
    p_x_y_matrix = input.readlines()

for i in range(len(p_x_y_matrix)):
    values = p_x_y_matrix[i].split(",")
    x_values.append(float(values[0]))
    y_values.append(float(values[1]))
    pressure_vals.append(float(values[2]))

#Populate numpy arrays for numerical analysis
x_array = np.array(x_values)
y_array = np.array(y_values)
p_array = np.array(pressure_vals)

#Recover unique grid axes from flattened data
x_coords = np.unique(x_array)
y_coords = np.unique(y_array)

#Build 2D pressure grid with 0s for intialization
P_grid = np.zeros((len(y_coords), len(x_coords)))

for i in range(len(p_array)):
    x_index = np.where(x_coords == x_array[i])[0][0]
    y_index = np.where(y_coords == y_array[i])[0][0]
    P_grid[y_index, x_index] = p_array[i]

#Build interpolator using recovered grid axes and pressure grid
interpolator = RegularGridInterpolator((y_coords, x_coords), P_grid, method="linear", bounds_error=False, fill_value=None)

#Safety-net if ANSYS MAPDL launch fails
try:
    print("Launching MAPDL")
    mapdl = pymapdl.launch_mapdl()
    print("MAPDL running")

    #Pre-processing______________________________________________________________________________________________________
    mapdl.prep7()
    mapdl.rectng(0, 254, 0, 127)

    #Linear Elastic properties
    mapdl.mp("EX", AISI_4140, 200000)    # Avg Young's Modulus
    mapdl.mp("PRXY", AISI_4140, 0.285)   # Avg Poisson's ratio
    mapdl.mp("DENS", AISI_4140, 7.85e-9) # Density in tonnes/mm^3

    #Strength and Thermal properties
    mapdl.tb("FAIL", AISI_4140)
    mapdl.tbdata(AISI_4140, 415, 655)    # Yield strength, tensile strength
    mapdl.mp("REFT", AISI_4140, 1416)    # Melting point in C

    #Specify shells and thickness
    mapdl.et(AISI_4140, "SHELL181")
    mapdl.sectype(AISI_4140, "SHELL")
    mapdl.secdata(0.635)

    #Specify meshing
    mapdl.mshape(1, "2D")  # Triangular elements
    mapdl.mshkey(0)        # Free mesh
    mapdl.esize(2.5)       # Element size in mm

    #Specify active mesh material and element type
    mapdl.mat(AISI_4140)
    mapdl.type(1)

    #Apply mesh
    mapdl.amesh("ALL")

    #Plot mesh for testing purposes, comment when not needed
    #mapdl.eplot()

    mapdl.allsel()

    #Interpolate pressure values onto ANSYS mesh by querying each element's centroid,
    #then looking up the corresponding pressure from the MATLAB grid via interpolation.
    all_element_numbers = mapdl.mesh.enum
    element_numbers = []
    interpolated_pressures = []

    for elem_num in all_element_numbers:
        cx = mapdl.queries.centrx(int(elem_num))
        cy = mapdl.queries.centry(int(elem_num))
        p_value = interpolator([cy, cx])[0]
        element_numbers.append(int(elem_num))
        interpolated_pressures.append(p_value)

    print(f"Interpolated pressure for {len(element_numbers)} elements")
    mapdl.allsel()

    #Solution______________________________________________________________________________________________
    mapdl.run("/SOLU")
    mapdl.antype(0)    # Static analysis
    mapdl.nlgeom(0)
    mapdl.nsubst(10, 100, 5)

    #Clamp boundaries
    mapdl.lsel("S", "LOC", "X", 0)
    mapdl.lsel("A", "LOC", "X", 254)
    mapdl.lsel("A", "LOC", "Y", 0)
    mapdl.lsel("A", "LOC", "Y", 127)
    mapdl.nsll("S")

    #Fix displacement of edges to 0
    mapdl.d("ALL", "UX", 0)
    mapdl.d("ALL", "UY", 0)
    mapdl.d("ALL", "UZ", 0)
    mapdl.d("ALL", "ROTX", 0)
    mapdl.d("ALL", "ROTY", 0)
    mapdl.d("ALL", "ROTZ", 0)
    mapdl.allsel()

    #Apply interpolated pressure to each element
    for i in range(len(element_numbers)):
        mapdl.sfe(element_numbers[i], 1, "PRES", 1, -float(interpolated_pressures[i]) / 1e6)
    print(f"Applied pressure to {len(element_numbers)} elements")

    mapdl.solve()
    mapdl.finish()

    #Post-processing________________________________________________________________________________________________________________
    mapdl.post1()

    #Graph contour plot, testing purposes, uncomment when needed
    '''mapdl.set("LAST")
    mapdl.view(1,1,1,1)
    mapdl.plnsol("U", "Z")'''

    mapdl.set("LAST")
    
    #Create centerline parallel to long side
    mapdl.path("MLINE", 2, 30, 200)
    mapdl.ppath(1, 0, 0, 63.5, 0)
    mapdl.ppath(2, 0, 254, 63.5, 0)
    mapdl.pdef("Z_DEF", "U", "Z")

    #Parse deformation results and output cleaner results without MAPDL disclaimer
    output = mapdl.prpath("Z_DEF")
    uz_values = []

    for line in output.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('-') or line.startswith('*') or '****' in line or 'DO NOT' in line:
            continue
        if line[0].isalpha() or 'PATH' in line or 'VARIABLE' in line or 'SUMMARY' in line:
            continue
        try:
            parts = line.split()
            if len(parts) == 2:
                s_val = float(parts[0]) / 1000
                z_val = float(parts[1]) / 1000
                uz_values.append((s_val, z_val))
        except ValueError:
            continue

    #Write deformation results to output file
    output_path = output_file
    with open(output_path, "w") as output_text:
        output_text.write("Deformation results for spatially-varying sinusoidal pressure load centerline\n")
        output_text.write(f"{'Index':<5} {'S Position (m)':<20} {'Z Deflection (m)':<20}\n")
        for j, (s, uz) in enumerate(uz_values, start=1):
            output_text.write(f"{j:<5} {s:<20.4e} {uz:<20.6e}\n")

    print(f"Done, results written to {output_path}")
    mapdl.exit()

except Exception as e:
    print(f"Launch failed. Error: {e}")
    mapdl.exit()
