%% Specify Panel dimensions in mm
x_min = 0;
y_min = 0;
x_max = 254;
y_max = 127;
element_size = 2.5;
L=x_max;
W=y_max;

%% Create coords vectors using linspace
x_coords = linspace(x_min + element_size/2, x_max - element_size/2, round((x_max-x_min)/element_size));
y_coords = linspace(y_min + element_size/2, y_max - element_size/2, round((y_max-y_min)/element_size));

%% Put coords into matrix
[x_grid, y_grid] = meshgrid(x_coords, y_coords);

%% Create Pressure matrix with the same size as x_grid and calculated sin wave
p_grid = 10000*sin(2*pi*x_grid / L).*sin(2*pi*y_grid/W);

%% Reshape matrix into 1D to input into PyANSYS
x_col = reshape(x_grid, [], 1);
y_col = reshape(y_grid, [], 1);
p_col = reshape(p_grid, [], 1);

%% Create final matrix and write as txt
pressure_matrix = [x_col, y_col, p_col];
writematrix(pressure_matrix, 'C:\DiMSL\Pressure loads for PyANSYS\pressure_load_spatially_varied.txt');