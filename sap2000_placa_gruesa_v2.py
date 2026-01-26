# -*- coding: utf-8 -*-
"""
COMPARACION PLACA GRUESA Q4 - CALCPAD VS SAP2000 (Version 2)
============================================================
Crea un modelo de placa empotrada en un borde y extrae resultados
para comparar con Calcpad.

Configuracion:
- Placa Q4 de 1x1 m
- Empotrada en nodos 1 y 4 (borde izquierdo)
- Carga puntual en nodo 3
"""

import comtypes.client
import numpy as np

print("="*60)
print("COMPARACION PLACA GRUESA Q4 - CALCPAD VS SAP2000")
print("="*60)

# ============================================================
# 1. DATOS DEL EJEMPLO (del PDF Ing. Pompilla Yabar)
# ============================================================
E = 2e7          # Modulo de elasticidad
nu = 0.30        # Coeficiente de Poisson
t = 0.02         # Espesor de la placa
kappa = 5.0/6.0  # Factor de correccion por corte

# Coordenadas de los nodos (sentido antihorario)
nodos = {
    1: (0.0, -1.0, 0.0),   # Nodo 1
    2: (1.0, -1.0, 0.0),   # Nodo 2
    3: (1.0,  0.0, 0.0),   # Nodo 3
    4: (0.0,  0.0, 0.0),   # Nodo 4
}

print("\n--- DATOS DE ENTRADA ---")
print(f"E = {E:.2e}")
print(f"nu = {nu}")
print(f"t = {t}")
print(f"kappa = {kappa:.6f}")
print("\nCoordenadas de nodos:")
for n, (x, y, z) in nodos.items():
    print(f"  Nodo {n}: ({x}, {y}, {z})")

# Valores esperados de Calcpad/PDF
print("\n--- VALORES ESPERADOS (PDF Pompilla) ---")
print("  K_b(2,2) = 6.593")
print("  K_s(1,1)x10^3 = 64.103")
print("  K_T(2,2)x10^3 = 8.019")

# ============================================================
# 2. CONECTAR A SAP2000
# ============================================================
print("\n--- CONECTANDO A SAP2000 ---")
try:
    mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
    SapModel = mySapObject.SapModel
    print("Conexion exitosa!")
    version = SapModel.GetVersion()
    print(f"SAP2000 version: {version[0]}")
except Exception as e:
    print(f"ERROR: No se pudo conectar a SAP2000: {e}")
    exit(1)

# ============================================================
# 3. CREAR NUEVO MODELO
# ============================================================
print("\n--- CREANDO MODELO ---")
ret = SapModel.InitializeNewModel(6)  # 6 = kN_m_C
ret = SapModel.File.NewBlank()
print("Modelo nuevo creado (unidades: kN, m, C)")

# ============================================================
# 4. DEFINIR MATERIAL
# ============================================================
print("\n--- DEFINIENDO MATERIAL ---")
mat_name = "MAT_PLACA"
ret = SapModel.PropMaterial.SetMaterial(mat_name, 1)
G = E / (2 * (1 + nu))
ret = SapModel.PropMaterial.SetMPIsotropic(mat_name, E, nu, 0.0, G)
print(f"Material: E={E:.2e}, nu={nu}, G={G:.2e}")

# ============================================================
# 5. DEFINIR SECCION SHELL-THICK (MINDLIN)
# ============================================================
print("\n--- DEFINIENDO SECCION SHELL ---")
shell_name = "SHELL_THICK"

# SetShell_1: ShellType=2 es Shell-Thick (Mindlin)
ret = SapModel.PropArea.SetShell_1(
    shell_name, 2, False, mat_name, 0.0, t, t, 0, "", ""
)
print(f"Seccion: {shell_name} (Shell-Thick/Mindlin, t={t})")

# ============================================================
# 6. CREAR NODOS
# ============================================================
print("\n--- CREANDO NODOS ---")
for nodo_id, (x, y, z) in nodos.items():
    ret = SapModel.PointObj.AddCartesian(x, y, z, str(nodo_id))
    print(f"  Nodo {nodo_id}: ({x}, {y}, {z})")

