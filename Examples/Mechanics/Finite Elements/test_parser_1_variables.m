% TEST 1: Variables simples (Octave)
% ====================================

% PRUEBA 1A: Variables simples
a = 6;
b = 4;
t = 0.1;
fprintf('PRUEBA 1A:\n');
fprintf('a = %g\n', a);
fprintf('b = %g\n', b);
fprintf('t = %g\n', t);

% PRUEBA 1B: Variables (sin unidades en Octave)
E = 35000e6;  % Pa
q = 10;       % kN/m2
fprintf('\nPRUEBA 1B:\n');
fprintf('E = %g Pa\n', E);
fprintf('q = %g kN/m2\n', q);

% PRUEBA 1C: Variable n
n = 16;
fprintf('\nPRUEBA 1C:\n');
fprintf('n = %g\n', n);

% PRUEBA 1D: Expresiones
c = a + b;
d = a * b;
e = a / b;
fprintf('\nPRUEBA 1D:\n');
fprintf('c = a + b = %g\n', c);
fprintf('d = a * b = %g\n', d);
fprintf('e = a / b = %g\n', e);
