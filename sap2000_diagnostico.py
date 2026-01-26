# -*- coding: utf-8 -*-
"""
DIAGNOSTICO SAP2000
===================
Verifica el estado del modelo actual en SAP2000.
"""

import comtypes.client

print("="*60)
print("DIAGNOSTICO SAP2000")
print("="*60)

# Conectar
mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"\nSAP2000 {SapModel.GetVersion()[0]}")

# Estado del modelo
print("\n--- ESTADO DEL MODELO ---")
locked = SapModel.GetModelIsLocked()
print(f"Modelo bloqueado: {locked}")

# Unidades
units = SapModel.GetPresentUnits()
unit_names = {1: "lb,in,F", 2: "lb,ft,F", 3: "kip,in,F", 4: "kip,ft,F",
              5: "kN,mm,C", 6: "kN,m,C", 7: "kgf,mm,C", 8: "kgf,m,C",
              9: "N,mm,C", 10: "N,m,C", 11: "Ton,mm,C", 12: "Ton,m,C",
              13: "kN,cm,C", 14: "kgf,cm,C", 15: "N,cm,C", 16: "Ton,cm,C"}
print(f"Unidades: {unit_names.get(units, units)}")

# Conteo de objetos
print("\n--- OBJETOS EN EL MODELO ---")
print(f"Nodos: {SapModel.PointObj.Count()}")
print(f"Areas: {SapModel.AreaObj.Count()}")
print(f"Frames: {SapModel.FrameObj.Count()}")

# Listar nodos
print("\n--- NODOS ---")
ret = SapModel.PointObj.GetNameList()
if ret[0] > 0:
    for nodo in ret[1]:
        ret_coord = SapModel.PointObj.GetCoordCartesian(nodo)
        x, y, z = ret_coord[0], ret_coord[1], ret_coord[2]
        ret_restr = SapModel.PointObj.GetRestraint(nodo)
        restr = list(ret_restr[0])
        print(f"  {nodo}: ({x:.2f}, {y:.2f}, {z:.2f}) restr={restr}")

# Listar areas
print("\n--- AREAS ---")
ret = SapModel.AreaObj.GetNameList()
if ret[0] > 0:
    for area in ret[1]:
        ret_pts = SapModel.AreaObj.GetPoints(area)
        puntos = list(ret_pts[1])
        ret_prop = SapModel.AreaObj.GetProperty(area)
        prop = ret_prop[0]
        print(f"  {area}: nodos={puntos}, seccion={prop}")

# Listar secciones shell
print("\n--- SECCIONES SHELL ---")
ret = SapModel.PropArea.GetNameList()
if ret[0] > 0:
    for sec in ret[1]:
        ret_shell = SapModel.PropArea.GetShell_1(sec)
        tipo = ret_shell[0]  # 1=thin, 2=thick
        mat = ret_shell[2]
        t_mem = ret_shell[4]
        t_bend = ret_shell[5]
        tipo_str = {1: "Thin", 2: "Thick", 3: "Membrane", 4: "Plate-Thin", 5: "Plate-Thick"}
        print(f"  {sec}: tipo={tipo_str.get(tipo, tipo)}, mat={mat}, t={t_mem}")

# Listar materiales
print("\n--- MATERIALES ---")
ret = SapModel.PropMaterial.GetNameList()
if ret[0] > 0:
    for mat in ret[1]:
        try:
            ret_mp = SapModel.PropMaterial.GetMPIsotropic(mat)
            E = ret_mp[0]
            nu = ret_mp[1]
            print(f"  {mat}: E={E:.2e}, nu={nu}")
        except:
            print(f"  {mat}: (propiedades no disponibles)")

# Listar patrones de carga
print("\n--- PATRONES DE CARGA ---")
ret = SapModel.LoadPatterns.GetNameList()
if ret[0] > 0:
    patrones = list(ret[1])
    print(f"  Patrones: {patrones}")

# Listar casos de carga
print("\n--- CASOS DE CARGA ---")
ret = SapModel.LoadCases.GetNameList()
if ret[0] > 0:
    casos = list(ret[1])
    print(f"  Casos: {casos}")

# Verificar cargas en nodos
print("\n--- CARGAS NODALES ---")
ret = SapModel.PointObj.GetNameList()
if ret[0] > 0:
    for nodo in ret[1]:
        # GetLoadForce retorna las cargas de todos los patrones
        ret_load = SapModel.PointObj.GetLoadForce(nodo)
        if ret_load[0] > 0:
            patrones = list(ret_load[1])
            valores = list(ret_load[3])  # [F1, F2, F3, M1, M2, M3] para cada patron
            for i, pat in enumerate(patrones):
                start = i * 6
                carga = valores[start:start+6]
                if any(c != 0 for c in carga):
                    print(f"  {nodo} - {pat}: F=({carga[0]:.2f}, {carga[1]:.2f}, {carga[2]:.2f}), M=({carga[3]:.2f}, {carga[4]:.2f}, {carga[5]:.2f})")

# Verificar si el modelo puede analizarse
print("\n--- VERIFICACION DE ANALISIS ---")

# Verificar DOF
ret = SapModel.Analyze.GetActiveDOF()
dof = list(ret[0])
dof_names = ["UX", "UY", "UZ", "RX", "RY", "RZ"]
active = [dof_names[i] for i in range(6) if dof[i]]
print(f"DOF activos: {active}")

# Intentar analizar
print("\n--- INTENTANDO ANALISIS ---")
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis codigo: {ret}")

if ret == 0:
    print("Analisis exitoso!")

    # Resultados
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

    # Obtener primer caso de carga disponible
    ret_casos = SapModel.LoadCases.GetNameList()
    if ret_casos[0] > 0:
        caso = ret_casos[1][0]
        SapModel.Results.Setup.SetCaseSelectedForOutput(caso)

        ret_disp = SapModel.Results.JointDispl("", 2)
        print(f"\nDesplazamientos ({caso}):")
        if ret_disp[0] > 0:
            nombres = list(ret_disp[2])
            U3 = list(ret_disp[9])
            for i in range(ret_disp[0]):
                print(f"  {nombres[i]}: U3={U3[i]:.6e}")
        else:
            print("  Sin resultados")
else:
    print(f"ERROR en analisis (codigo {ret})")
    print("Posibles causas:")
    print("  - Modelo inestable (falta restricciones)")
    print("  - Elemento mal definido")
    print("  - Sin cargas aplicadas")

print("\n" + "="*60)
