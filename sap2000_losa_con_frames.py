# -*- coding: utf-8 -*-
"""
Modelo de losa con elementos Frame como apoyos
==============================================
Workaround para el bug del API de SAP2000 donde SetRestraint
no funciona correctamente con elementos de area.

Solucion: Agregar elementos Frame verticales muy cortos en cada nodo
del borde, con el extremo inferior empotrado.
"""

import comtypes.client
import math
import time

print("="*70)
print("LOSA RECTANGULAR - APOYOS CON FRAMES")
print("="*70)

# Datos
a = 6.0
b = 4.0
t = 0.1
q = 10.0
E = 35000000  # kN/m2
nu = 0.15
n_a = 6
n_b = 4

print(f"Losa: {a}m x {b}m, t={t}m")
print(f"Carga: {q} kN/m2")
print(f"Material: E={E/1000} MPa, nu={nu}")
print(f"Malla: {n_a}x{n_b}")

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"\nSAP2000 {SapModel.GetVersion()[0]}")

# Nuevo modelo
SapModel.InitializeNewModel(6)
SapModel.File.NewBlank()

# Material
mat = "CONCRETO"
SapModel.PropMaterial.SetMaterial(mat, 1)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Seccion Shell - Plate-Thin (Kirchhoff)
shell = "LOSA"
SapModel.PropArea.SetShell_1(shell, 3, False, mat, 0.0, t, t, 0, "", "")

# Seccion Frame para apoyos (muy rigida, muy corta)
frame_apoyo = "APOYO"
# Seccion rectangular muy pequena pero rigida
SapModel.PropFrame.SetRectangle(frame_apoyo, mat, 0.01, 0.01)

# Crear nodos de la losa (z=0)
print("\n=== CREANDO MODELO ===")
a1 = a / n_a
b1 = b / n_b
nodos_losa = {}
nodo_id = 1

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * a1
        y = j * b1
        name = str(nodo_id)
        SapModel.PointObj.AddCartesian(x, y, 0.0, name)
        nodos_losa[nodo_id] = (x, y)
        nodo_id += 1

print(f"Nodos losa: {len(nodos_losa)}")

# Crear elementos de losa
elementos_losa = []
for i in range(n_a):
    for j in range(n_b):
        n1 = j + 1 + (n_b + 1) * i
        n2 = n1 + (n_b + 1)
        n3 = n2 + 1
        n4 = n1 + 1
        pts = [str(n1), str(n2), str(n3), str(n4)]
        name = f"L{len(elementos_losa)+1}"
        SapModel.AreaObj.AddByPoint(4, pts, name, shell, name)
        elementos_losa.append(name)

print(f"Elementos losa: {len(elementos_losa)}")

# Crear apoyos (nodos inferiores + frames)
print("\n=== CREANDO APOYOS ===")
L_apoyo = 0.001  # Longitud del frame de apoyo (muy corto, 1mm)
nodos_apoyo = {}  # Nodos inferiores
frames_apoyo = []
nodos_borde = []

for nodo, (x, y) in nodos_losa.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        nodos_borde.append(nodo)

        # Crear nodo inferior
        nodo_inf = nodo_id
        SapModel.PointObj.AddCartesian(x, y, -L_apoyo, str(nodo_inf))
        nodos_apoyo[nodo_inf] = (x, y, -L_apoyo)
        nodo_id += 1

        # Crear frame entre nodo inferior y nodo de la losa
        frame_name = f"A{len(frames_apoyo)+1}"
        SapModel.FrameObj.AddByPoint(str(nodo_inf), str(nodo), frame_name, frame_apoyo, frame_name)
        frames_apoyo.append(frame_name)

        # Aplicar restricciones al nodo inferior
        # - Para apoyo simple: solo restringir UZ (y UX/UY en esquinas)
        esquina_00 = abs(x) < 0.001 and abs(y) < 0.001
        esquina_a0 = abs(x - a) < 0.001 and abs(y) < 0.001
        esquina_0b = abs(x) < 0.001 and abs(y - b) < 0.001

        if esquina_00:
            restr = [True, True, True, True, True, True]  # Empotrado
        elif esquina_a0:
            restr = [False, True, True, True, True, True]
        elif esquina_0b:
            restr = [True, False, True, True, True, True]
        else:
            restr = [False, False, True, True, True, True]  # Apoyo con rotacion libre

        SapModel.PointObj.SetRestraint(str(nodo_inf), restr)

