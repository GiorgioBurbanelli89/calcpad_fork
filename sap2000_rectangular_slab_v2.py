# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - COMPARACION CALCPAD VS SAP2000 (v2)
======================================================
Replica el ejemplo "Rectangular Slab FEA.cpd" en SAP2000
con verificacion de cargas y resultados.
"""

import comtypes.client
import numpy as np
np.set_printoptions(precision=4, suppress=True, linewidth=150)

print("="*70)
print("LOSA RECTANGULAR - CALCPAD vs SAP2000")
print("="*70)

# Datos del problema
a = 6.0       # dimension en X (m)
b = 4.0       # dimension en Y (m)
t = 0.1       # espesor (m)
q = 10.0      # carga (kN/m2)
E = 35000e3   # E en kPa (35000 MPa)
nu = 0.15

# Malla
n_a = 6
n_b = 4
a_1 = a / n_a
b_1 = b / n_b

print("\n--- DATOS ---")
print(f"Losa: {a}m x {b}m, t={t}m")
print(f"Carga: q={q} kN/m2")
print(f"Material: E={E/1000} MPa, nu={nu}")
print(f"Malla: {n_a}x{n_b} elementos")

# Conectar a SAP2000
print("\n--- CONECTANDO ---")
mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Crear modelo
print("\n--- CREANDO MODELO ---")
SapModel.InitializeNewModel(6)  # kN, m, C
SapModel.File.NewBlank()

# Material
mat = "MAT"
G = E / (2 * (1 + nu))
SapModel.PropMaterial.SetMaterial(mat, 1)  # 1 = Isotropic
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0, G)
print(f"Material creado")

# Seccion shell - usar Shell-Thin para placa (Kirchhoff)
shell = "SHELL"
# ShellType: 1=Shell-Thin, 2=Shell-Thick, 4=Plate-Thin, 5=Plate-Thick
SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")
print(f"Seccion Shell-Thin creada")

# Crear nodos
print("\n--- CREANDO MALLA ---")
nodo_num = 1
nodos = {}

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * a_1
        y = j * b_1
        nombre = str(nodo_num)
        SapModel.PointObj.AddCartesian(x, y, 0.0, nombre)
        nodos[nodo_num] = (x, y)
        nodo_num += 1

print(f"{len(nodos)} nodos")

# Crear elementos
elem_num = 1
elementos = []

for i in range(n_a):
    for j in range(n_b):
        j1 = j + 1 + (n_b + 1) * i
        j2 = j1 + (n_b + 1)
        j3 = j2 + 1
        j4 = j1 + 1

        pts = [str(j1), str(j2), str(j3), str(j4)]
        nombre = f"E{elem_num}"
        SapModel.AreaObj.AddByPoint(4, pts, nombre, shell, nombre)
        elementos.append(nombre)
        elem_num += 1

print(f"{len(elementos)} elementos")

# Condiciones de borde: apoyo simple en perimetro
print("\n--- CONDICIONES DE BORDE ---")
apoyados = []

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        # Apoyo simple: U3=0, rotaciones libres
        # [U1, U2, U3, R1, R2, R3]
        SapModel.PointObj.SetRestraint(str(nodo), [True, True, True, False, False, True], 0)
        apoyados.append(nodo)
    else:
        # Interior: solo membrana restringida
        SapModel.PointObj.SetRestraint(str(nodo), [True, True, False, False, False, True], 0)

print(f"{len(apoyados)} nodos apoyados")

# Aplicar carga - METODO DIFERENTE: usar SetLoadUniformToFrame
print("\n--- APLICANDO CARGA ---")

# Primero verificar que el patron DEAD existe
ret = SapModel.LoadPatterns.GetNameList()
patrones = list(ret[1]) if ret[0] > 0 else []
print(f"Patrones existentes: {patrones}")

if "DEAD" not in patrones:
    SapModel.LoadPatterns.Add("DEAD", 1)
    print("Patron DEAD creado")

# Aplicar carga uniforme a cada elemento
for elem in elementos:
    # SetLoadUniform(Name, LoadPat, Value, Dir, Replace, CSys, ItemType)
    # Dir: 3 = local Z (perpendicular a la placa), 6 = Gravity
    ret = SapModel.AreaObj.SetLoadUniform(elem, "DEAD", -q, 3, True, "Local", 0)

print(f"Carga q={q} kN/m2 aplicada (dir local Z negativa)")

# Verificar cargas aplicadas
print("\nVerificando cargas en elementos:")
for elem in elementos[:3]:  # solo primeros 3
    ret = SapModel.AreaObj.GetLoadUniform(elem)
    if ret[0] > 0:
        print(f"  {elem}: patron={ret[1]}, valor={ret[3]}, dir={ret[4]}")

# Ejecutar analisis
print("\n--- EJECUTANDO ANALISIS ---")

# Asegurar que DEAD se ejecute
SapModel.Analyze.SetRunCaseFlag("", False, True)  # desactivar todos
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)  # activar DEAD

ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Verificar si modelo esta bloqueado (analizado)
locked = SapModel.GetModelIsLocked()
print(f"Modelo analizado: {locked}")

# Extraer resultados
print("\n--- RESULTADOS ---")

SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Desplazamientos
ret = SapModel.Results.JointDispl("", 2)
print(f"JointDispl: {ret[0]} resultados")

if ret[0] > 0:
    nombres = list(ret[2])
    U3 = list(ret[9])
    R1 = list(ret[10])
    R2 = list(ret[11])

    # Encontrar desplazamiento maximo
    max_idx = np.argmin(U3)  # minimo porque es negativo
    print(f"\nDesplazamiento maximo:")
    print(f"  Nodo {nombres[max_idx]}: U3 = {U3[max_idx]*1000:.4f} mm")

    # Centro de la losa (nodo cerca de x=3, y=2)
    nodo_centro = None
    for nodo, (x, y) in nodos.items():
        if abs(x - 3) < 0.1 and abs(y - 2) < 0.1:
            nodo_centro = nodo
            break

    if nodo_centro and str(nodo_centro) in nombres:
        idx = nombres.index(str(nodo_centro))
        print(f"  Centro ({nodos[nodo_centro]}): U3 = {U3[idx]*1000:.4f} mm")

    # Momentos flectores
    print("\nMomentos flectores:")

    M11_all = []
    M22_all = []

    for elem in elementos:
        ret = SapModel.Results.AreaForceShell(elem, 0)
        if ret[0] > 0:
            M11_all.extend(list(ret[14]))
            M22_all.extend(list(ret[15]))

    if M11_all:
        print(f"  M11: min={min(M11_all):.4f}, max={max(M11_all):.4f} kNm/m")
    if M22_all:
        print(f"  M22: min={min(M22_all):.4f}, max={max(M22_all):.4f} kNm/m")

else:
    print("No hay resultados")

    # Intentar ver si hay errores
    print("\nVerificando posibles problemas...")

    # Ver DOF activos
    ret = SapModel.Analyze.GetActiveDOF()
    print(f"DOF activos: {list(ret[0])}")

# Comparacion
print("\n" + "="*70)
print("COMPARACION CON CALCPAD")
print("="*70)

print("""
VALORES DE REFERENCIA (solucion analitica para losa simplemente apoyada):

Para losa rectangular a=6m, b=4m, t=0.1m, q=10 kN/m2:
- Desplazamiento centro (Navier): w_max aprox 3-4 mm
- Momento Mx centro: aprox 7-8 kNm/m
- Momento My centro: aprox 5-6 kNm/m

Calcpad (16 DOF Kirchhoff): resultados similares
SAP2000 (Shell element): resultados deben ser comparables
""")

# Guardar
print("\n--- GUARDANDO ---")
ruta = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Rectangular_Slab_v2.sdb"
SapModel.File.Save(ruta)
print(f"Modelo: {ruta}")

print("\n" + "="*70)
