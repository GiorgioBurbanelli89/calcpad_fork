#!/usr/bin/env python3
"""
plate_fem_example.py - Ejemplo de placa FEM simplificado
Basado en Awatif-FEM (elementos shell triangulares)

Ejecutar: python plate_fem_example.py
"""

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve

# ============================================================
# GENERACION DE MALLA
# ============================================================
def generate_rectangular_mesh(Lx, Ly, nx, ny):
    """Genera malla triangular para rectangulo"""
    nodes = []
    elements = []

    dx = Lx / nx
    dy = Ly / ny

    # Generar nodos
    for j in range(ny + 1):
        for i in range(nx + 1):
            nodes.append([i * dx, j * dy, 0])

    # Generar elementos triangulares
    for j in range(ny):
        for i in range(nx):
            n1 = j * (nx + 1) + i
            n2 = j * (nx + 1) + i + 1
            n3 = (j + 1) * (nx + 1) + i + 1
            n4 = (j + 1) * (nx + 1) + i

            # Triangulo 1: n1-n2-n4
            elements.append([n1, n2, n4])
            # Triangulo 2: n2-n3-n4
            elements.append([n2, n3, n4])

    return np.array(nodes), np.array(elements)

# ============================================================
# MATRIZ DE RIGIDEZ DE PLACA (MINDLIN-REISSNER SIMPLIFICADO)
# ============================================================
def triangle_area(n1, n2, n3):
    """Calcula area de triangulo"""
    x21 = n2[0] - n1[0]
    y21 = n2[1] - n1[1]
    x31 = n3[0] - n1[0]
    y31 = n3[1] - n1[1]
    return 0.5 * abs(x21 * y31 - x31 * y21)

def get_bending_stiffness_matrix(n1, n2, n3, E, nu, t):
    """Matriz de rigidez de flexion para triangulo (3 DOF por nodo: w, theta_x, theta_y)"""
    A = triangle_area(n1, n2, n3)
    if A < 1e-12:
        return np.zeros((9, 9))

    # Matriz constitutiva de flexion D_b
    D = E * t**3 / (12.0 * (1.0 - nu**2))
    Db = D * np.array([
        [1,   nu,  0],
        [nu,  1,   0],
        [0,   0,   (1-nu)/2]
    ])

    # Coordenadas
    x1, y1 = n1[0], n1[1]
    x2, y2 = n2[0], n2[1]
    x3, y3 = n3[0], n3[1]

    # Derivadas de funciones de forma
    b1 = y2 - y3
    b2 = y3 - y1
    b3 = y1 - y2
    c1 = x3 - x2
    c2 = x1 - x3
    c3 = x2 - x1

    # Matriz B de deformacion-curvatura
    Bb = np.zeros((3, 9))
    inv2A = 1.0 / (2.0 * A)

    # dNi/dx para theta_y (curvatura kappa_x)
    Bb[0, 2] = b1 * inv2A
    Bb[0, 5] = b2 * inv2A
    Bb[0, 8] = b3 * inv2A

    # dNi/dy para -theta_x (curvatura kappa_y)
    Bb[1, 1] = -c1 * inv2A
    Bb[1, 4] = -c2 * inv2A
    Bb[1, 7] = -c3 * inv2A

    # Curvatura de torsion
    Bb[2, 1] = -b1 * inv2A
    Bb[2, 2] = c1 * inv2A
    Bb[2, 4] = -b2 * inv2A
    Bb[2, 5] = c2 * inv2A
    Bb[2, 7] = -b3 * inv2A
    Bb[2, 8] = c3 * inv2A

    return Bb.T @ Db @ Bb * A

