# -*- coding: utf-8 -*-
"""
PLACA GRUESA Q4 EN SAP2000 - COMPARACION CON CALCPAD
=====================================================
Modelo: Placa Q4 con 4 nodos
Condiciones: Nodo 1 empotrado, resto libre para flexion
Carga: Fuerza unitaria en nodo 3
"""

import comtypes.client
import numpy as np
np.set_printoptions(precision=6, suppress=True, linewidth=150)

print("="*70)
print("PLACA GRUESA Q4 - COMPARACION SAP2000 vs CALCPAD")
print("="*70)

# Datos del problema
E = 2e7
nu = 0.30
t = 0.02
kappa = 5.0/6.0
G = E / (2 * (1 + nu))

print("\n--- DATOS DEL PROBLEMA ---")
print(f"E = {E:.2e}")
print(f"nu = {nu}")
print(f"t = {t}")
print(f"G = {G:.2e}")
print(f"kappa = {kappa:.6f}")

# Coordenadas de nodos
nodos = {
    "1": (0.0, -1.0, 0.0),
    "2": (1.0, -1.0, 0.0),
    "3": (1.0,  0.0, 0.0),
    "4": (0.0,  0.0, 0.0),
}

print("\nNodos:")
for n, (x, y, z) in nodos.items():
    print(f"  {n}: ({x}, {y}, {z})")

# Valores esperados de Calcpad
print("\n--- VALORES CALCPAD/PDF ---")
print("K_b(2,2) = 6.593")
print("K_s(1,1) x10^3 = 64.103  => K_s(1,1) = 64103")
print("K_T(2,2) x10^3 = 8.019   => K_T(2,2) = 8019")

# Conectar a SAP2000
print("\n--- CONECTANDO A SAP2000 ---")
try:
    mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
    SapModel = mySapObject.SapModel
    print(f"SAP2000 {SapModel.GetVersion()[0]} conectado")
except:
    print("ERROR: SAP2000 no disponible")
    exit(1)

# Crear modelo
print("\n--- CREANDO MODELO ---")
SapModel.InitializeNewModel(6)  # kN, m, C
SapModel.File.NewBlank()

# Material
mat = "MAT"
SapModel.PropMaterial.SetMaterial(mat, 1)
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0, G)
print(f"Material: E={E:.2e}, nu={nu}")

# Seccion shell thick (Mindlin)
shell = "THICK"
SapModel.PropArea.SetShell_1(shell, 2, False, mat, 0.0, t, t, 0, "", "")
print(f"Seccion: Shell-Thick t={t}")

# Crear nodos
for n, (x, y, z) in nodos.items():
    SapModel.PointObj.AddCartesian(x, y, z, n)
print("Nodos creados")

# Crear elemento
SapModel.AreaObj.AddByPoint(4, ["1", "2", "3", "4"], "P1", shell, "P1")
print("Elemento area Q4 creado")

# Restricciones: empotrar nodo 1, liberar flexion en resto
# SAP2000: [U1, U2, U3, R1, R2, R3]
print("\n--- RESTRICCIONES ---")

# Nodo 1: completamente empotrado
SapModel.PointObj.SetRestraint("1", [True, True, True, True, True, True], 0)
print("Nodo 1: Empotrado total")

# Nodos 2, 3, 4: solo U3, R1, R2 libres (restringir U1, U2, R3)
for n in ["2", "3", "4"]:
    SapModel.PointObj.SetRestraint(n, [True, True, False, False, False, True], 0)
print("Nodos 2,3,4: U3, R1, R2 libres")

# Crear casos de carga con fuerzas unitarias
print("\n--- CASOS DE CARGA ---")

# Caso 1: Fuerza en Z nodo 2
SapModel.LoadPatterns.Add("F2_Z", 8)
SapModel.PointObj.SetLoadForce("2", "F2_Z", [0,0,1,0,0,0], 0, "Global")
print("F2_Z: Fz=1 en nodo 2")

# Caso 2: Momento en X nodo 2
SapModel.LoadPatterns.Add("M2_X", 8)
SapModel.PointObj.SetLoadForce("2", "M2_X", [0,0,0,1,0,0], 0, "Global")
print("M2_X: Mx=1 en nodo 2")

# Caso 3: Momento en Y nodo 2
SapModel.LoadPatterns.Add("M2_Y", 8)
SapModel.PointObj.SetLoadForce("2", "M2_Y", [0,0,0,0,1,0], 0, "Global")
print("M2_Y: My=1 en nodo 2")

# Caso 4: Fuerza en Z nodo 3
SapModel.LoadPatterns.Add("F3_Z", 8)
SapModel.PointObj.SetLoadForce("3", "F3_Z", [0,0,1,0,0,0], 0, "Global")
print("F3_Z: Fz=1 en nodo 3")

