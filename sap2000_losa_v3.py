# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - VERSION 3 (Siguiendo ejemplo oficial CSI)
=============================================================
Basado en Example 7 (Python COM) de la documentacion CSI OAPI.
Replica el ejemplo "Rectangular Slab FEA.cpd" de Calcpad.
"""

import os
import sys
import comtypes.client

print("="*70)
print("LOSA RECTANGULAR - CALCPAD vs SAP2000 (v3)")
print("="*70)

# ============================================================
# DATOS DEL PROBLEMA (del ejemplo Calcpad)
# ============================================================
a = 6.0       # dimension en X (m)
b = 4.0       # dimension en Y (m)
t = 0.1       # espesor (m)
q = 10.0      # carga (kN/m2)
E = 35000e3   # E en kPa (35000 MPa = 35000*1000 kPa)
nu = 0.15     # Poisson

# Malla
n_a = 6       # elementos en X
n_b = 4       # elementos en Y
a_1 = a / n_a  # dimension elemento X
b_1 = b / n_b  # dimension elemento Y

print(f"\n--- DATOS DEL PROBLEMA ---")
print(f"Losa: {a}m x {b}m, t={t}m")
print(f"Carga: q={q} kN/m2")
print(f"Material: E={E/1000} MPa, nu={nu}")
print(f"Malla: {n_a}x{n_b} elementos ({n_a*n_b} total)")

# ============================================================
# RUTA DEL MODELO (importante: debe existir antes de analizar)
# ============================================================
APIPath = r'C:\Users\j-b-j\Documents\Calcpad-7.5.7'
ModelPath = APIPath + os.sep + 'SAP2000_Losa_v3.sdb'

# ============================================================
# CONECTAR A SAP2000 (usando metodo del ejemplo oficial)
# ============================================================
print("\n--- CONECTANDO A SAP2000 ---")

# Crear API helper object (como en ejemplo oficial)
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)

# Obtener instancia activa de SAP2000
try:
    mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
    print("Conectado a SAP2000 existente")
except (OSError, comtypes.COMError):
    print("No se encontro SAP2000 activo, intentando GetActiveObject...")
    mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")

SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# ============================================================
# INICIALIZAR MODELO
# ============================================================
print("\n--- INICIALIZANDO MODELO ---")

# Inicializar modelo (sin parametros como en ejemplo oficial)
ret = SapModel.InitializeNewModel()
print(f"InitializeNewModel: {ret}")

# Crear modelo en blanco
ret = SapModel.File.NewBlank()
print(f"NewBlank: {ret}")

# Cambiar unidades a kN, m, C
kN_m_C = 6
ret = SapModel.SetPresentUnits(kN_m_C)
print(f"SetPresentUnits (kN,m,C): {ret}")

# ============================================================
# DEFINIR MATERIAL
# ============================================================
print("\n--- DEFINIENDO MATERIAL ---")
MATERIAL_CONCRETE = 2
mat_name = 'CONC'

ret = SapModel.PropMaterial.SetMaterial(mat_name, MATERIAL_CONCRETE)
print(f"SetMaterial: {ret}")

# Propiedades isotropicas: E, nu, alpha (coef. termico)
G = E / (2 * (1 + nu))
ret = SapModel.PropMaterial.SetMPIsotropic(mat_name, E, nu, 0.0)
print(f"SetMPIsotropic (E={E/1000} MPa, nu={nu}): {ret}")

# ============================================================
# DEFINIR SECCION SHELL
# ============================================================
print("\n--- DEFINIENDO SECCION SHELL ---")
shell_name = 'LOSA'

# SetShell_1(Name, ShellType, IncludeDrillingDOF, MatProp, MatAng, Thickness, BendThick, Color, Notes, GUID)
# ShellType: 1=Shell-Thin, 2=Shell-Thick, 3=Plate-Thin, 4=Plate-Thick, 5=Membrane
SHELL_THICK = 2
ret = SapModel.PropArea.SetShell_1(shell_name, SHELL_THICK, False, mat_name, 0.0, t, t, 0, "", "")
print(f"SetShell_1 (Shell-Thick, t={t}m): {ret}")

# ============================================================
# CREAR NODOS
# ============================================================
print("\n--- CREANDO NODOS ---")
nodos = {}
nodo_num = 1

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * a_1
        y = j * b_1
        nombre = str(nodo_num)
        ret = SapModel.PointObj.AddCartesian(x, y, 0.0, nombre)
        nodos[nodo_num] = (x, y)
        nodo_num += 1

print(f"{len(nodos)} nodos creados")

# ============================================================
# CREAR ELEMENTOS
# ============================================================
print("\n--- CREANDO ELEMENTOS ---")
elementos = []
elem_num = 1

for i in range(n_a):
    for j in range(n_b):
        # Nodos del elemento (antihorario visto desde arriba)
        j1 = j + 1 + (n_b + 1) * i
        j2 = j1 + (n_b + 1)
        j3 = j2 + 1
        j4 = j1 + 1

        pts = [str(j1), str(j2), str(j3), str(j4)]
        nombre = f"E{elem_num}"
        ret = SapModel.AreaObj.AddByPoint(4, pts, nombre, shell_name, nombre)
        elementos.append(nombre)
        elem_num += 1

print(f"{len(elementos)} elementos creados")

# ============================================================
# CONDICIONES DE BORDE
# ============================================================
print("\n--- APLICANDO RESTRICCIONES ---")
# Apoyo simple en perimetro: U3=0 (desplazamiento vertical restringido)
# Rotaciones libres

n_apoyados = 0
Restraint_borde = [True, True, True, False, False, True]   # UX,UY,UZ,RX,RY,RZ
Restraint_interior = [True, True, False, False, False, True]

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        ret = SapModel.PointObj.SetRestraint(str(nodo), Restraint_borde)
        n_apoyados += 1
    else:
        ret = SapModel.PointObj.SetRestraint(str(nodo), Restraint_interior)

print(f"{n_apoyados} nodos apoyados en perimetro")

# ============================================================
# PATRON Y CASO DE CARGA
# ============================================================
print("\n--- CONFIGURANDO CARGAS ---")

# Verificar patrones existentes
ret = SapModel.LoadPatterns.GetNameList()
n_patterns = ret[0]
patterns = list(ret[1]) if n_patterns > 0 else []
print(f"Patrones existentes: {patterns}")

# Si no existe un patron adecuado, usar DEAD o crear uno
load_pattern = "DEAD"
if load_pattern not in patterns:
    LTYPE_DEAD = 1
    ret = SapModel.LoadPatterns.Add(load_pattern, LTYPE_DEAD, 1, True)
    print(f"Patron '{load_pattern}' creado: {ret}")

# ============================================================
# APLICAR CARGA UNIFORME
# ============================================================
print("\n--- APLICANDO CARGA UNIFORME ---")

# Aplicar carga a cada elemento
# SetLoadUniform(Name, LoadPat, Value, Dir, Replace, CSys, ItemType)
# Dir: 6 = Gravity (Z global negativo)

for elem in elementos:
    ret = SapModel.AreaObj.SetLoadUniform(elem, load_pattern, q, 6, True, "Global", 0)

print(f"Carga q={q} kN/m2 aplicada a {len(elementos)} elementos")

# Verificar una carga
ret = SapModel.AreaObj.GetLoadUniform(elementos[0])
print(f"Verificacion E1: n_cargas={ret[0]}, patron={ret[1] if ret[0]>0 else 'N/A'}")

# ============================================================
# REFRESCAR VISTA
# ============================================================
ret = SapModel.View.RefreshView(0, False)
print(f"RefreshView: {ret}")

# ============================================================
# GUARDAR MODELO (CRITICO: debe hacerse ANTES del analisis)
# ============================================================
print("\n--- GUARDANDO MODELO ---")
ret = SapModel.File.Save(ModelPath)
print(f"Save({ModelPath}): {ret}")

# ============================================================
# EJECUTAR ANALISIS
# ============================================================
print("\n--- EJECUTANDO ANALISIS ---")

# Configurar casos a ejecutar
ret = SapModel.Analyze.SetRunCaseFlag("", False, True)  # Desactivar todos
print(f"SetRunCaseFlag('', False): {ret}")

ret = SapModel.Analyze.SetRunCaseFlag(load_pattern, True, False)  # Activar DEAD
print(f"SetRunCaseFlag('{load_pattern}', True): {ret}")

# Ejecutar analisis (esto crea el modelo de analisis)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Verificar estado
locked = SapModel.GetModelIsLocked()
print(f"Modelo bloqueado (analizado): {locked}")

# ============================================================
# EXTRAER RESULTADOS
# ============================================================
print("\n--- EXTRAYENDO RESULTADOS ---")

# Inicializar variables para resultados (como en ejemplo oficial)
NumberResults = 0
Obj = []
Elm = []
ACase = []
StepType = []
StepNum = []
U1 = []
U2 = []
U3 = []
R1 = []
R2 = []
R3 = []
ObjectElm = 0

# Seleccionar caso para output
ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
print(f"DeselectAllCasesAndCombosForOutput: {ret}")

ret = SapModel.Results.Setup.SetCaseSelectedForOutput(load_pattern)
print(f"SetCaseSelectedForOutput('{load_pattern}'): {ret}")

# Obtener desplazamientos de todos los nodos
# JointDispl(Name, ItemTypeElm, NumberResults, Obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3)
# ItemTypeElm: 0=Object, 1=Element, 2=GroupElm (All)
result = SapModel.Results.JointDispl("", 2, NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3)

NumberResults = result[0]
print(f"\nJointDispl: {NumberResults} resultados")

if NumberResults > 0:
    nombres = list(result[1])
    U3_results = list(result[9])
    R1_results = list(result[10])
    R2_results = list(result[11])

    # Desplazamiento maximo
    min_U3 = min(U3_results)
    max_U3 = max(U3_results)
    max_idx = U3_results.index(min_U3)

    print(f"\n--- DESPLAZAMIENTOS ---")
    print(f"U3 min = {min_U3*1000:.4f} mm (nodo {nombres[max_idx]})")
    print(f"U3 max = {max_U3*1000:.4f} mm")

    # Buscar nodo central (cerca de x=3, y=2)
    print(f"\nDesplazamientos en nodos centrales:")
    for nodo, (x, y) in nodos.items():
        if abs(x - 3) < 0.1 and abs(y - 2) < 0.1:
            try:
                idx = nombres.index(str(nodo))
                print(f"  Nodo {nodo} ({x},{y}): U3 = {U3_results[idx]*1000:.4f} mm")
            except ValueError:
                pass

    # Mostrar desplazamientos en linea central y=b/2
    print(f"\nDesplazamientos en y=b/2={b/2}m:")
    for nodo, (x, y) in sorted(nodos.items()):
        if abs(y - b/2) < 0.01:
            try:
                idx = nombres.index(str(nodo))
                print(f"  x={x:.1f}m: U3 = {U3_results[idx]*1000:.4f} mm")
            except ValueError:
                pass

    # Momentos flectores
    print(f"\n--- MOMENTOS FLECTORES ---")
    M11_all = []
    M22_all = []
    M12_all = []

    for elem in elementos:
        ret = SapModel.Results.AreaForceShell(elem, 0)
        n = ret[0]
        if n > 0:
            M11_all.extend(list(ret[14]))
            M22_all.extend(list(ret[15]))
            M12_all.extend(list(ret[16]))

    if M11_all:
        print(f"M11: min={min(M11_all):.4f}, max={max(M11_all):.4f} kNm/m")
    if M22_all:
        print(f"M22: min={min(M22_all):.4f}, max={max(M22_all):.4f} kNm/m")
    if M12_all:
        print(f"M12: min={min(M12_all):.4f}, max={max(M12_all):.4f} kNm/m")

else:
    print("*** NO HAY RESULTADOS ***")
    print("\nDiagnostico:")

    # Ver casos de carga disponibles
    ret = SapModel.LoadCases.GetNameList()
    print(f"Casos de carga: {list(ret[1]) if ret[0]>0 else 'ninguno'}")

    # Ver DOF activos
    ret = SapModel.Analyze.GetActiveDOF()
    dof = list(ret[0])
    dof_names = ["UX", "UY", "UZ", "RX", "RY", "RZ"]
    activos = [dof_names[i] for i in range(6) if dof[i]]
    print(f"DOF activos: {activos}")

    # Contar objetos
    print(f"Areas: {SapModel.AreaObj.Count()}")
    print(f"Nodos: {SapModel.PointObj.Count()}")

# ============================================================
# COMPARACION CON CALCPAD
# ============================================================
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
SAP2000 (Shell-Thick Mindlin): resultados deben ser comparables
""")

print("="*70)
print("COMPLETADO")
print("="*70)
