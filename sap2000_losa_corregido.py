# -*- coding: utf-8 -*-
"""
Modelo corregido de losa rectangular
====================================
Problema: Las restricciones no se aplicaron a TODOS los nodos del borde.
Solo los nodos en x=0 y x=a tienen reacciones.

Solucion: Aplicar UZ=0 (restriccion vertical) a TODOS los nodos del perimetro.
"""

import comtypes.client
import math
import sys

print("="*70)
print("MODELO CORREGIDO - LOSA RECTANGULAR")
print("="*70)

# Datos del problema
a = 6.0        # dimension en x
b = 4.0        # dimension en y
t = 0.1        # espesor
q = 10.0       # carga kN/m2
E = 35000000   # kN/m2 (35000 MPa)
nu = 0.15      # Poisson
n_a = 6        # divisiones en x
n_b = 4        # divisiones en y

print(f"Losa: {a}m x {b}m, t={t}m")
print(f"Carga: {q} kN/m2")
print(f"Material: E={E/1000} MPa, nu={nu}")
print(f"Malla: {n_a}x{n_b} elementos")

# Conectar a SAP2000 - intentar conectar a existente, si no, crear nueva instancia
try:
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")

    if mySapObject is None:
        print("SAP2000 no esta abierto. Iniciando nueva instancia...")
        mySapObject = helper.CreateObject(r"C:\Program Files\Computers and Structures\SAP2000 24\SAP2000.exe")
        mySapObject.ApplicationStart()

    SapModel = mySapObject.SapModel
    print(f"\nSAP2000 {SapModel.GetVersion()[0]}")

except Exception as e:
    print(f"Error conectando a SAP2000: {e}")
    print("Por favor abra SAP2000 manualmente e intente de nuevo.")
    sys.exit(1)

# Nuevo modelo
SapModel.InitializeNewModel(6)  # kN, m, C
SapModel.File.NewBlank()

# Material
mat = "CONCRETO"
SapModel.PropMaterial.SetMaterial(mat, 1)  # 1=Concrete
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)

# Seccion Shell-Thin (Kirchhoff)
shell = "LOSA_10CM"
# SetShell_1(Name, ShellType, IncludeDrillingDOF, MatProp, MatAng, Thickness, BendThick, Coord, Notes, GUID)
# ShellType: 1=Shell-Thin, 2=Shell-Thick
SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")

# Crear nodos
a1 = a / n_a
b1 = b / n_b
nodos = {}
nodo_id = 1

for j in range(n_b + 1):
    for i in range(n_a + 1):
        x = i * a1
        y = j * b1
        nombre = str(nodo_id)
        SapModel.PointObj.AddCartesian(x, y, 0.0, nombre)
        nodos[nombre] = (x, y)
        nodo_id += 1

print(f"Nodos creados: {len(nodos)}")

# Crear elementos
elementos = []
for j in range(n_b):
    for i in range(n_a):
        # Nodos del elemento (CCW desde esquina inferior izquierda)
        n1 = j * (n_a + 1) + i + 1
        n2 = n1 + 1
        n3 = n2 + (n_a + 1)
        n4 = n1 + (n_a + 1)

        pts = [str(n1), str(n2), str(n3), str(n4)]
        nombre = f"E{len(elementos)+1}"
        SapModel.AreaObj.AddByPoint(4, pts, nombre, shell, nombre)
        elementos.append(nombre)

print(f"Elementos creados: {len(elementos)}")

# RESTRICCIONES - TODOS los nodos del borde deben tener UZ=0
print("\n=== APLICANDO RESTRICCIONES ===")
nodos_borde = []
nodos_borde_coords = []

for nombre, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        nodos_borde.append(nombre)
        nodos_borde_coords.append((nombre, x, y))

        # Determinar restricciones
        # Esquina (0,0): fijar UX, UY, UZ para evitar movimiento rigido
        # Esquina (a,0): fijar UY, UZ
        # Esquina (0,b): fijar UX, UZ
        # Resto del borde: solo fijar UZ

        es_origen = abs(x) < 0.001 and abs(y) < 0.001
        es_esq_xa_y0 = abs(x - a) < 0.001 and abs(y) < 0.001
        es_esq_x0_yb = abs(x) < 0.001 and abs(y - b) < 0.001

        if es_origen:
            restr = [True, True, True, False, False, False]  # UX, UY, UZ
        elif es_esq_xa_y0:
            restr = [False, True, True, False, False, False]  # UY, UZ
        elif es_esq_x0_yb:
            restr = [True, False, True, False, False, False]  # UX, UZ
        else:
            restr = [False, False, True, False, False, False]  # Solo UZ

        ret = SapModel.PointObj.SetRestraint(nombre, restr)
        if ret != 0:
            print(f"  ERROR en nodo {nombre}: ret={ret}")

