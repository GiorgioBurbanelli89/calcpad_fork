% TEST 2: Matrices (Octave)
% ====================================

% PRUEBA 2A: Crear matriz 3x3
nu = 0.15;
D = [1, nu, 0; nu, 1, 0; 0, 0, (1-nu)/2];
fprintf('PRUEBA 2A: Matriz D:\n');
disp(D);

% PRUEBA 2B: Crear vector
v = [1; 2; 3; 4];  % Vector columna
fprintf('PRUEBA 2B: Vector v:\n');
disp(v);

% PRUEBA 2C: Acceso a elementos
fprintf('PRUEBA 2C: Acceso a elementos:\n');
fprintf('D(1,1) = %g\n', D(1,1));
fprintf('D(1,2) = %g\n', D(1,2));
fprintf('D(2,1) = %g\n', D(2,1));
fprintf('D(3,3) = %g\n', D(3,3));

% PRUEBA 2D: Crear con zeros()
n = 4;
w = zeros(n, 1);
fprintf('\nPRUEBA 2D: Vector w (zeros):\n');
disp(w);

% PRUEBA 2E: Crear con zeros()
A = zeros(3, 2);
fprintf('PRUEBA 2E: Matriz A (zeros):\n');
disp(A);

% PRUEBA 2F: Asignar elementos
A(1, 1) = 10;
A(2, 2) = 20;
fprintf('PRUEBA 2F: Matriz A modificada:\n');
disp(A);
