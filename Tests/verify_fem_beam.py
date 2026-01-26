#!/usr/bin/env python3
"""
Verificacion de matriz de rigidez viga 2D
Ejecutar: python verify_fem_beam.py
"""

import numpy as np

# Parametros (igual que en Mathcad)
E = 210e9       # Pa (210 GPa)
A = 0.01        # m2 (100 cm2)
I = 833.3e-8    # m4 (833.3 cm4)
L = 3.0         # m

print("=== Verificacion Matriz Rigidez Viga 2D ===")
print()
print("Parametros:")
print(f"  E = {E/1e9} GPa")
print(f"  A = {A*1e4} cm2")
print(f"  I = {I*1e8} cm4")
print(f"  L = {L} m")
print()

# Coeficientes de la matriz
EA_L = E * A / L
EI_L3 = E * I / (L**3)
EI_L2 = E * I / (L**2)
EI_L = E * I / L

k11 = EA_L              # EA/L
k22 = 12 * EI_L3        # 12EI/L3
k23 = 6 * EI_L2         # 6EI/L2
k33 = 4 * EI_L          # 4EI/L
k36 = 2 * EI_L          # 2EI/L

print("Coeficientes calculados:")
print(f"  EA/L     = {k11:,.3f}")
print(f"  12EI/L3  = {k22:,.3f}")
print(f"  6EI/L2   = {k23:,.3f}")
print(f"  4EI/L    = {k33:,.3f}")
print(f"  2EI/L    = {k36:,.3f}")
print()

# Matriz completa 6x6
K = np.array([
    [ k11,    0,     0,   -k11,    0,     0   ],
    [   0,  k22,   k23,      0, -k22,   k23   ],
    [   0,  k23,   k33,      0, -k23,   k36   ],
    [-k11,    0,     0,    k11,    0,     0   ],
    [   0, -k22,  -k23,      0,  k22,  -k23   ],
    [   0,  k23,   k36,      0, -k23,   k33   ]
])

print("Matriz de Rigidez K (6x6):")
for i in range(6):
    row = "  ["
    for j in range(6):
        row += f"{K[i,j]:14.2f}"
        if j < 5:
            row += ", "
    row += "]"
    print(row)
print()

# Valores de Mathcad (de la captura de pantalla)
mathcad_K = np.array([
    [ 700000000,          0,         0, -700000000,           0,         0],
    [         0,  777746.667,  1166620,          0,  -777746.667,  1166620],
    [         0,    1166620,   2333240,          0,    -1166620,  1166620],
    [-700000000,          0,         0,  700000000,           0,         0],
    [         0, -777746.667, -1166620,          0,   777746.667, -1166620],
    [         0,    1166620,   1166620,          0,    -1166620,  2333240]
])

print("=== Comparacion con Mathcad ===")
error = np.abs(K - mathcad_K)
max_error = np.max(error)
print(f"Error maximo absoluto: {max_error:.6f}")

# Error relativo
max_rel_error = 0
for i in range(6):
    for j in range(6):
        if mathcad_K[i,j] != 0:
            rel = abs(K[i,j] - mathcad_K[i,j]) / abs(mathcad_K[i,j]) * 100
            if rel > max_rel_error:
                max_rel_error = rel

print(f"Error maximo relativo: {max_rel_error:.6f} %")
print()

# Verificacion de propiedades de la matriz
print("=== Verificacion de Propiedades ===")
print(f"  Simetrica: {np.allclose(K, K.T)}")
print(f"  Determinante: {np.linalg.det(K):.2e} (debe ser ~0 para cuerpo rigido)")

# Eigenvalues
eigenvalues = np.linalg.eigvalsh(K)
print(f"  Eigenvalores: {eigenvalues}")
num_zero = np.sum(np.abs(eigenvalues) < 1e-6)
print(f"  Eigenvalores cero (modos rigidos): {num_zero}")
print()

# Verificacion cantilever
print("=== Verificacion Cantilever ===")
P = 1000  # N
defl_teorica = P * L**3 / (3 * E * I)
rot_teorica = P * L**2 / (2 * E * I)

print(f"  P = {P} N")
print(f"  Deflexion teorica = PL3/(3EI) = {defl_teorica * 1000:.6f} mm")
print(f"  Rotacion teorica  = PL2/(2EI) = {rot_teorica * 1000:.6f} mrad")
print()

# Resolver cantilever con FEM
print("=== Solucion FEM del Cantilever ===")
# Condiciones de borde: u1=v1=theta1=0 (empotrado en nodo 1)
# Cargas: F5 = -P (fuerza vertical en nodo 2)

# Submatriz reducida (eliminar DOFs 0,1,2)
K_red = K[3:6, 3:6]
F_red = np.array([0, -P, 0])  # Fx2=0, Fy2=-P, M2=0

# Resolver
U_red = np.linalg.solve(K_red, F_red)
print(f"  Desplazamiento nodo 2:")
print(f"    u2     = {U_red[0]*1000:.6f} mm")
print(f"    v2     = {U_red[1]*1000:.6f} mm")
print(f"    theta2 = {U_red[2]*1000:.6f} mrad")
print()
print(f"  Comparacion:")
print(f"    v2 FEM    = {U_red[1]*1000:.6f} mm")
print(f"    v2 Teoria = {-defl_teorica*1000:.6f} mm")
print(f"    Error     = {abs(U_red[1] + defl_teorica)/defl_teorica*100:.6f} %")
