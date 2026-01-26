# TEST 2: Matrices (Python)
# ====================================
import numpy as np

# PRUEBA 2A: Crear matriz 3x3
nu = 0.15
D = np.array([
    [1, nu, 0],
    [nu, 1, 0],
    [0, 0, (1-nu)/2]
])
print('PRUEBA 2A: Matriz D:')
print(D)

# PRUEBA 2B: Crear vector
v = np.array([1, 2, 3, 4])
print('\nPRUEBA 2B: Vector v:')
print(v)

# PRUEBA 2C: Acceso a elementos (0-based en Python)
print('\nPRUEBA 2C: Acceso a elementos:')
print(f'D[0,0] = {D[0,0]}')  # Equivalente a D.(1;1) en Calcpad
print(f'D[0,1] = {D[0,1]}')
print(f'D[1,0] = {D[1,0]}')
print(f'D[2,2] = {D[2,2]}')

# PRUEBA 2D: Crear con zeros()
n = 4
w = np.zeros(n)
print('\nPRUEBA 2D: Vector w (zeros):')
print(w)

# PRUEBA 2E: Crear con zeros()
A = np.zeros((3, 2))
print('\nPRUEBA 2E: Matriz A (zeros):')
print(A)

# PRUEBA 2F: Asignar elementos
A[0, 0] = 10  # Equivalente a A.(1;1) = 10 en Calcpad
A[1, 1] = 20
print('\nPRUEBA 2F: Matriz A modificada:')
print(A)
