# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - VERSION MANUAL
=================================
Crear el modelo paso a paso con verificacion rigurosa.
"""

import comtypes.client
import math

print("="*70)
print("LOSA RECTANGULAR - VERSION MANUAL")
print("="*70)

# Datos
a = 6.0   # m
b = 4.0   # m
t = 0.1   # m (100mm)
q = 10.0  # kN/m2
E = 35000e3  # kPa (35000 MPa = 35,000,000 kPa)
nu = 0.15

n_a = 6   # elementos en X
n_b = 4   # elementos en Y

print(f"\nLosa: {a}x{b}m, t={t}m")
print(f"q={q}kN/m2, E={E/1e6}GPa, nu={nu}")
print(f"Malla: {n_a}x{n_b}")

# Conectar a SAP2000
print("\n--- CONECTANDO ---")
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 v{SapModel.GetVersion()[0]}")

# Nuevo modelo
print("\n--- NUEVO MODELO ---")
ret = SapModel.InitializeNewModel()
print(f"InitializeNewModel: {ret}")

ret = SapModel.File.NewBlank()
print(f"NewBlank: {ret}")

# Unidades kN, m
ret = SapModel.SetPresentUnits(6)
print(f"SetPresentUnits(kN,m): {ret}")

# Material
print("\n--- MATERIAL ---")
mat = "MAT"
ret = SapModel.PropMaterial.SetMaterial(mat, 2)  # 2=Concrete
print(f"SetMaterial: {ret}")

ret = SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0)
print(f"SetMPIsotropic(E={E}, nu={nu}): {ret}")

# Verificar
ret = SapModel.PropMaterial.GetMPIsotropic(mat)
print(f"  Verificacion: E={ret[0]}, nu={ret[1]}")

# Seccion Shell
print("\n--- SECCION SHELL ---")
shell = "SHELL"
# SetShell_1: ShellType 1=Shell-Thin (Kirchhoff), 2=Shell-Thick (Mindlin)
ret = SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")
print(f"SetShell_1(Shell-Thin, t={t}): {ret}")

# Verificar
ret = SapModel.PropArea.GetShell_1(shell)
print(f"  Verificacion: tipo={ret[0]}, mat={ret[2]}, t={ret[4]}")

# Crear nodos
print("\n--- CREANDO NODOS ---")
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

# Crear elementos
print("\n--- CREANDO ELEMENTOS ---")
elementos = []
elem_id = 1

for i in range(n_a):
    for j in range(n_b):
        # Nodos del elemento (CCW)
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

# Restricciones
# Para placa simplemente apoyada en bordes:
# - Bordes: desplazamiento vertical = 0 (w = 0)
# - Interior: libre
# - PERO necesitamos prevenir movimiento de cuerpo rigido en el plano
#   Solución: restringir UX,UY en una esquina, UY en otra esquina
print("\n--- RESTRICCIONES ---")

# Identificar nodos especiales
nodo_00 = 1   # (0, 0)
nodo_a0 = (n_b + 1) * n_a + 1  # (a, 0)
nodo_0b = n_b + 1  # (0, b)

print(f"Nodo (0,0): {nodo_00}")
print(f"Nodo ({a},0): {nodo_a0}")
print(f"Nodo (0,{b}): {nodo_0b}")

n_restr = 0

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 1e-6 or abs(x - a) < 1e-6 or
                abs(y) < 1e-6 or abs(y - b) < 1e-6)

    if nodo == nodo_00:
        # Esquina (0,0): fijar UX, UY, UZ
        restr = [True, True, True, False, False, False]
        ret = SapModel.PointObj.SetRestraint(str(nodo), restr)
        print(f"  Nodo {nodo} ({x},{y}): UX=UY=UZ=0, ret={ret}")
        n_restr += 1
    elif nodo == nodo_a0:
        # Esquina (a,0): fijar UY, UZ (permite expansion en X)
        restr = [False, True, True, False, False, False]
        ret = SapModel.PointObj.SetRestraint(str(nodo), restr)
        print(f"  Nodo {nodo} ({x},{y}): UY=UZ=0, ret={ret}")
        n_restr += 1
    elif nodo == nodo_0b:
        # Esquina (0,b): fijar UX, UZ (permite expansion en Y)
        restr = [True, False, True, False, False, False]
        ret = SapModel.PointObj.SetRestraint(str(nodo), restr)
        print(f"  Nodo {nodo} ({x},{y}): UX=UZ=0, ret={ret}")
        n_restr += 1
    elif en_borde:
        # Resto del borde: solo UZ
        restr = [False, False, True, False, False, False]
        ret = SapModel.PointObj.SetRestraint(str(nodo), restr)
        n_restr += 1
    # Nodos interiores: sin restricciones

print(f"\nTotal: {n_restr} nodos restringidos")

# Verificar algunas restricciones
print("\nVerificando restricciones:")
for nodo in [nodo_00, nodo_a0, nodo_0b, 18]:  # 18 deberia ser interior
    ret = SapModel.PointObj.GetRestraint(str(nodo))
    restr = list(ret[0])
    print(f"  Nodo {nodo}: {restr}")

# Cargas
print("\n--- CARGA ---")

# Verificar patron DEAD
ret = SapModel.LoadPatterns.GetNameList()
patrones = list(ret[1]) if ret[0] > 0 else []
print(f"Patrones existentes: {patrones}")

if "DEAD" not in patrones:
    ret = SapModel.LoadPatterns.Add("DEAD", 1)
    print(f"Creado patron DEAD: {ret}")

# Aplicar carga a todos los elementos
for elem in elementos:
    # SetLoadUniform(Name, LoadPat, Value, Dir, Replace, CSys, ItemType)
    # Dir: 6 = Gravity (Z global negativo)
    ret = SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)

print(f"Carga q={q} kN/m2 aplicada a {len(elementos)} elementos")

# Verificar carga
ret = SapModel.AreaObj.GetLoadUniform(elementos[0])
print(f"Verificacion {elementos[0]}: n={ret[0]}")
if ret[0] > 0:
    print(f"  patron={ret[1]}, valor={ret[3]}, dir={ret[4]}")

# Refrescar vista
SapModel.View.RefreshView(0, False)

# Guardar
print("\n--- GUARDANDO ---")
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Manual.sdb"
ret = SapModel.File.Save(ModelPath)
print(f"Save: {ret}")
print(f"Archivo: {ModelPath}")

# Analizar
print("\n--- ANALIZANDO ---")
SapModel.Analyze.SetRunCaseFlag("", False, True)  # Desactivar todos
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)  # Activar DEAD

# Ver DOF activos
ret = SapModel.Analyze.GetActiveDOF()
dof = list(ret[0])
dof_names = ['UX','UY','UZ','RX','RY','RZ']
activos = [dof_names[i] for i in range(6) if dof[i]]
print(f"DOF activos: {activos}")

# Ejecutar
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

if ret != 0:
    print("ERROR en analisis!")
    # Ver status
    ret = SapModel.Analyze.GetCaseStatus()
    if ret[0] > 0:
        for i in range(ret[0]):
            status = {1: "NotRun", 2: "CouldNotStart", 3: "NotFinished", 4: "Finished"}
            print(f"  {ret[1][i]}: {status.get(ret[2][i], ret[2][i])}")
    exit(1)

print(f"Modelo bloqueado: {SapModel.GetModelIsLocked()}")

# Resultados
print("\n" + "="*70)
print("RESULTADOS")
print("="*70)

SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
print(f"SetCaseSelectedForOutput: {ret}")

# Desplazamientos nodo por nodo
print("\nDesplazamientos nodales:")
U3_dict = {}

for nodo in nodos:
    ret = SapModel.Results.JointDispl(str(nodo), 0)
    if ret[0] > 0:
        U3_dict[nodo] = ret[9][0]  # U3 = ret[9]

# Mostrar matriz
print("\nMatriz de desplazamientos UZ (mm):")
print(f"{'y\\x':<6}", end="")
for x in [round(i * a1, 1) for i in range(n_a + 1)]:
    print(f"{x:>8}", end="")
print()

for j in range(n_b, -1, -1):
    y = j * b1
    print(f"{y:<6.1f}", end="")
    for i in range(n_a + 1):
        x = i * a1
        # Buscar nodo
        for nodo, (nx, ny) in nodos.items():
            if abs(nx - x) < 0.001 and abs(ny - y) < 0.001:
                uz = U3_dict.get(nodo, 0) * 1000
                print(f"{uz:>8.3f}", end="")
                break
    print()

# Nodo central
print(f"\nNodo central (x={a/2}, y={b/2}):")
for nodo, (x, y) in nodos.items():
    if abs(x - a/2) < 0.01 and abs(y - b/2) < 0.01:
        print(f"  Nodo {nodo}: UZ = {U3_dict.get(nodo, 0)*1000:.4f} mm")
        break

# Maximo
if U3_dict:
    min_nodo = min(U3_dict, key=U3_dict.get)
    min_uz = U3_dict[min_nodo]
    print(f"\nDesplazamiento maximo:")
    print(f"  Nodo {min_nodo} {nodos[min_nodo]}: UZ = {min_uz*1000:.4f} mm")

# Solucion analitica
print("\n--- SOLUCION ANALITICA (NAVIER) ---")
D = E * t**3 / (12 * (1 - nu**2))

def navier_w(x, y, a, b, q, D, n=100):
    w = 0.0
    for m in range(1, n, 2):
        for nn in range(1, n, 2):
            coef = 16.0 * q / (math.pi**6 * m * nn)
            denom = D * (m**2/a**2 + nn**2/b**2)**2
            w += coef / denom * math.sin(m*math.pi*x/a) * math.sin(nn*math.pi*y/b)
    return w

w_centro = navier_w(a/2, b/2, a, b, q, D)
print(f"D = {D:.2f} kNm")
print(f"w_centro (Navier) = {w_centro*1000:.4f} mm")

# Comparacion
nodo_centro = None
for n, (x, y) in nodos.items():
    if abs(x - a/2) < 0.01 and abs(y - b/2) < 0.01:
        nodo_centro = n
        break

if nodo_centro and nodo_centro in U3_dict:
    w_sap = abs(U3_dict[nodo_centro])
    error = abs(w_sap - w_centro) / w_centro * 100
    print(f"\n--- COMPARACION ---")
    print(f"Navier:  {w_centro*1000:.4f} mm")
    print(f"SAP2000: {w_sap*1000:.4f} mm")
    print(f"Error:   {error:.2f}%")

print("\n" + "="*70)
