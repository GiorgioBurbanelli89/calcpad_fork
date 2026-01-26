# TEST 3: Bucles y asignacion de matrices (Python)
# ====================================
import numpy as np

# PRUEBA 3A: Bucle simple
n = 4
v = np.zeros(n)
for i in range(1, n+1):  # 1-based like Calcpad
    v[i-1] = i * 10
print('PRUEBA 3A: Vector v:')
print(v)

# PRUEBA 3B: Bucle anidado
A = np.zeros((3, 3))
for i in range(1, 4):
    for j in range(1, 4):
        A[i-1, j-1] = i + j
print('\nPRUEBA 3B: Matriz A:')
print(A)

# PRUEBA 3C: Equivalente a $Repeat
B = np.zeros((2, 2))
for i in range(1, 3):
    B[i-1, 0] = i
for i in range(1, 3):
    B[i-1, 1] = i * 2
print('\nPRUEBA 3C: Matriz B:')
print(B)
