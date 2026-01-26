# -*- coding: utf-8 -*-
"""
PLACA Q4 SIMPLE EN SAP2000
==========================
Modelo minimo para verificar que SAP2000 funciona correctamente.
"""

import comtypes.client
import numpy as np

print("="*60)
print("PLACA Q4 SIMPLE - SAP2000")
print("="*60)

# Datos
E = 2e7
nu = 0.30
t = 0.02
G = E / (2 * (1 + nu))

# Conectar
print("\n--- CONECTANDO ---")
mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
SapModel = mySapObject.SapModel
print(f"SAP2000 {SapModel.GetVersion()[0]}")

# Crear modelo
print("\n--- CREANDO MODELO ---")
SapModel.InitializeNewModel(6)
SapModel.File.NewBlank()

# Material y seccion
SapModel.PropMaterial.SetMaterial("MAT", 1)
SapModel.PropMaterial.SetMPIsotropic("MAT", E, nu, 0.0, G)
SapModel.PropArea.SetShell_1("SH", 2, False, "MAT", 0.0, t, t, 0, "", "")
print("Material y seccion creados")

# Nodos
SapModel.PointObj.AddCartesian(0.0, 0.0, 0.0, "1")
SapModel.PointObj.AddCartesian(1.0, 0.0, 0.0, "2")
SapModel.PointObj.AddCartesian(1.0, 1.0, 0.0, "3")
SapModel.PointObj.AddCartesian(0.0, 1.0, 0.0, "4")
print("4 nodos creados")

# Elemento
SapModel.AreaObj.AddByPoint(4, ["1", "2", "3", "4"], "A1", "SH", "A1")
print("Elemento area creado")

# Empotrar nodos 1 y 4 (borde x=0)
SapModel.PointObj.SetRestraint("1", [True]*6, 0)
SapModel.PointObj.SetRestraint("4", [True]*6, 0)
print("Nodos 1 y 4 empotrados")

# Carga en nodo 3
# Usar el patron DEAD que ya existe
carga = [0.0, 0.0, -1.0, 0.0, 0.0, 0.0]
ret = SapModel.PointObj.SetLoadForce("3", "Dead", carga, 0, "Global")
print(f"Carga en nodo 3: Fz=-1 kN (ret={ret})")

# Ejecutar analisis
print("\n--- EJECUTANDO ANALISIS ---")
ret = SapModel.Analyze.RunAnalysis()
print(f"RunAnalysis ret={ret}")

# Ver si hay errores
locked = SapModel.GetModelIsLocked()
print(f"Modelo bloqueado (analizado): {locked}")

# Resultados
print("\n--- RESULTADOS ---")
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("Dead")

ret = SapModel.Results.JointDispl("", 2)
print(f"JointDispl retorno: {ret[0]} resultados")

if ret[0] > 0:
    nombres = list(ret[2])
    U3 = list(ret[9])
    R1 = list(ret[10])
    R2 = list(ret[11])

    print(f"\n{'Nodo':<6} {'U3 (m)':<14} {'R1 (rad)':<14} {'R2 (rad)':<14}")
    print("-"*50)
    for i in range(ret[0]):
        print(f"{nombres[i]:<6} {U3[i]:>13.6e} {R1[i]:>13.6e} {R2[i]:>13.6e}")
else:
    print("No hay resultados de desplazamiento")

    # Verificar si hay errores en el log
    print("\nVerificando log de errores...")

# Guardar
ruta = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_test.sdb"
SapModel.File.Save(ruta)
print(f"\nModelo guardado: {ruta}")

print("\nRevisa el modelo en SAP2000 para ver si hay errores.")