def get_shear_stiffness_matrix(n1, n2, n3, E, nu, t):
    """Matriz de rigidez de cortante para triangulo"""
    A = triangle_area(n1, n2, n3)
    if A < 1e-12:
        return np.zeros((9, 9))

    # Factor de correccion de cortante
    kappa = 5.0 / 6.0
    G = E / (2.0 * (1.0 + nu))
    Ds_val = kappa * G * t

    Ds = np.array([
        [Ds_val, 0],
        [0, Ds_val]
    ])

    # Coordenadas
    x1, y1 = n1[0], n1[1]
    x2, y2 = n2[0], n2[1]
    x3, y3 = n3[0], n3[1]

    # Funciones de forma en centroide
    N1 = N2 = N3 = 1.0 / 3.0

    # Derivadas de N
    inv2A = 1.0 / (2.0 * A)
    dN1dx = (y2 - y3) * inv2A
    dN2dx = (y3 - y1) * inv2A
    dN3dx = (y1 - y2) * inv2A
    dN1dy = (x3 - x2) * inv2A
    dN2dy = (x1 - x3) * inv2A
    dN3dy = (x2 - x1) * inv2A

    # Matriz Bs (gamma = dw/dx - theta_y, dw/dy + theta_x)
    Bs = np.zeros((2, 9))

    # gamma_xz = dw/dx - theta_y
    Bs[0, 0] = dN1dx;  Bs[0, 2] = -N1
    Bs[0, 3] = dN2dx;  Bs[0, 5] = -N2
    Bs[0, 6] = dN3dx;  Bs[0, 8] = -N3

    # gamma_yz = dw/dy + theta_x
    Bs[1, 0] = dN1dy;  Bs[1, 1] = N1
    Bs[1, 3] = dN2dy;  Bs[1, 4] = N2
    Bs[1, 6] = dN3dy;  Bs[1, 7] = N3

    return Bs.T @ Ds @ Bs * A

def get_local_stiffness_matrix(n1, n2, n3, E, nu, t):
    """Matriz de rigidez local completa del elemento shell"""
    Kb = get_bending_stiffness_matrix(n1, n2, n3, E, nu, t)
    Ks = get_shear_stiffness_matrix(n1, n2, n3, E, nu, t)
    return Kb + Ks

# ============================================================
# ENSAMBLAJE GLOBAL
# ============================================================
def assemble_global_stiffness(nodes, elements, E, nu, t):
    """Ensambla matriz de rigidez global"""
    num_nodes = len(nodes)
    dof = num_nodes * 3  # 3 DOF por nodo (w, theta_x, theta_y)

    K = lil_matrix((dof, dof))

    for elem in elements:
        n1_idx, n2_idx, n3_idx = elem
        n1 = nodes[n1_idx]
        n2 = nodes[n2_idx]
        n3 = nodes[n3_idx]

        Ke = get_local_stiffness_matrix(n1, n2, n3, E, nu, t)

        # Indices de DOF
        dofs = [
            n1_idx * 3,     n1_idx * 3 + 1, n1_idx * 3 + 2,
            n2_idx * 3,     n2_idx * 3 + 1, n2_idx * 3 + 2,
            n3_idx * 3,     n3_idx * 3 + 1, n3_idx * 3 + 2
        ]

        for i in range(9):
            for j in range(9):
                K[dofs[i], dofs[j]] += Ke[i, j]

    return K.tocsr()

