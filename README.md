# Spatially-Varying Pressure Load Solver: PyMAPDL
Python/ANSYS structural solvers for applying static and spatially-varying pressure loads to a compliant panel, developed as part of ongoing fluid-structure interaction (FSI) research at the UCF Data-informed Multiphysics Laboratory (DiMSL).

## Overview
This repository implements and validates a custom PyMAPDL solver capable of applying arbitrary, non-uniform pressure fields P(x, y) to a structural mesh — as opposed to standard uniform-pressure loading. The spatially-varying solver maps pressure data to mesh element centroids via custom interpolation, enabling more realistic simulation of non-uniform aeroelastic-style load cases.

This code supports model verification for a broader reduced-order modeling (ROM) research effort within the lab; the ROM itself is not included in this repository.

## Model details:
- Geometry: 254 mm × 127 mm clamped panel
- Material: AISI 4140 steel
- Element type: SHELL181
- Load cases: uniform-pressure baseline vs. spatially-varying pressure field

## Repository Structure
- PyANSYS_static_solver.py                  PyMAPDL solver for uniform pressure loading
- PyANSYS_spatially_varied_solver.py        PyMAPDL solver with custom P(x,y) interpolation
- Pressure_x_y_matrix_creation_sin_wave.m      MATLAB script generating pressure grid data for spatially varied solver
- Pressure Loads.txt                Sample pressures for static solver
- Matplotlib sinusoidal wave deformations graph quarterline vs. centerline.py  Plots/compares deflection results for panel's - centerline path and "quarter"line path
- results/
    - Spatially varied deformation due to sinusodal wave load centerline.txt
    - Spatially varied deformation due to sinusodal wave load quarterline.txt
    
- PyANSYS requirements.txt
- README.md

## Requirements
- Python 3.x
- `ansys-mapdl-core` (PyMAPDL)
- `numpy`, `matplotlib`, `scipy`
- MATLAB (for pressure field generation script)
- Licensed ANSYS Mechanical APDL installation

Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Generate a pressure field using `pressure_field_generation.m` (or use the provided `pressure_input.txt`).
2. Run `static_solver.py` for the uniform-pressure baseline case.
3. Run `spatially_varied_solver.py` to apply the non-uniform pressure field via interpolated centroid mapping.
4. Run `plot_deflection_validation.py`, pointing it at the solver output files, to generate comparison plots.

## Validation
The spatially-varying solver was validated against the uniform-pressure baseline across 49 centerline path points, achieving near-exact deflection agreement and confirming solver correctness for non-uniform load cases. Results were additionally cross-checked against reference ANSYS GUI models across parametric pressure sweeps.

## License
This project is licensed under the MIT License, see the `LICENSE` file for details.

## Acknowledgments
Developed as part of undergraduate research at the UCF Data-informed Multiphysics Laboratory (DiMSL).