# ============================================================
# 7. CREAR ELEMENTO AREA Q4
# ============================================================
print("\n--- CREANDO ELEMENTO AREA Q4 ---")
area_name = "PLACA1"
nodos_lista = ["1", "2", "3", "4"]
ret = SapModel.AreaObj.AddByPoint(4, nodos_lista, area_name, shell_name, area_name)
print(f"Elemento: {area_name} con nodos {nodos_lista}")

# ============================================================
# 8. APLICAR RESTRICCIONES - EMPOTRAR BORDE IZQUIERDO
# ============================================================
print("\n--- APLICANDO RESTRICCIONES ---")
# Empotrar nodos 1 y 4 (borde izquierdo x=0)
# [U1, U2, U3, R1, R2, R3]
empotre = [True, True, True, True, True, True]
for nodo in ["1", "4"]:
    ret = SapModel.PointObj.SetRestraint(nodo, empotre, 0)
    print(f"  Nodo {nodo}: Empotrado")

# Nodos 2 y 3 libres para flexion
libre = [True, True, False, False, False, True]  # Solo U3, R1, R2 libres
for nodo in ["2", "3"]:
    ret = SapModel.PointObj.SetRestraint(nodo, libre, 0)
    print(f"  Nodo {nodo}: U3, R1, R2 libres")

# ============================================================
# 9. CREAR PATRON Y CASO DE CARGA
# ============================================================
print("\n--- CREANDO CASO DE CARGA ---")

# Crear patron de carga
ret = SapModel.LoadPatterns.Add("CARGA", 1)

# Aplicar carga puntual en nodo 3: Fz = -1 kN
carga = [0.0, 0.0, -1.0, 0.0, 0.0, 0.0]
ret = SapModel.PointObj.SetLoadForce("3", "CARGA", carga, 0, "Global")
print("Carga puntual en nodo 3: Fz = -1 kN")

# ============================================================
# 10. EJECUTAR ANALISIS
# ============================================================
print("\n--- EJECUTANDO ANALISIS ---")

# Configurar opciones de analisis - usar DEAD que se crea por defecto
# y agregar la carga al patron DEAD
carga2 = [0.0, 0.0, -1.0, 0.0, 0.0, 0.0]
ret = SapModel.PointObj.SetLoadForce("3", "Dead", carga2, 0, "Global")

ret = SapModel.Analyze.RunAnalysis()
if ret == 0:
    print("Analisis completado exitosamente!")
else:
    print(f"Codigo de retorno: {ret}")

# ============================================================
# 11. EXTRAER RESULTADOS
# ============================================================
print("\n--- EXTRAYENDO RESULTADOS ---")

# Configurar caso para salida
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput("Dead")

# Desplazamientos nodales
print("\nDesplazamientos nodales:")
ret = SapModel.Results.JointDispl("", 2)
num_results = ret[0]

if num_results > 0:
    nombres = ret[2]
    U3_list = ret[9]   # Desplazamiento Z
    R1_list = ret[10]  # Rotacion X
    R2_list = ret[11]  # Rotacion Y

    print(f"{'Nodo':<6} {'U3 (m)':<14} {'R1 (rad)':<14} {'R2 (rad)':<14}")
    print("-" * 50)
    for i in range(num_results):
        print(f"{nombres[i]:<6} {U3_list[i]:>13.6e} {R1_list[i]:>13.6e} {R2_list[i]:>13.6e}")

    # Calcular rigidez efectiva
    # Para una carga F=-1kN en nodo 3, K = F/U3
    idx_3 = list(nombres).index("3") if "3" in nombres else -1
    if idx_3 >= 0:
        U3_nodo3 = U3_list[idx_3]
        if abs(U3_nodo3) > 1e-20:
            K_eff = -1.0 / U3_nodo3
            print(f"\nRigidez efectiva en nodo 3: K_eff = F/U3 = {K_eff:.2f} kN/m")
else:
    print("No hay resultados de desplazamiento")

# Fuerzas en el elemento
print("\nFuerzas/Momentos en el elemento:")
ret = SapModel.Results.AreaForceShell(area_name, 0)
num_results = ret[0]