# ============================================================
# APLICAR CONDICIONES DE FRONTERA
# ============================================================
def apply_boundary_conditions(K, F, fixed_dofs):
    """Aplica condiciones de frontera por metodo de penalizacion"""
    K = K.tolil()
    penalty = 1e20

    for dof in fixed_dofs:
        K[dof, dof] += penalty
        F[dof] = 0

    return K.tocsr(), F

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Ejemplo de Placa FEM - Elementos Shell Triangulares")
    print("  (Similar al ejemplo plate de Awatif)")
    print("=" * 60)
    print()

    # Parametros de la placa
    Lx = 6.0   # Longitud en X (m)
    Ly = 4.0   # Longitud en Y (m)
    nx = 3     # Divisiones en X
    ny = 2     # Divisiones en Y

    # Material
    E = 210e9     # Modulo de Young (Pa)
    nu = 0.3      # Coeficiente de Poisson
    t = 0.1       # Espesor (m)

    # Carga distribuida
    q = -1000     # N/m2 (carga uniforme hacia abajo)

    print("Parametros:")
    print(f"  Placa: {Lx} x {Ly} m")
    print(f"  Malla: {nx} x {ny} elementos")
    print(f"  E = {E/1e9} GPa")
    print(f"  nu = {nu}")
    print(f"  t = {t*1000} mm")
    print(f"  q = {q} N/m2")
    print()

    # Generar malla
    nodes, elements = generate_rectangular_mesh(Lx, Ly, nx, ny)

    print("Malla generada:")
    print(f"  Nodos: {len(nodes)}")
    print(f"  Elementos: {len(elements)}")
    print()

    # Ensamblar matriz de rigidez global
    num_nodes = len(nodes)
    dof = num_nodes * 3

    K = assemble_global_stiffness(nodes, elements, E, nu, t)

    # Vector de fuerzas (carga distribuida convertida a nodal)
    F = np.zeros(dof)
    area_per_node = (Lx * Ly) / num_nodes
    for i in range(num_nodes):
        F[i * 3] = q * area_per_node  # Fuerza en w

    # Condiciones de frontera: bordes empotrados
    fixed_dofs = []
    for i, node in enumerate(nodes):
        x, y = node[0], node[1]

        # Nodos en los bordes
        if abs(x) < 1e-6 or abs(x - Lx) < 1e-6 or abs(y) < 1e-6 or abs(y - Ly) < 1e-6:
            fixed_dofs.append(i * 3)      # w = 0
            fixed_dofs.append(i * 3 + 1)  # theta_x = 0
            fixed_dofs.append(i * 3 + 2)  # theta_y = 0

    print("Condiciones de frontera:")
    print(f"  Nodos fijos en bordes: {len(fixed_dofs) // 3}")
    print()

    # Aplicar condiciones de frontera
    K, F = apply_boundary_conditions(K, F, fixed_dofs)

    # Resolver sistema
    U = spsolve(K, F)

    # Resultados
    print("=" * 60)
    print("  RESULTADOS")
    print("=" * 60)
    print()

    # Encontrar desplazamiento maximo
    w_values = U[::3]  # Solo desplazamientos w
    w_max = np.min(w_values)  # Maximo (negativo porque carga hacia abajo)
    node_max = np.argmin(w_values)

    print("Desplazamiento maximo (w):")
    print(f"  Nodo {node_max} en ({nodes[node_max][0]:.1f}, {nodes[node_max][1]:.1f})")
    print(f"  w_max = {w_max * 1000:.6f} mm")
    print()

    # Solucion analitica para placa rectangular empotrada (aproximacion)
    D = E * t**3 / (12.0 * (1.0 - nu**2))
    a = min(Lx, Ly)
    w_analytical = 0.00126 * abs(q) * a**4 / D

    print("Comparacion con solucion analitica (placa empotrada):")
    print(f"  w_analitico = {w_analytical * 1000:.6f} mm")
    print(f"  Error: {abs(abs(w_max) - w_analytical) / w_analytical * 100:.2f} %")
    print()

    # Mostrar algunos desplazamientos
    print("Desplazamientos en nodos centrales:")
    print(f"{'Nodo':>6} {'x':>10} {'y':>10} {'w (mm)':>15} {'theta_x':>15} {'theta_y':>15}")

    for i, node in enumerate(nodes):
        x, y = node[0], node[1]

        # Solo nodos interiores
        if x > 0.5 and x < Lx - 0.5 and y > 0.5 and y < Ly - 0.5:
            print(f"{i:6d} {x:10.1f} {y:10.1f} {U[i*3]*1000:15.6f} {U[i*3+1]:15.6f} {U[i*3+2]:15.6f}")
