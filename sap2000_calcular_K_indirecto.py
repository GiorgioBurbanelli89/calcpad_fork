# -*- coding: utf-8 -*-
"""
CALCULAR MATRIZ DE RIGIDEZ INDIRECTAMENTE - SAP2000
====================================================
Este script calcula la matriz de rigidez del elemento Q4 aplicando
cargas unitarias en cada GDL y midiendo los desplazamientos.

K * U = F  =>  K = F * U^(-1)

Aplicando F unitario en cada GDL, obtenemos cada columna de K^(-1)
Luego K = inv(K^(-1))
"""

import comtypes.client
import numpy as np
np.set_printoptions(precision=4, suppress=True, linewidth=150)

print("="*70)
print("CALCULO INDIRECTO DE MATRIZ DE RIGIDEZ - SAP2000")
print("="*70)

# ============================================================
# DATOS DEL PROBLEMA
# ============================================================
E = 2e7
nu = 0.30
t = 0.02
kappa = 5.0/6.0

# Nodos y coordenadas
nodos_coords = {
    "1": (0.0, -1.0, 0.0),
    "2": (1.0, -1.0, 0.0),
    "3": (1.0,  0.0, 0.0),
    "4": (0.0,  0.0, 0.0),
}

# GDL de interes para placa (w, theta_x, theta_y) = (U3, R1, R2)
# Total: 4 nodos x 3 GDL = 12 GDL
gdl_names = []
for nodo in ["1", "2", "3", "4"]:
    gdl_names.append(f"{nodo}_U3")   # desplazamiento Z
    gdl_names.append(f"{nodo}_R1")   # rotacion X
    gdl_names.append(f"{nodo}_R2")   # rotacion Y

n_gdl = len(gdl_names)
print(f"\nGDL del elemento ({n_gdl} total):")
for i, g in enumerate(gdl_names):
    print(f"  {i+1}: {g}")

# ============================================================
# CONECTAR A SAP2000
# ============================================================
print("\n--- CONECTANDO A SAP2000 ---")
try:
    mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
    SapModel = mySapObject.SapModel
    print(f"Conectado a SAP2000 {SapModel.GetVersion()[0]}")
except:
    print("ERROR: SAP2000 no esta abierto")
    exit(1)

# ============================================================
# CREAR MODELO NUEVO
# ============================================================
print("\n--- CREANDO MODELO ---")
SapModel.InitializeNewModel(6)  # kN, m, C
SapModel.File.NewBlank()

# Material
mat = "MAT"
SapModel.PropMaterial.SetMaterial(mat, 1)
G = E / (2 * (1 + nu))
SapModel.PropMaterial.SetMPIsotropic(mat, E, nu, 0.0, G)

# Seccion shell thick
shell = "SHELL"
SapModel.PropArea.SetShell_1(shell, 2, False, mat, 0.0, t, t, 0, "", "")

# Crear nodos
for nodo, (x, y, z) in nodos_coords.items():
    SapModel.PointObj.AddCartesian(x, y, z, nodo)

# Crear elemento area
SapModel.AreaObj.AddByPoint(4, ["1", "2", "3", "4"], "PLACA", shell, "PLACA")

# Restringir GDL de membrana (U1, U2, R3) en todos los nodos
for nodo in ["1", "2", "3", "4"]:
    # [U1, U2, U3, R1, R2, R3]
    # Dejar libres solo U3, R1, R2
    restr = [True, True, False, False, False, True]
    SapModel.PointObj.SetRestraint(nodo, restr, 0)

print("Modelo creado: E=2e7, nu=0.3, t=0.02")
print("Shell-Thick (Mindlin), GDL de membrana restringidos")

# ============================================================
# CALCULAR MATRIZ DE FLEXIBILIDAD (K^-1) VIA CARGAS UNITARIAS
# ============================================================
print("\n--- CALCULANDO MATRIZ DE FLEXIBILIDAD ---")
print("Aplicando cargas unitarias en cada GDL...")

# Matriz de flexibilidad (12x12)
F_matrix = np.zeros((n_gdl, n_gdl))

