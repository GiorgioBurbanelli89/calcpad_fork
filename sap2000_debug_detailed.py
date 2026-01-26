# -*- coding: utf-8 -*-
"""
Debug detallado del modelo SAP2000
"""

import comtypes.client

print("="*70)
print("DEBUG DETALLADO - MODELO SAP2000")
print("="*70)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel

print(f"SAP2000 {SapModel.GetVersion()[0]}")
print(f"Modelo bloqueado: {SapModel.GetModelIsLocked()}")

# Listar TODOS los nodos con coordenadas y desplazamientos
print("\n--- NODOS Y DESPLAZAMIENTOS ---")

SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

ret = SapModel.PointObj.GetNameList()
nodos = list(ret[1]) if ret[0] > 0 else []

print(f"{'Nodo':<6}{'X':<8}{'Y':<8}{'Z':<8}{'UZ(mm)':<12}{'Restr'}")
print("-"*60)

for nodo in sorted(nodos, key=int):
    # Coordenadas
    ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
    x, y, z = ret_coord[0], ret_coord[1], ret_coord[2]

    # Restricciones
    ret_restr = SapModel.PointObj.GetRestraint(nodo)
    restr = list(ret_restr[0])
    restr_str = "".join(["1" if r else "0" for r in restr])

    # Desplazamiento
    ret_disp = SapModel.Results.JointDispl(nodo, 0)
    if ret_disp[0] > 0:
        uz = ret_disp[9][0] * 1000  # mm
    else:
        uz = float('nan')

    print(f"{nodo:<6}{x:<8.2f}{y:<8.2f}{z:<8.2f}{uz:<12.4f}{restr_str}")

# Ver cargas en elementos
print("\n--- CARGAS EN ELEMENTOS ---")
ret = SapModel.AreaObj.GetNameList()
elementos = list(ret[1]) if ret[0] > 0 else []

for elem in elementos[:3]:  # Solo primeros 3
    ret_load = SapModel.AreaObj.GetLoadUniform(elem)
    if ret_load[0] > 0:
        patron = ret_load[1]
        valor = list(ret_load[3])
        dir_carga = list(ret_load[4])
        print(f"  {elem}: patron={patron}, valor={valor}, dir={dir_carga}")

# Ver DOF activos del modelo
print("\n--- DOF ACTIVOS ---")
ret = SapModel.Analyze.GetActiveDOF()
dof = list(ret[0])
dof_names = ["UX", "UY", "UZ", "RX", "RY", "RZ"]
activos = [dof_names[i] for i in range(6) if dof[i]]
print(f"DOF: {activos}")

# Ver si hay alguna configuracion especial
print("\n--- PROPIEDADES DE AREA ---")
ret = SapModel.PropArea.GetNameList()
secciones = list(ret[1]) if ret[0] > 0 else []

for sec in secciones:
    ret_shell = SapModel.PropArea.GetShell_1(sec)
    tipo = ret_shell[0]
    mat = ret_shell[2]
    t_mem = ret_shell[4]
    t_bend = ret_shell[5]
    tipos = {1: "Shell-Thin", 2: "Shell-Thick", 3: "Plate-Thin",
             4: "Plate-Thick", 5: "Membrane", 6: "Shell-Layered"}
    print(f"  {sec}: tipo={tipos.get(tipo, tipo)}, mat={mat}, t={t_mem}m")

# Ver orientacion del elemento
print("\n--- ORIENTACION DE ELEMENTOS ---")
for elem in elementos[:3]:
    ret = SapModel.AreaObj.GetLocalAxes(elem)
    print(f"  {elem}: RotZ={ret[0]} grados")

print("\n" + "="*70)
