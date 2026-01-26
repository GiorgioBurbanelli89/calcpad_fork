# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - VERSION DEFINITIVA
=====================================
Verificando cuidadosamente las unidades y coordenadas.
"""

import comtypes.client
import math

print("="*70)
print("LOSA RECTANGULAR - VERSION DEFINITIVA")
print("="*70)

# Datos en unidades SI (kN, m)
a = 6.0       # m
b = 4.0       # m
t = 0.1       # m
q = 10.0      # kN/m2
E = 35000000  # kPa = 35000 MPa * 1000
nu = 0.15

n_a = 6
n_b = 4

print(f"\nDatos:")
print(f"  Losa: {a} x {b} m")
print(f"  Espesor: {t} m")
print(f"  Carga: {q} kN/m2")
print(f"  E = {E} kPa = {E/1000} MPa")
print(f"  nu = {nu}")
print(f"  Malla: {n_a} x {n_b}")

# Conectar
print("\n--- CONECTANDO ---")
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Nuevo modelo - IMPORTANTE: especificar unidades
print("\n--- NUEVO MODELO ---")
ret = SapModel.InitializeNewModel(6)  # 6 = kN, m, C
print(f"InitializeNewModel(kN,m,C): {ret}")

ret = SapModel.File.NewBlank()
print(f"NewBlank: {ret}")

# Verificar unidades
units = SapModel.GetPresentUnits()
unit_names = {1: "lb,in,F", 2: "lb,ft,F", 3: "kip,in,F", 4: "kip,ft,F",
              5: "kN,mm,C", 6: "kN,m,C", 7: "kgf,mm,C", 8: "kgf,m,C",
              9: "N,mm,C", 10: "N,m,C"}
print(f"Unidades actuales: {unit_names.get(units, units)}")

# Si no son kN,m, cambiar
if units != 6:
    ret = SapModel.SetPresentUnits(6)
    print(f"SetPresentUnits(kN,m): {ret}")
    units = SapModel.GetPresentUnits()
    print(f"Unidades verificadas: {unit_names.get(units, units)}")

# Material isotropico
print("\n--- MATERIAL ---")
mat = "MAT"
ret = SapModel.PropMaterial.SetMaterial(mat, 1)  # 1 = Isotropic
print(f"SetMaterial: {ret}")

ret = SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)
print(f"SetMPIsotropic(E={E}, nu={nu}): {ret}")

# Verificar
ret = SapModel.PropMaterial.GetMPIsotropic(mat)
print(f"  Verificacion: E={ret[0]}, nu={ret[1]}")

# Seccion Shell-Thick (Mindlin) - mejor para elementos gruesos
print("\n--- SECCION ---")
shell = "SHELL"
# SetShell_1: 1=Shell-Thin, 2=Shell-Thick, 3=Plate-Thin, 4=Plate-Thick
# Probamos con Plate-Thick (solo flexion, sin membrana)
ret = SapModel.PropArea.SetShell_1(shell, 4, False, mat, 0.0, t, t, 0, "", "")
print(f"SetShell_1(tipo=4=Plate-Thick, t={t}): {ret}")

ret = SapModel.PropArea.GetShell_1(shell)
print(f"  Verificacion: tipo={ret[0]}, t={ret[4]}")

# Crear nodos
print("\n--- NODOS ---")
a1 = a / n_a
b1 = b / n_b

nodos = {}
nodo_id = 1

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * a1
        y = j * b1
        name = str(nodo_id)
        ret = SapModel.PointObj.AddCartesian(x, y, 0.0, name)
        nodos[nodo_id] = (x, y)
        nodo_id += 1

print(f"{len(nodos)} nodos creados")

# Verificar coordenadas
ret = SapModel.PointObj.GetCoordCartesian("1")
print(f"  Nodo 1: ({ret[0]}, {ret[1]}, {ret[2]})")
ret = SapModel.PointObj.GetCoordCartesian("35")
print(f"  Nodo 35: ({ret[0]}, {ret[1]}, {ret[2]})")

# Crear elementos
print("\n--- ELEMENTOS ---")
elementos = []
elem_id = 1

for i in range(n_a):
    for j in range(n_b):
        n1 = j + 1 + (n_b + 1) * i
        n2 = n1 + (n_b + 1)
        n3 = n2 + 1
        n4 = n1 + 1
        pts = [str(n1), str(n2), str(n3), str(n4)]
        name = f"E{elem_id}"
        ret = SapModel.AreaObj.AddByPoint(4, pts, name, shell, name)
        elementos.append(name)
        elem_id += 1

print(f"{len(elementos)} elementos creados")

# RESTRICCIONES - Para Plate elements solo se necesita restringir UZ
print("\n--- RESTRICCIONES ---")

n_restringidos = 0
nodos_borde = []

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        nodos_borde.append(nodo)

        # Simplemente apoyado: solo restringir UZ en todo el borde
        # Para evitar movimiento rigido en plano horizontal:
        # - Esquina (0,0): UX, UY, UZ
        # - Esquina (a,0): UY, UZ
        # - Esquina (0,b): UX, UZ
        # - Resto: UZ

        esquina_00 = abs(x) < 0.001 and abs(y) < 0.001
        esquina_a0 = abs(x - a) < 0.001 and abs(y) < 0.001
        esquina_0b = abs(x) < 0.001 and abs(y - b) < 0.001

        if esquina_00:
            restr = [True, True, True, False, False, False]
        elif esquina_a0:
            restr = [False, True, True, False, False, False]
        elif esquina_0b:
            restr = [True, False, True, False, False, False]
        else:
            restr = [False, False, True, False, False, False]

        ret = SapModel.PointObj.SetRestraint(str(nodo), restr)
        n_restringidos += 1

print(f"{n_restringidos} nodos restringidos")

# Verificar restricciones
print("Verificando restricciones:")
for nodo in [1, 5, 31, 18]:
    ret = SapModel.PointObj.GetRestraint(str(nodo))
    x, y = nodos[nodo]
    print(f"  Nodo {nodo} ({x},{y}): {list(ret[0])}")

# CARGAS
print("\n--- CARGAS ---")
# Verificar patron DEAD
ret = SapModel.LoadPatterns.GetNameList()
patrones = list(ret[1]) if ret[0] > 0 else []
print(f"Patrones: {patrones}")

# Aplicar carga uniforme
for elem in elementos:
    # Dir=6 es Gravity (Z global negativo)
    ret = SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)

print(f"Carga q={q} kN/m2 aplicada (Gravity)")

# GUARDAR
print("\n--- GUARDAR ---")
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Definitivo.sdb"
ret = SapModel.File.Save(ModelPath)
print(f"Guardado: {ret}")

# ANALIZAR
print("\n--- ANALIZAR ---")
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

if ret != 0:
    print("ERROR en analisis")
    exit(1)

print(f"Bloqueado: {SapModel.GetModelIsLocked()}")

# RESULTADOS
print("\n" + "="*70)
print("RESULTADOS")
print("="*70)

SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Desplazamientos
print("\nDesplazamientos UZ (mm):")
U3_dict = {}

for nodo in nodos:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]

# Matriz
print(f"\n{'y\\x':<6}", end="")
for i in range(n_a + 1):
    print(f"{i*a1:>8.1f}", end="")
print()

for j in range(n_b, -1, -1):
    y = j * b1
    print(f"{y:<6.1f}", end="")
    for i in range(n_a + 1):
        x = i * a1
        for nodo, (nx, ny) in nodos.items():
            if abs(nx - x) < 0.001 and abs(ny - y) < 0.001:
                uz = U3_dict.get(nodo, 0) * 1000
                print(f"{uz:>8.3f}", end="")
                break
    print()

# Centro
print(f"\nCentro (x={a/2}, y={b/2}):")
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.01 and abs(y - b/2) < 0.01:
        print(f"  Nodo {nodo}: UZ = {U3_dict.get(nodo, 0)*1000:.4f} mm")
        break

# Maximo
if U3_dict:
    min_nodo = min(U3_dict, key=U3_dict.get)
    print(f"\nMaximo: Nodo {min_nodo} {nodos[min_nodo]}: UZ = {U3_dict[min_nodo]*1000:.4f} mm")

# Solucion de Navier
print("\n--- SOLUCION ANALITICA ---")
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
print(f"w_centro (Navier) = {w_navier*1000:.4f} mm")

# Comparacion
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.01 and abs(y - b/2) < 0.01:
        w_sap = abs(U3_dict.get(nodo, 0))
        error = abs(w_sap - w_navier) / w_navier * 100 if w_navier != 0 else 0
        print(f"\nComparacion:")
        print(f"  Navier:  {w_navier*1000:.4f} mm")
        print(f"  SAP2000: {w_sap*1000:.4f} mm")
        print(f"  Error:   {error:.2f}%")
        break

print("\n" + "="*70)