# Para cada GDL, aplicar carga unitaria y medir desplazamientos
for col, gdl in enumerate(gdl_names):
    # Crear patron de carga para este GDL
    patron = f"F_{gdl}"
    SapModel.LoadPatterns.Add(patron, 8)  # 8 = Other

    # Parsear el GDL
    nodo = gdl.split("_")[0]
    tipo = gdl.split("_")[1]

    # Crear vector de carga unitaria
    # [F1, F2, F3, M1, M2, M3]
    carga = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if tipo == "U3":
        carga[2] = 1.0  # Fuerza en Z
    elif tipo == "R1":
        carga[3] = 1.0  # Momento en X
    elif tipo == "R2":
        carga[4] = 1.0  # Momento en Y

    SapModel.PointObj.SetLoadForce(nodo, patron, carga, 0, "Global")

# Ejecutar analisis
print("Ejecutando analisis...")
SapModel.Analyze.RunAnalysis()

# Extraer resultados para cada patron de carga
for col, gdl in enumerate(gdl_names):
    patron = f"F_{gdl}"

    # Seleccionar caso de carga
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput(patron)

    # Obtener desplazamientos
    ret = SapModel.Results.JointDispl("", 2)
    num = ret[0]

    if num > 0:
        nombres = list(ret[2])
        U3_all = list(ret[9])
        R1_all = list(ret[10])
        R2_all = list(ret[11])

        # Llenar la columna de F_matrix
        for row, gdl_row in enumerate(gdl_names):
            nodo_row = gdl_row.split("_")[0]
            tipo_row = gdl_row.split("_")[1]

            # Buscar el nodo en los resultados
            if nodo_row in nombres:
                idx = nombres.index(nodo_row)
                if tipo_row == "U3":
                    F_matrix[row, col] = U3_all[idx]
                elif tipo_row == "R1":
                    F_matrix[row, col] = R1_all[idx]
                elif tipo_row == "R2":
                    F_matrix[row, col] = R2_all[idx]

print("Analisis completado.")

# ============================================================
# CALCULAR MATRIZ DE RIGIDEZ K = inv(F)
# ============================================================
print("\n--- MATRIZ DE FLEXIBILIDAD F (K^-1) ---")
print(F_matrix)

print("\n--- CALCULANDO MATRIZ DE RIGIDEZ K ---")
try:
    K_matrix = np.linalg.inv(F_matrix)
    print("K = inv(F)")
except np.linalg.LinAlgError:
    print("ERROR: Matriz singular, no se puede invertir")
    print("Esto indica que el sistema no tiene restricciones suficientes")
    K_matrix = None

if K_matrix is not None:
    print("\n--- MATRIZ DE RIGIDEZ K (12x12) ---")
    print(K_matrix)

    # Comparar con valores de Calcpad/PDF
    print("\n" + "="*70)
    print("COMPARACION CON CALCPAD/PDF")
    print("="*70)

    print("\nValores del PDF (Ing. Pompilla Yabar):")
    print("  K_b(2,2) = 6.593")
    print("  K_s(1,1) x10^3 = 64.103")
    print("  K_T(2,2) x10^3 = 8.019")

    print("\nValores de SAP2000 (indices 0-based):")
    print(f"  K(1,1) = {K_matrix[0,0]:.3f} (1_U3, 1_U3)")
    print(f"  K(1,2) = {K_matrix[0,1]:.3f} (1_U3, 1_R1)")
    print(f"  K(2,2) = {K_matrix[1,1]:.3f} (1_R1, 1_R1)")

    # K_b(2,2) en el PDF corresponde a theta_x del nodo 1, que es R1
    # Pero el PDF usa indices diferentes...

    print("\nNOTA: Los indices del PDF y SAP2000 pueden diferir")
    print("El PDF ordena los GDL como: [w1, theta_x1, theta_y1, w2, ...]")
    print("SAP2000 ordena igual pero la numeracion empieza en 0")

    # Mostrar elementos diagonales
    print("\nElementos diagonales de K:")
    for i in range(n_gdl):
        print(f"  K({i+1},{i+1}) = {K_matrix[i,i]:.3f} ({gdl_names[i]})")

    # Mostrar K en forma de submatrices 3x3 por nodo
    print("\n--- SUBMATRICES POR NODO ---")
    for i in range(4):
        for j in range(4):
            print(f"\nK_{i+1}{j+1} (nodo {i+1} - nodo {j+1}):")
            K_sub = K_matrix[i*3:(i+1)*3, j*3:(j+1)*3]
            print(K_sub)

# Guardar modelo
print("\n--- GUARDANDO MODELO ---")
ruta = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_K_indirecto.sdb"
SapModel.File.Save(ruta)
print(f"Guardado: {ruta}")

print("\n" + "="*70)
print("SCRIPT COMPLETADO")
print("="*70)
