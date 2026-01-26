# -*- coding: utf-8 -*-
"""
LOSA SIMPLE - VERSION MINIMA
============================
Version simplificada para diagnosticar el problema.
"""

import comtypes.client

print("="*60)
print("LOSA SIMPLE - SAP2000")
print("="*60)

# Conectar
print("\n[1] Conectando...")
sap = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
m = sap.SapModel
print(f"SAP2000 {m.GetVersion()[0]}")

# Modelo nuevo
print("\n[2] Creando modelo...")
m.InitializeNewModel(6)  # kN, m, C
m.File.NewBlank()

# Material simple
print("\n[3] Material...")
m.PropMaterial.SetMaterial("MAT", 1)
m.PropMaterial.SetMPIsotropic("MAT", 30e6, 0.2, 0, 0)  # E=30GPa, nu=0.2

# Seccion shell
print("\n[4] Seccion shell...")
m.PropArea.SetShell_1("SHELL", 1, False, "MAT", 0, 0.2, 0.2, 0, "", "")

# 4 nodos (placa simple 2x2m)
print("\n[5] Nodos...")
m.PointObj.AddCartesian(0, 0, 0, "1")
m.PointObj.AddCartesian(2, 0, 0, "2")
m.PointObj.AddCartesian(2, 2, 0, "3")
m.PointObj.AddCartesian(0, 2, 0, "4")

# 1 elemento
print("\n[6] Elemento...")
m.AreaObj.AddByPoint(4, ["1", "2", "3", "4"], "A1", "SHELL", "A1")

# Apoyos: todos excepto nodo 3
print("\n[7] Apoyos...")
m.PointObj.SetRestraint("1", [True, True, True, True, True, True], 0)  # fijo
m.PointObj.SetRestraint("2", [True, True, True, True, True, True], 0)  # fijo
m.PointObj.SetRestraint("3", [True, True, False, False, False, True], 0)  # libre Z
m.PointObj.SetRestraint("4", [True, True, True, True, True, True], 0)  # fijo

# Carga puntual en nodo 3
print("\n[8] Carga...")
m.PointObj.SetLoadForce("3", "Dead", [0, 0, -10, 0, 0, 0], 0, "Global")

# Ejecutar
print("\n[9] Analisis...")
ret = m.Analyze.RunAnalysis()
print(f"RunAnalysis: {ret}")

# Resultados
print("\n[10] Resultados...")
m.Results.Setup.DeselectAllCasesAndCombosForOutput()
m.Results.Setup.SetCaseSelectedForOutput("Dead")

ret = m.Results.JointDispl("3", 0)
print(f"JointDispl nodo 3: n={ret[0]}")

if ret[0] > 0:
    U3 = ret[9][0]
    print(f"  U3 = {U3*1000:.4f} mm")
else:
    print("  Sin resultados")

# Guardar
print("\n[11] Guardando...")
m.File.Save(r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Simple.sdb")

print("\nListo. Abre SAP2000_Simple.sdb para verificar.")
