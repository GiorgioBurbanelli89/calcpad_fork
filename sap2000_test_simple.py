# -*- coding: utf-8 -*-
"""
Test simple con viga en cantiléver para verificar que el API funciona
"""

import comtypes.client

print("="*60)
print("TEST SIMPLE - VIGA EN CANTILEVER")
print("="*60)

# Datos
L = 10.0   # longitud (m)
P = 100.0  # carga puntual (kN)
E = 200e6  # kPa (200 GPa para acero)
I = 0.0001 # m^4 (momento de inercia aproximado)

# Conectar
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Nuevo modelo
print("\n--- NUEVO MODELO ---")
SapModel.InitializeNewModel()
SapModel.File.NewBlank()
SapModel.SetPresentUnits(6)  # kN, m

# Material
print("\n--- MATERIAL ---")
mat = "STEEL"
SapModel.PropMaterial.SetMaterial(mat, 1)  # 1=Steel
SapModel.PropMaterial.SetMPIsotropic(mat, E, 0.3, 0.0)

# Seccion
print("\n--- SECCION ---")
sec = "SEC1"
# SetGeneral: Area, As2, As3, Torsion, I22, I33, S22, S33, Z22, Z33, R22, R33
A = 0.01   # m^2
Iz = 0.0001  # m^4
Iy = 0.0001  # m^4
J = 0.0002   # m^4
SapModel.PropFrame.SetGeneral(sec, mat, 0.0, 0.0, A, A, A, J, Iy, Iz, 0, 0, 0, 0, 0, 0)

# Nodos
print("\n--- NODOS ---")
SapModel.PointObj.AddCartesian(0, 0, 0, "1")  # Base
SapModel.PointObj.AddCartesian(L, 0, 0, "2")  # Extremo libre

# Elemento
print("\n--- ELEMENTO ---")
ret = SapModel.FrameObj.AddByCoord(0, 0, 0, L, 0, 0, "VIGA", sec, "VIGA")
print(f"AddByCoord: {ret}")

# Restriccion en base (empotramiento)
print("\n--- RESTRICCION ---")
empotramiento = [True, True, True, True, True, True]
ret = SapModel.PointObj.SetRestraint("1", empotramiento)
print(f"SetRestraint('1', empotramiento): {ret}")

# Verificar
ret = SapModel.PointObj.GetRestraint("1")
print(f"GetRestraint('1'): {list(ret[0])}")

# Carga puntual en extremo libre (Z negativo)
print("\n--- CARGA ---")
carga = [0, 0, -P, 0, 0, 0]  # Fx, Fy, Fz, Mx, My, Mz
ret = SapModel.PointObj.SetLoadForce("2", "DEAD", carga)
print(f"SetLoadForce('2', -P): {ret}")

# Guardar
print("\n--- GUARDAR ---")
ModelPath = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Test_Cantilever.sdb"
SapModel.File.Save(ModelPath)

# Analizar
print("\n--- ANALIZAR ---")
SapModel.Analyze.SetRunCaseFlag("", False, True)
SapModel.Analyze.SetRunCaseFlag("DEAD", True, False)
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Resultados
print("\n--- RESULTADOS ---")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

# Desplazamiento en nodo 1 (base, debe ser 0)
ret = SapModel.Results.JointDispl("1", 0)
if ret[0] > 0:
    u3_base = ret[9][0]
    print(f"Nodo 1 (base): UZ = {u3_base*1000:.6f} mm (debe ser ~0)")

# Desplazamiento en nodo 2 (extremo libre)
ret = SapModel.Results.JointDispl("2", 0)
if ret[0] > 0:
    u3_libre = ret[9][0]
    print(f"Nodo 2 (extremo): UZ = {u3_libre*1000:.4f} mm")

# Calculo teorico: delta = P*L^3/(3*E*I)
delta_teorico = P * L**3 / (3 * E * Iz) * 1000  # mm
print(f"\nTeorico: delta = P*L^3/(3*E*I) = {delta_teorico:.4f} mm")

if ret[0] > 0:
    error = abs(abs(u3_libre*1000) - delta_teorico) / delta_teorico * 100
    print(f"Error: {error:.2f}%")

print("\n" + "="*60)