# Caso 5: Momento en X nodo 3
SapModel.LoadPatterns.Add("M3_X", 8)
SapModel.PointObj.SetLoadForce("3", "M3_X", [0,0,0,1,0,0], 0, "Global")
print("M3_X: Mx=1 en nodo 3")

# Caso 6: Momento en Y nodo 3
SapModel.LoadPatterns.Add("M3_Y", 8)
SapModel.PointObj.SetLoadForce("3", "M3_Y", [0,0,0,0,1,0], 0, "Global")
print("M3_Y: My=1 en nodo 3")

# Caso 7: Fuerza en Z nodo 4
SapModel.LoadPatterns.Add("F4_Z", 8)
SapModel.PointObj.SetLoadForce("4", "F4_Z", [0,0,1,0,0,0], 0, "Global")
print("F4_Z: Fz=1 en nodo 4")

# Caso 8: Momento en X nodo 4
SapModel.LoadPatterns.Add("M4_X", 8)
SapModel.PointObj.SetLoadForce("4", "M4_X", [0,0,0,1,0,0], 0, "Global")
print("M4_X: Mx=1 en nodo 4")

# Caso 9: Momento en Y nodo 4
SapModel.LoadPatterns.Add("M4_Y", 8)
SapModel.PointObj.SetLoadForce("4", "M4_Y", [0,0,0,0,1,0], 0, "Global")
print("M4_Y: My=1 en nodo 4")

# Ejecutar analisis
print("\n--- EJECUTANDO ANALISIS ---")
ret = SapModel.Analyze.RunAnalysis()
print(f"Codigo de retorno: {ret}")

# GDL libres: 9 (3 nodos x 3 GDL cada uno)
gdl_labels = ["2_U3", "2_R1", "2_R2", "3_U3", "3_R1", "3_R2", "4_U3", "4_R1", "4_R2"]
casos = ["F2_Z", "M2_X", "M2_Y", "F3_Z", "M3_X", "M3_Y", "F4_Z", "M4_X", "M4_Y"]
n_gdl = 9

# Matriz de flexibilidad (9x9)
F = np.zeros((n_gdl, n_gdl))

print("\n--- EXTRAYENDO RESULTADOS ---")
for col, caso in enumerate(casos):
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput(caso)

    ret = SapModel.Results.JointDispl("", 2)
    num = ret[0]

    if num > 0:
        nombres = list(ret[2])
        U3 = list(ret[9])
        R1 = list(ret[10])
        R2 = list(ret[11])

        for row, gdl in enumerate(gdl_labels):
            nodo = gdl.split("_")[0]
            tipo = gdl.split("_")[1]

            if nodo in nombres:
                idx = nombres.index(nodo)
                if tipo == "U3":
                    F[row, col] = U3[idx]
                elif tipo == "R1":
                    F[row, col] = R1[idx]
                elif tipo == "R2":
                    F[row, col] = R2[idx]

print("\n--- MATRIZ DE FLEXIBILIDAD F (9x9) ---")
print("GDL: 2_U3, 2_R1, 2_R2, 3_U3, 3_R1, 3_R2, 4_U3, 4_R1, 4_R2")
print(F)

# Calcular matriz de rigidez
print("\n--- MATRIZ DE RIGIDEZ K = inv(F) ---")
try:
    K = np.linalg.inv(F)
    print(K)

    # Comparar con valores de Calcpad
    print("\n" + "="*70)
    print("COMPARACION CON CALCPAD/PDF")
    print("="*70)

    print("\n--- VALORES DEL PDF (Ing. Pompilla Yabar) ---")
    print("Nota: El PDF muestra la matriz K completa (12x12) sin restricciones")
    print("SAP2000 nos da la matriz reducida (9x9) con nodo 1 empotrado")
    print("")
    print("Valores de referencia del PDF:")
    print("  K_b(2,2) = 6.593")
    print("  K_s(1,1) x 1000 = 64.103")
    print("  K_T(2,2) x 1000 = 8.019")

    print("\n--- ELEMENTOS DIAGONALES DE K (SAP2000) ---")
    for i, gdl in enumerate(gdl_labels):
        print(f"  K({gdl},{gdl}) = {K[i,i]:.3f}")

    # Guardar K a archivo
    print("\n--- GUARDANDO MATRIZ K ---")
    np.savetxt(r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\K_SAP2000_9x9.txt", K, fmt="%.6f")
    print("Matriz guardada en K_SAP2000_9x9.txt")

except np.linalg.LinAlgError:
    print("ERROR: Matriz singular")

# Guardar modelo
print("\n--- GUARDANDO MODELO ---")
ruta = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Placa_Q4_Empotrada.sdb"
SapModel.File.Save(ruta)
print(f"Modelo: {ruta}")

print("\n" + "="*70)
print("SCRIPT COMPLETADO")
print("="*70)
