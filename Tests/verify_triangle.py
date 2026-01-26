#!/usr/bin/env python3
"""
Verificacion de funciones de mallado triangular
Para comparar con mathcad_triangle.dll en Mathcad Prime
"""

import numpy as np

def tri_nodes(Lx, Ly, nx, ny):
    """Genera coordenadas de nodos para malla rectangular"""
    num_nodes = (nx + 1) * (ny + 1)
    nodes = np.zeros((num_nodes, 2))

    dx = Lx / nx
    dy = Ly / ny

    idx = 0
    for j in range(ny + 1):
        for i in range(nx + 1):
            nodes[idx, 0] = i * dx  # x
            nodes[idx, 1] = j * dy  # y
            idx += 1

    return nodes

def tri_elements(nx, ny):
    """Genera conectividad de elementos triangulares (base 1)"""
    num_tri = 2 * nx * ny
    elements = np.zeros((num_tri, 3), dtype=int)

    tri_idx = 0
    for j in range(ny):
        for i in range(nx):
            # Nodos del cuadrilatero (base 1)
            n1 = j * (nx + 1) + i + 1
            n2 = j * (nx + 1) + i + 2
            n3 = (j + 1) * (nx + 1) + i + 2
            n4 = (j + 1) * (nx + 1) + i + 1

            # Triangulo 1: n1-n2-n4
            elements[tri_idx, :] = [n1, n2, n4]
            tri_idx += 1

            # Triangulo 2: n2-n3-n4
            elements[tri_idx, :] = [n2, n3, n4]
            tri_idx += 1

    return elements

def tri_area(x1, y1, x2, y2, x3, y3):
    """Calcula el area de un triangulo"""
    return 0.5 * abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))

def tri_quality(x1, y1, x2, y2, x3, y3):
    """Calcula la calidad de un triangulo (1 = equilatero perfecto)"""
    # Longitudes de lados al cuadrado
    a2 = (x2 - x1)**2 + (y2 - y1)**2
    b2 = (x3 - x2)**2 + (y3 - y2)**2
    c2 = (x1 - x3)**2 + (y1 - y3)**2

    # Area
    area = 0.5 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))

    # Calidad: 4*sqrt(3)*A / (a^2 + b^2 + c^2)
    if a2 + b2 + c2 > 0:
        return 4.0 * np.sqrt(3) * abs(area) / (a2 + b2 + c2)
    return 0.0

def tri_centroid(x1, y1, x2, y2, x3, y3):
    """Calcula el centroide de un triangulo"""
    return (x1 + x2 + x3) / 3.0, (y1 + y2 + y3) / 3.0

# ============================================================
# PRUEBAS
# ============================================================

print("=" * 60)
print("  Verificacion de funciones de mallado triangular")
print("  Para comparar con Mathcad Prime")
print("=" * 60)
print()

# Parametros de prueba
Lx, Ly = 6.0, 4.0
nx, ny = 3, 2

print(f"Parametros: Lx={Lx}, Ly={Ly}, nx={nx}, ny={ny}")
print()

# 1. Generar nodos
print("1. TRI_NODES - Coordenadas de nodos")
print("-" * 40)
nodes = tri_nodes(Lx, Ly, nx, ny)
print(f"   Numero de nodos: {len(nodes)}")
print("   Primeros 5 nodos:")
for i in range(min(5, len(nodes))):
    print(f"     Nodo {i+1}: ({nodes[i,0]:.4f}, {nodes[i,1]:.4f})")
print()

# 2. Generar elementos
print("2. TRI_ELEMENTS - Conectividad")
print("-" * 40)
elements = tri_elements(nx, ny)
print(f"   Numero de triangulos: {len(elements)}")
print("   Primeros 6 elementos:")
for i in range(min(6, len(elements))):
    print(f"     Elem {i+1}: [{elements[i,0]}, {elements[i,1]}, {elements[i,2]}]")
print()

# 3. Calcular area de un triangulo
print("3. TRI_AREA - Area de triangulo")
print("-" * 40)
# Triangulo de prueba: (0,0), (2,0), (0,2)
x1, y1 = 0, 0
x2, y2 = 2, 0
x3, y3 = 0, 2
area = tri_area(x1, y1, x2, y2, x3, y3)
print(f"   Triangulo: ({x1},{y1}), ({x2},{y2}), ({x3},{y3})")
print(f"   Area = {area:.6f} (esperado: 2.0)")
print()

# Triangulo equilatero
h = np.sqrt(3) / 2
x1, y1 = 0, 0
x2, y2 = 1, 0
x3, y3 = 0.5, h
area_eq = tri_area(x1, y1, x2, y2, x3, y3)
print(f"   Triangulo equilatero lado 1:")
print(f"   Area = {area_eq:.6f} (esperado: {np.sqrt(3)/4:.6f})")
print()

# 4. Calidad de triangulo
print("4. TRI_QUALITY - Calidad de triangulo")
print("-" * 40)
quality_eq = tri_quality(0, 0, 1, 0, 0.5, h)
print(f"   Triangulo equilatero: quality = {quality_eq:.6f} (esperado: 1.0)")

quality_rect = tri_quality(0, 0, 2, 0, 0, 2)
print(f"   Triangulo rectangulo isoceles: quality = {quality_rect:.6f}")

# Triangulo muy alargado
quality_thin = tri_quality(0, 0, 10, 0, 5, 0.1)
print(f"   Triangulo muy alargado: quality = {quality_thin:.6f}")
print()

# 5. Centroide
print("5. TRI_CENTROID - Centroide de triangulo")
print("-" * 40)
cx, cy = tri_centroid(0, 0, 3, 0, 0, 3)
print(f"   Triangulo (0,0), (3,0), (0,3)")
print(f"   Centroide = ({cx:.6f}, {cy:.6f}) (esperado: 1.0, 1.0)")
print()

# 6. Resumen para Mathcad
print("=" * 60)
print("  VALORES PARA VERIFICAR EN MATHCAD PRIME")
print("=" * 60)
print()
print("Con Lx=6, Ly=4, nx=3, ny=2:")
print(f"  tri_nodes(6,4,3,2) -> matriz {nodes.shape[0]}x2")
print(f"  tri_elements(3,2) -> matriz {elements.shape[0]}x3")
print()
print("Pruebas de area:")
print(f"  tri_area(0,0, 2,0, 0,2) = {tri_area(0,0,2,0,0,2):.6f}")
print(f"  tri_area(0,0, 1,0, 0.5,{h:.6f}) = {area_eq:.6f}")
print()
print("Pruebas de calidad:")
print(f"  tri_quality(0,0, 1,0, 0.5,{h:.6f}) = {quality_eq:.6f}")
print(f"  tri_quality(0,0, 2,0, 0,2) = {quality_rect:.6f}")
print()
print("Pruebas de centroide:")
print(f"  tri_centroid(0,0, 3,0, 0,3) = ({cx:.6f}, {cy:.6f})")
