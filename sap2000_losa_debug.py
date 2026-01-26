# -*- coding: utf-8 -*-
"""
LOSA RECTANGULAR - DEBUG VERSION
================================
Version con logging detallado para diagnosticar problemas.
"""

import comtypes.client
import numpy as np
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

print("="*70)
print("LOSA RECTANGULAR - DEBUG")
print("="*70)

# Datos
a = 6.0
b = 4.0
t = 0.1
q = 10.0
E = 35000e3  # kPa
nu = 0.15

n_a = 6
n_b = 4
a_1 = a / n_a
b_1 = b / n_b

log.info(f"Losa: {a}x{b}m, t={t}m, q={q}kN/m2")
log.info(f"Material: E={E/1000}MPa, nu={nu}")
log.info(f"Malla: {n_a}x{n_b}")

# Conectar
log.info("Conectando a SAP2000...")
mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
log.info(f"SAP2000 {SapModel.GetVersion()[0]}")

# Crear modelo
log.info("Inicializando modelo...")
ret = SapModel.InitializeNewModel(6)
log.debug(f"InitializeNewModel: {ret}")

ret = SapModel.File.NewBlank()
log.debug(f"NewBlank: {ret}")

# Material
log.info("Creando material...")
mat = "MAT"
G = E / (2 * (1 + nu))

ret = SapModel.PropMaterial.SetMaterial(mat, 1)
log.debug(f"SetMaterial: {ret}")

ret = SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0, G)
log.debug(f"SetMPIsotropic: {ret}")

# Verificar material
ret = SapModel.PropMaterial.GetMPIsotropic(mat)
log.debug(f"GetMPIsotropic: E={ret[0]}, nu={ret[1]}")

# Seccion
log.info("Creando seccion shell...")
shell = "SHELL"

# Usar Shell-Thin (tipo 1)
ret = SapModel.PropArea.SetShell_1(shell, 1, False, mat, 0.0, t, t, 0, "", "")
log.debug(f"SetShell_1: {ret}")

# Verificar seccion
ret = SapModel.PropArea.GetShell_1(shell)
log.debug(f"GetShell_1: tipo={ret[0]}, mat={ret[2]}, t_mem={ret[4]}, t_bend={ret[5]}")

# Crear nodos
log.info("Creando nodos...")
nodos = {}
nodo_num = 1

for i in range(n_a + 1):
    for j in range(n_b + 1):
        x = i * a_1
        y = j * b_1
        nombre = str(nodo_num)
        ret = SapModel.PointObj.AddCartesian(x, y, 0.0, nombre)
        nodos[nodo_num] = (x, y)
        if nodo_num <= 5:
            log.debug(f"  Nodo {nombre}: ({x}, {y}, 0) -> ret={ret}")
        nodo_num += 1

log.info(f"{len(nodos)} nodos creados")

# Crear elementos
log.info("Creando elementos...")
elementos = []
elem_num = 1

for i in range(n_a):
    for j in range(n_b):
        j1 = j + 1 + (n_b + 1) * i
        j2 = j1 + (n_b + 1)
        j3 = j2 + 1
        j4 = j1 + 1

        pts = [str(j1), str(j2), str(j3), str(j4)]
        nombre = f"E{elem_num}"
        ret = SapModel.AreaObj.AddByPoint(4, pts, nombre, shell, nombre)
        elementos.append(nombre)
        if elem_num <= 3:
            log.debug(f"  {nombre}: nodos={pts} -> ret={ret}")
        elem_num += 1

log.info(f"{len(elementos)} elementos creados")

# Restricciones
log.info("Aplicando restricciones...")
n_apoyados = 0

for nodo, (x, y) in nodos.items():
    en_borde = (abs(x) < 0.001 or abs(x - a) < 0.001 or
                abs(y) < 0.001 or abs(y - b) < 0.001)

    if en_borde:
        # Apoyo simple
        restr = [True, True, True, False, False, True]
        n_apoyados += 1
    else:
        # Interior
        restr = [True, True, False, False, False, True]

    ret = SapModel.PointObj.SetRestraint(str(nodo), restr, 0)
    if nodo <= 5:
        log.debug(f"  Nodo {nodo}: restr={restr} -> ret={ret}")

log.info(f"{n_apoyados} nodos apoyados en perimetro")

# Verificar patron de carga
log.info("Verificando patrones de carga...")
ret = SapModel.LoadPatterns.GetNameList()
patrones = list(ret[1]) if ret[0] > 0 else []
log.info(f"Patrones existentes: {patrones}")

# Si no existe DEAD, crearlo
if "DEAD" not in patrones:
    ret = SapModel.LoadPatterns.Add("DEAD", 1)
    log.info(f"Patron DEAD creado: {ret}")

# Aplicar carga uniforme
log.info("Aplicando carga uniforme...")