print(f"Nodos de borde restringidos: {len(nodos_borde)}")

# Verificar que las restricciones estan correctas
print("\nVerificacion de restricciones (muestra):")
for nombre, x, y in nodos_borde_coords[:4]:
    ret = SapModel.PointObj.GetRestraint(nombre)
    print(f"  Nodo {nombre} ({x:.1f},{y:.1f}): {list(ret[0])}")

# Cargas
print("\n=== APLICANDO CARGAS ===")
for elem in elementos:
    # SetLoadUniform(Name, LoadPat, Value, Dir, Replace, CSys, ItemType)
    # Dir: 6 = Local 3 (perpendicular al elemento, hacia abajo)
    SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)

print(f"Carga aplicada: {q} kN/m2 en {len(elementos)} elementos")
print(f"Carga total: {q * a * b} kN")

# Guardar
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_LosaCorregida.sdb"
SapModel.File.Save(ModelPath)
print(f"\nModelo guardado: {ModelPath}")

# Analizar
print("\n=== ANALIZANDO ===")
SapModel.Analyze.SetRunCaseFlag("", False, True)  # Desactivar todos
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)  # Activar DEAD
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Guardar despues del analisis
SapModel.File.Save(ModelPath)

# Verificar que el modelo esta bloqueado
print(f"Modelo bloqueado: {SapModel.GetModelIsLocked()}")

# RESULTADOS
print("\n=== RESULTADOS ===")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Desplazamientos
U3_dict = {}
for nombre in nodos:
    ret = SapModel.Results.JointDispl(nombre, 0)
    if ret[0] > 0:
        U3_dict[nombre] = ret[9][0]

print(f"Nodos con desplazamiento: {len(U3_dict)}")

# Matriz de desplazamientos
xs = sorted(set(x for x, y in nodos.values()))
ys = sorted(set(y for x, y in nodos.values()), reverse=True)

print(f"\nMatriz UZ (mm):")
print(f"{'y\\x':<6}", end="")
for x in xs:
    print(f"{x:>8.1f}", end="")
print()

for y in ys:
    print(f"{y:<6.1f}", end="")
    for x in xs:
        for nombre, (nx, ny) in nodos.items():
            if abs(nx - x) < 0.001 and abs(ny - y) < 0.001:
                uz = U3_dict.get(nombre, 0) * 1000
                print(f"{uz:>8.3f}", end="")
                break
    print()

# Estadisticas
print(f"\nUZ min: {min(U3_dict.values())*1000:.4f} mm")
print(f"UZ max: {max(U3_dict.values())*1000:.4f} mm")

# Nodo central
w_sap = 0
for nombre, (x, y) in nodos.items():
    if abs(x - a/2) < 0.1 and abs(y - b/2) < 0.1:
        print(f"UZ centro (nodo {nombre}): {U3_dict.get(nombre, 0)*1000:.4f} mm")
        w_sap = abs(U3_dict.get(nombre, 0))
        break

# Reacciones
print("\n=== REACCIONES ===")
total_F3 = 0
n_reac = 0

for nombre in nodos_borde:
    ret = SapModel.Results.JointReact(nombre, 0)
    if ret[0] > 0:
        F3 = ret[8][0]
        total_F3 += F3
        n_reac += 1

print(f"Numero de reacciones: {n_reac}")
print(f"Suma F3: {total_F3:.4f} kN")
print(f"Carga esperada: {-q*a*b:.4f} kN")
print(f"Diferencia: {abs(total_F3 + q*a*b):.4f} kN ({abs(total_F3 + q*a*b)/(q*a*b)*100:.2f}%)")

# Solucion analitica (Navier)
print("\n=== COMPARACION CON SOLUCION ANALITICA ===")
D = E * t**3 / (12 * (1 - nu**2))
print(f"D = {D:.2f} kNm")

def navier_w(x, y, a, b, q, D, n=100):
    w = 0.0
    for m in range(1, n, 2):
        for nn in range(1, n, 2):
            coef = 16.0 * q / (math.pi**6 * m * nn)
            denom = D * (m**2/a**2 + nn**2/b**2)**2
            w += coef / denom * math.sin(m*math.pi*x/a) * math.sin(nn*math.pi*y/b)
    return w

w_navier = navier_w(a/2, b/2, a, b, q, D)
print(f"w_centro (Navier, 100 terminos): {w_navier*1000:.4f} mm")
print(f"w_centro (SAP2000): {w_sap*1000:.4f} mm")

if w_navier != 0:
    error = abs(w_sap - w_navier) / w_navier * 100
    print(f"Error: {error:.2f}%")

print("\n" + "="*70)
