% TEST 3: Bucles y asignacion de matrices (Octave)
% ====================================

% PRUEBA 3A: Bucle simple
n = 4;
v = zeros(n, 1);
for i = 1:n
    v(i) = i * 10;
end
fprintf('PRUEBA 3A: Vector v:\n');
disp(v);

% PRUEBA 3B: Bucle anidado
A = zeros(3, 3);
for i = 1:3
    for j = 1:3
        A(i, j) = i + j;
    end
end
fprintf('PRUEBA 3B: Matriz A:\n');
disp(A);

% PRUEBA 3C: Equivalente a $Repeat
B = zeros(2, 2);
for i = 1:2
    B(i, 1) = i;
end
for i = 1:2
    B(i, 2) = i * 2;
end
fprintf('PRUEBA 3C: Matriz B:\n');
disp(B);