for i, elem in enumerate(elementos):
    # SetLoadUniform(Name, LoadPat, Value, Dir, Replace, CSys, ItemType)
    # Dir: 6 = Gravity (Z global negativo)
    ret = SapModel.AreaObj.SetLoadUniform(elem, "DEAD", q, 6, True, "Global", 0)
    if i < 3:
        log.debug(f"  {elem}: SetLoadUniform(q={q}, dir=6) -> ret={ret}")

log.info(f"Carga aplicada a {len(elementos)} elementos")

# Verificar cargas
log.info("Verificando cargas aplicadas...")
for elem in elementos[:3]:
    ret = SapModel.AreaObj.GetLoadUniform(elem)
    log.debug(f"  {elem}: GetLoadUniform -> n={ret[0]}, pat={ret[1]}, val={ret[3]}, dir={ret[4]}")

# Verificar casos de carga
log.info("Verificando casos de carga...")
ret = SapModel.LoadCases.GetNameList()
casos = list(ret[1]) if ret[0] > 0 else []
log.info(f"Casos de carga: {casos}")

# Configurar caso DEAD para ejecutar
log.info("Configurando analisis...")
ret = SapModel.Analyze.SetRunCaseFlag("", False, True)  # Desactivar todos
log.debug(f"SetRunCaseFlag('', False): {ret}")

ret = SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)  # Activar DEAD
log.debug(f"SetRunCaseFlag('DEAD', True): {ret}")

# Ver DOF activos
ret = SapModel.Analyze.GetActiveDOF()
dof = list(ret[0])
dof_names = ["UX", "UY", "UZ", "RX", "RY", "RZ"]
activos = [dof_names[i] for i in range(6) if dof[i]]
log.info(f"DOF activos: {activos}")

# Ejecutar analisis
log.info("Ejecutando analisis...")
ret = SapModel.Analyze.RunAnalysis()
log.info(f"RunAnalysis: {ret}")

# Verificar estado
locked = SapModel.GetModelIsLocked()
log.info(f"Modelo bloqueado (analizado): {locked}")

# Extraer resultados
log.info("Extrayendo resultados...")

SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
log.debug(f"SetCaseSelectedForOutput('DEAD'): {ret}")

# Desplazamientos
log.info("Obteniendo desplazamientos...")
ret = SapModel.Results.JointDispl("", 2)
n_results = ret[0]
log.info(f"JointDispl: {n_results} resultados")

if n_results > 0:
    nombres = list(ret[2])
    casos_res = list(ret[4])
    U3 = list(ret[9])
    R1 = list(ret[10])
    R2 = list(ret[11])

    log.debug(f"  Primer resultado: nodo={nombres[0]}, caso={casos_res[0]}")
    log.debug(f"  U3[0]={U3[0]}, R1[0]={R1[0]}, R2[0]={R2[0]}")

    # Desplazamiento maximo
    min_U3 = min(U3)
    max_U3 = max(U3)
    log.info(f"  U3: min={min_U3*1000:.4f}mm, max={max_U3*1000:.4f}mm")

    # Nodo central (cerca de x=3, y=2)
    for i, nombre in enumerate(nombres):
        nodo = int(nombre)
        if nodo in nodos:
            x, y = nodos[nodo]
            if abs(x - 3) < 0.5 and abs(y - 2) < 0.5:
                log.info(f"  Centro ({x},{y}): U3={U3[i]*1000:.4f}mm")
                break
else:
    log.warning("NO HAY RESULTADOS DE DESPLAZAMIENTO")

    # Diagnostico adicional
    log.info("Diagnostico adicional...")

    # Ver si hay errores
    log.info("Verificando si modelo tiene elementos...")
    n_areas = SapModel.AreaObj.Count()
    log.info(f"  Areas: {n_areas}")

    n_joints = SapModel.PointObj.Count()
    log.info(f"  Nodos: {n_joints}")

    # Ver restricciones
    log.info("Verificando restricciones en nodos interiores...")
    nodo_interior = 13  # deberia ser interior
    if nodo_interior in nodos:
        ret = SapModel.PointObj.GetRestraint(str(nodo_interior))
        log.info(f"  Nodo {nodo_interior} restricciones: {list(ret[0])}")

# Fuerzas en elementos
log.info("Obteniendo fuerzas en elementos...")
for elem in elementos[:3]:
    ret = SapModel.Results.AreaForceShell(elem, 0)
    n = ret[0]
    if n > 0:
        M11 = list(ret[14])
        M22 = list(ret[15])
        log.debug(f"  {elem}: n={n}, M11={M11[:2]}, M22={M22[:2]}")
    else:
        log.debug(f"  {elem}: sin resultados")

# Guardar
log.info("Guardando modelo...")
ruta = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Losa_Debug.sdb"
ret = SapModel.File.Save(ruta)
log.info(f"Guardado: {ruta}")

print("\n" + "="*70)
print("RESUMEN")
print("="*70)
print(f"Nodos: {len(nodos)}")
print(f"Elementos: {len(elementos)}")
print(f"Apoyados: {n_apoyados}")
print(f"Analisis: {'OK' if ret == 0 else 'ERROR'}")
print(f"Resultados: {'SI' if n_results > 0 else 'NO'}")
print("="*70)