print(f"Nodos apoyo: {len(nodos_apoyo)}")
print(f"Frames apoyo: {len(frames_apoyo)}")

# Cargas
print("\n=== APLICANDO CARGAS ===")
for elem in elementos_losa:
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)

print(f"Carga: {q} kN/m2")

# Guardar
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_LosaConFrames.sdb"
SapModel.File.Save(ModelPath)
print(f"\nGuardado: {ModelPath}")

# Analizar
print("\n=== ANALIZANDO ===")
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")
print(f"Bloqueado: {SapModel.GetModelIsLocked()}")

# Resultados
print("\n=== RESULTADOS ===")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

U3_dict = {}
for nodo in nodos_losa:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

# Matriz
print(f"\nMatriz UZ (mm):")
print(f"{'y\\x':<6}", end="")
for i in range(n_a + 1):
    print(f"{i*a1:>8.1f}", end="")
print()

for j in range(n_b, -1, -1):
    y = j * b1
    print(f"{y:<6.1f}", end="")
    for i in range(n_a + 1):
        x = i * a1
        for nodo, (nx, ny) in nodos_losa.items():
            if abs(nx - x) < 0.001 and abs(ny - y) < 0.001:
                uz = U3_dict.get(nodo, 0) * 1000
                print(f"{uz:>8.3f}", end="")
                break
    print()

# Estadisticas
if U3_dict:
    print(f"\nUZ min: {min(U3_dict.values())*1000:.4f} mm")
    print(f"UZ max: {max(U3_dict.values())*1000:.4f} mm")

# Centro
w_sap = 0
for nodo, (x, y) in nodos_losa.items():
    if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
        w_sap = abs(U3_dict.get(nodo, 0))
        print(f"\nCentro ({nodo}): UZ = {-U3_dict.get(nodo, 0)*1000:.4f} mm")
        break

# Reacciones en nodos de apoyo
print("\n=== REACCIONES ===")
total_F3 = 0
n_reac = 0

for nodo_inf in nodos_apoyo:
    ret = SapModel.Results.JointReact(str(nodo_inf), 0)
    if ret[0] > 0:
        F3 = ret[8][0]
        total_F3 += F3
        n_reac += 1

print(f"Reacciones: {n_reac}")
print(f"Suma F3: {total_F3:.4f} kN")
print(f"Carga total: {-q*a*b:.4f} kN")
diferencia = abs(total_F3 + q*a*b)
print(f"Diferencia: {diferencia:.4f} kN ({diferencia/(q*a*b)*100:.2f}%)")

# Solucion de Navier
print("\n=== COMPARACION CON NAVIER ===")
D = E * t**3 / (12 * (1 - nu**2))

def navier_w(x, y, a, b, q, D, n=100):
    w = 0.0
    for m in range(1, n, 2):
        for nn in range(1, n, 2):
            coef = 16.0 * q / (math.pi**6 * m * nn)
            denom = D * (m**2/a**2 + nn**2/b**2)**2
            w += coef / denom * math.sin(m*math.pi*x/a) * math.sin(nn*math.pi*y/b)
    return w

w_navier = navier_w(a/2, b/2, a, b, q, D)
print(f"D = {D:.2f} kNm")
print(f"w_centro (Navier): {w_navier*1000:.4f} mm")
print(f"w_centro (SAP2000): {w_sap*1000:.4f} mm")

if w_navier != 0 and w_sap != 0:
    error = abs(w_sap - w_navier) / w_navier * 100
    print(f"Error: {error:.2f}%")

print("\n" + "="*70)
