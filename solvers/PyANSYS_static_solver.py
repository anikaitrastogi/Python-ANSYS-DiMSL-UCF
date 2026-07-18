#Material number
AISI_4140 = 1


#Read in pressure values__________________________________________________________________________________________
with open (r"C:\DiMSL\Pressure loads for PyANSYS\Pressure Loads.txt", "r")as input:
    pressure_values = input.read()

pressure_list = pressure_values.splitlines()
pressure_list_length = len(pressure_list)

#Mechanical Ansys Parametric Design Language (MAPDL)________________________________________________________________
#Import MAPDL Library
import ansys.mapdl.core as pymapdl


#Safety-net if ANSYS MAPDL launch fails
try:
    print("Launching MAPDL")
    mapdl = pymapdl.launch_mapdl() 
    
    print("MAPDL running")

#Pre-processing______________________________________________________________________________________________________
    # Build panel
    mapdl.prep7() #Pre-processing command
    mapdl.rectng(0, 254, 0, 127,) #Create 2D panel first according to specifications
    
    #Specify material properties:

    #Linear Elastic properties:
    mapdl.mp("EX", AISI_4140, 200000) #Avg Young's Modulus
    mapdl.mp("PRXY", AISI_4140, 0.285) #Avg Poisson's ratio
    mapdl.mp("DENS", AISI_4140, 7.85e-9) #Density in tonnes/mm^3

    #Strength and Thermal properties
    mapdl.tb("FAIL", AISI_4140)
    mapdl.tbdata(AISI_4140, 415, 655) #(Material number, yield strength, tensile strength)
    mapdl.mp("REFT", AISI_4140, 1416) #Melting point in C

    #Specify shells and thickness
    mapdl.et(AISI_4140, "SHELL181") #Shell 181 is a general shell type used for simple applications, such as panels
    mapdl.sectype(AISI_4140, "SHELL") #Create a shell section for the material
    mapdl.secdata(0.635) #Specify what thickness goes into the shell section

    #Specify s3 meshing
    mapdl.mshape(1, "2D") #1 specifies triangular elements
    mapdl.mshkey(0) #Free mesh, allows for ANSYS to determine mesh structure
    mapdl.esize(2.5) #Element sizing required for 10,000 elements, in mm

    #Specify active mesh material and element type
    mapdl.mat(AISI_4140) #Material
    mapdl.type(1) #Element type (SHELL=181)

    #Apply mesh
    mapdl.amesh("ALL")


#Solution______________________________________________________________________________________________

    for i in range(pressure_list_length):
        mapdl.run("/SOLU")
        mapdl.antype(0) #Set to static node
        mapdl.nlgeom(0)
        mapdl.nsubst(10,100,5)


        #Clamp boundaries
        #Select edges to clamp
        mapdl.lsel("S", "LOC", "X", 0) #Edges along X, S is to select a new set
        mapdl.lsel("A","LOC", "X", 254) #A is to add to the previous set
        mapdl.lsel("A","LOC", "Y", 0)#Edges along Y
        mapdl.lsel("A","LOC", "Y", 127)
        mapdl.nsll("S")

        #Fix displacement of edges to 0
        mapdl.d("ALL", "UX", 0)
        mapdl.d("ALL", "UY", 0)
        mapdl.d("ALL", "UZ", 0)
        mapdl.d("ALL", "ROTX", 0)
        mapdl.d("ALL", "ROTY", 0)
        mapdl.d("ALL", "ROTZ", 0)
        mapdl.allsel() #Ensures that pressure is applied to entire panel, not just one line/edge
        
        #Apply test pressure
        mapdl.sfa("ALL", 1, "PRES", -float(pressure_list[i])/10e5)

        #Solve and exit solution module
        mapdl.solve()
        mapdl.finish()

    #Post-processing________________________________________________________________________________________________________________
        mapdl.post1()

        #Create centerline parallel to long side
        mapdl.path("MLINE", 2, 30, 48) #Define a line with 2 points and 49 intervals
        mapdl.ppath(1, 0, 0, 63.5, 0) #Define location of first point
        mapdl.ppath(2, 0, 254, 63.5, 0) #Define location of second point
        mapdl.pdef("Z_DEF", "U", "Z")


    #Formatting and printing results________________________________________________________________________________________________
        output = mapdl.prpath("Z_DEF")
        
        # Parse output line by line, extract only numeric data
        uz_values = []
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that are all dashes or contain disclaimers
            if line.startswith('-') or line.startswith('*') or '****' in line or 'DO NOT' in line:
                continue
            
            # Skip header lines (contain letters at the start or are full words)
            if line[0].isalpha() or 'PATH' in line or 'VARIABLE' in line or 'SUMMARY' in line:
                continue
            
            # Try to parse as two numbers
            try:
                parts = line.split()
                if len(parts) == 2:
                    s_val = float(parts[0]) /1000
                    z_val = float(parts[1]) /1000
                    uz_values.append((s_val, z_val))
            except ValueError:
                continue
        
        # File output
        with open (r"C:\DiMSL\Deformation Results\Static deformations\Static pressure deformation due to "+str(float(pressure_list[i]))+" load.txt","w") as output_text:
            output_text.write("Deformation due to " + str(float(pressure_list[i])) + " Pa \n")
            output_text.write("Index    S Position (m)      Z Position \n")
            for j, (s, uz) in enumerate(uz_values, start =1):
                output_text.write(f"{j:<5} {s:<20.4e} {uz:<20.6e}\n")
    mapdl.exit()
    print("Done, check output files")



except Exception as e:
    print(f"Launch failed. Error: {e}")
    mapdl.exit()