if num_results > 0:
    print(f"Puntos de salida: {num_results}")
    M11 = list(ret[14])
    M22 = list(ret[15])
    M12 = list(ret[16])

    print(f"\nMomentos (kN-m/m):")
    print(f"  M11 max: {max(M11):.6f}, min: {min(M11):.6f}")
    print(f"  M22 max: {max(M22):.6f}, min: {min(M22):.6f}")
    print(f"  M12 max: {max(M12):.6f}, min: {min(M12):.6f}")

# ============================================================
# 12. COMPARACION TEORICA
# ============================================================
print("\n" + "="*60)
print("COMPARACION TEORICA")
print("="*60)

# Rigidez a flexion
D = E * t**3 / (12 * (1 - nu**2))
print(f"\nRigidez a flexion D = E*t^3/(12*(1-nu^2))")
print(f"D = {E:.2e} * {t}^3 / (12 * (1 - {nu}^2))")
print(f"D = {D:.6f}")

# Coeficiente de corte
Gs = kappa * G * t
print(f"\nRigidez a corte Gs = kappa * G * t")
print(f"Gs = {kappa:.6f} * {G:.2e} * {t}")
print(f"Gs = {Gs:.6f}")

# Comparacion con valores del PDF
print("\n--- VALORES DEL PDF (Ing. Pompilla Yabar) ---")
print("K_b(2,2) = 6.593 (matriz de rigidez a flexion)")
print("K_s(1,1)x10^3 = 64.103 (matriz de rigidez a corte)")
print("K_T(2,2)x10^3 = 8.019 (matriz de rigidez total)")

print("\n--- VERIFICACION ---")
print("Los valores K_b, K_s, K_T del PDF son para un elemento AISLADO")
print("(sin condiciones de borde aplicadas).")
print("")
print("SAP2000 calcula la matriz ensamblada del sistema completo.")
print("Para comparar directamente:")
print("  1. Display > Show Tables > Analysis > Element Stiffness")
print("  2. Exportar a Excel y comparar elemento por elemento")

# ============================================================
# 13. GUARDAR MODELO
# ============================================================
print("\n--- GUARDANDO MODELO ---")
ruta_modelo = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Placa_Gruesa_Q4.sdb"
ret = SapModel.File.Save(ruta_modelo)
print(f"Modelo guardado: {ruta_modelo}")

# ============================================================
# 14. EXTRAER MATRIZ DE RIGIDEZ VIA TABLAS
# ============================================================
print("\n" + "="*60)
print("EXTRACCION DE MATRIZ DE RIGIDEZ")
print("="*60)

try:
    # Intentar obtener la matriz de rigidez del elemento
    # GetStiffness(Name, StiffnessType, K, Location, ItemTypeElm)
    # StiffnessType: 1=Original, 2=Modified
    print("\nIntentando extraer matriz de rigidez del elemento...")

    # Metodo alternativo: usar tablas de base de datos
    print("\nExtrayendo via tablas de base de datos...")

    # Obtener lista de tablas disponibles
    ret = SapModel.DatabaseTables.GetAvailableTables()
    tablas = list(ret[1]) if ret[0] > 0 else []

    # Buscar tablas de rigidez
    tablas_rigidez = [t for t in tablas if 'stiff' in t.lower()]
    if tablas_rigidez:
        print(f"Tablas de rigidez encontradas: {tablas_rigidez[:5]}")

    # Intentar obtener "Element Forces - Area Shells"
    tabla = "Element Forces - Area Shells"
    if tabla in tablas:
        print(f"\nObteniendo tabla: {tabla}")
        ret = SapModel.DatabaseTables.GetTableForDisplayArray(tabla, "", "")
        if ret[0] == 0:
            headers = ret[2]
            data = ret[4]
            print(f"Columnas: {headers[:8]}...")
            print(f"Filas de datos: {len(data)//len(headers) if headers else 0}")

except Exception as e:
    print(f"Error al extraer matriz: {e}")

print("\n" + "="*60)
print("SCRIPT COMPLETADO")
print("="*60)
print("""
El modelo SAP2000 esta listo para inspeccion manual.

Para ver la matriz de rigidez del elemento:
1. Display > Show Tables
2. Seleccionar: Analysis Results > Element Stiffness Matrices
3. Comparar con valores de Calcpad

Nota: SAP2000 usa la formulacion Shell-Thick (Mindlin) que es
equivalente a la teoria de Reissner-Mindlin del ejemplo.
""")
