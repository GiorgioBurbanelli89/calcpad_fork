# -*- coding: utf-8 -*-
"""
COMPARACION PLACA GRUESA Q4 - CALCPAD VS SAP2000
=================================================
Este script crea un modelo en SAP2000 con el mismo elemento Q4 del ejemplo
de Ing. Pompilla Yabar y extrae la matriz de rigidez para comparacion.

Datos del ejemplo:
- E = 2e7
- nu = 0.30
- t = 0.02
- Nodos: (0,-1), (1,-1), (1,0), (0,0)
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
    1: (0.0, -1.0, 0.0),   # Nodo 1: (x, y, z)
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

# ============================================================
# 2. VALORES ESPERADOS DE CALCPAD/PDF
# ============================================================
print("\n--- VALORES ESPERADOS (PDF Pompilla) ---")
calcpad_values = {
    'K_b(2,2)': 6.593,
    'K_b(2,3)': 2.381,
    'K_s(1,1)x10^3': 64.103,
    'K_T(1,1)x10^3': 64.103,
    'K_T(2,2)x10^3': 8.019,
}
for key, val in calcpad_values.items():
    print(f"  {key} = {val}")

# ============================================================
# 3. CONECTAR A SAP2000
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
    print("Asegurese de que SAP2000 este abierto.")
    exit(1)

# ============================================================
# 4. CREAR NUEVO MODELO
# ============================================================
print("\n--- CREANDO MODELO ---")

# Iniciar nuevo modelo (unidades: kN, m, C)
ret = SapModel.InitializeNewModel(6)  # 6 = kN_m_C
if ret != 0:
    print("Advertencia: InitializeNewModel retorno", ret)

# Crear modelo en blanco
ret = SapModel.File.NewBlank()
if ret != 0:
    print("Advertencia: NewBlank retorno", ret)

print("Modelo nuevo creado.")

# ============================================================
# 5. DEFINIR MATERIAL
# ============================================================
print("\n--- DEFINIENDO MATERIAL ---")
mat_name = "MAT_PLACA"

# Agregar material isotropo
ret = SapModel.PropMaterial.SetMaterial(mat_name, 1)  # 1 = Isotropic
print(f"Material creado: {mat_name}")

# Definir propiedades del material
# SetMPIsotropic(Name, E, Poisson, CTE, G)
G = E / (2 * (1 + nu))
ret = SapModel.PropMaterial.SetMPIsotropic(mat_name, E, nu, 0.0, G)
print(f"  E = {E:.2e}")
print(f"  nu = {nu}")
print(f"  G = {G:.2e}")

# ============================================================
# 6. DEFINIR SECCION DE AREA (SHELL-THICK)
# ============================================================
print("\n--- DEFINIENDO SECCION SHELL ---")
shell_name = "SHELL_THICK"

# Crear seccion shell tipo Thick (Mindlin-Reissner)
# SetShell_1(Name, ShellType, MatProp, Thickness, MatAng, ...)
# ShellType: 1=Shell-Thin, 2=Shell-Thick, 3=Membrane, 4=Plate-Thin, 5=Plate-Thick
ret = SapModel.PropArea.SetShell_1(
    shell_name,      # Name
    2,               # ShellType = 2 (Shell-Thick = Mindlin)
    False,           # IncludeDrillingDOF
    mat_name,        # MatProp
    0.0,             # MatAng
    t,               # MemThick
    t,               # BendThick
    0,               # Color
    "",              # Notes
    ""               # GUID
)
print(f"Seccion creada: {shell_name}")
print(f"  Tipo: Shell-Thick (Mindlin)")
print(f"  Espesor: {t}")

# ============================================================
# 7. CREAR NODOS (JOINTS)
# ============================================================
print("\n--- CREANDO NODOS ---")
for nodo_id, (x, y, z) in nodos.items():
    nombre = str(nodo_id)
    ret = SapModel.PointObj.AddCartesian(x, y, z, nombre)
    print(f"  Nodo {nombre}: ({x}, {y}, {z})")

# ============================================================
# 8. CREAR ELEMENTO AREA (Q4)
# ============================================================
print("\n--- CREANDO ELEMENTO AREA Q4 ---")
area_name = "PLACA1"

# Lista de nodos en orden (antihorario visto desde +Z)
nodos_lista = ["1", "2", "3", "4"]
num_puntos = 4

# AddByPoint(NumPoints, Point, Name, PropName, UserName)
ret = SapModel.AreaObj.AddByPoint(
    num_puntos,
    nodos_lista,
    area_name,
    shell_name,
    area_name
)
print(f"Elemento area creado: {area_name}")
print(f"  Nodos: {nodos_lista}")
print(f"  Seccion: {shell_name}")

# ============================================================
# 9. APLICAR RESTRICCIONES
# ============================================================
print("\n--- APLICANDO RESTRICCIONES ---")
# Para extraer la matriz de rigidez completa, no aplicamos restricciones
# Los GDL del elemento son: U3, R1, R2 (w, theta_x, theta_y) para cada nodo
# SAP2000 usa 6 GDL por nodo: U1, U2, U3, R1, R2, R3

# Restringir GDL de membrana (U1, U2, R3) ya que solo nos interesa flexion
for nodo_id in nodos.keys():
    nombre = str(nodo_id)
    # SetRestraint(Name, Value, ItemType)
    # Value es array booleano [U1, U2, U3, R1, R2, R3]
    restricciones = [True, True, False, False, False, True]  # Solo U3, R1, R2 libres
    ret = SapModel.PointObj.SetRestraint(nombre, restricciones, 0)
print("GDL de membrana restringidos (U1, U2, R3)")
print("GDL de flexion libres (U3, R1, R2)")

# ============================================================
# 10. CREAR CASO DE CARGA ESTATICO
# ============================================================
print("\n--- CREANDO CASO DE CARGA ---")
caso = "CARGA_PUNTUAL"

# Crear patron de carga
ret = SapModel.LoadPatterns.Add("PUNTUAL", 1)  # 1 = Dead
print("Patron de carga creado: PUNTUAL")

# Crear caso de analisis estatico
ret = SapModel.LoadCases.StaticLinear.SetCase(caso)
print(f"Caso de carga creado: {caso}")

# Aplicar carga puntual en nodo 3 (para verificar respuesta)
# SetLoadForce(Name, LoadPat, Value, ItemType, Replace, CSys)
# Value es [F1, F2, F3, M1, M2, M3]
carga = [0.0, 0.0, -1.0, 0.0, 0.0, 0.0]  # Fz = -1 kN
ret = SapModel.PointObj.SetLoadForce("3", "PUNTUAL", carga, 0, "Global")
print("Carga puntual aplicada en nodo 3: Fz = -1 kN")

# ============================================================
# 11. EJECUTAR ANALISIS
# ============================================================
print("\n--- EJECUTANDO ANALISIS ---")
ret = SapModel.Analyze.RunAnalysis()
if ret == 0:
    print("Analisis completado exitosamente!")
else:
    print(f"Advertencia: Analisis retorno codigo {ret}")

# ============================================================
# 12. EXTRAER RESULTADOS
# ============================================================
print("\n--- EXTRAYENDO RESULTADOS ---")

# Configurar salida de resultados
SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
SapModel.Results.Setup.SetCaseSelectedForOutput(caso)

# Extraer desplazamientos
print("\nDesplazamientos nodales:")
ret = SapModel.Results.JointDispl("", 2)  # 2 = todos los nodos
num_results = ret[0]
if num_results > 0:
    nombres = ret[2]
    U3 = ret[9]   # Desplazamiento Z
    R1 = ret[10]  # Rotacion X
    R2 = ret[11]  # Rotacion Y

    print(f"{'Nodo':<6} {'U3 (w)':<15} {'R1 (theta_x)':<15} {'R2 (theta_y)':<15}")
    print("-" * 55)
    for i in range(num_results):
        print(f"{nombres[i]:<6} {U3[i]:>14.6e} {R1[i]:>14.6e} {R2[i]:>14.6e}")
else:
    print("No se encontraron resultados de desplazamiento")

# Extraer fuerzas en el area
print("\nFuerzas/Momentos en el elemento:")
ret = SapModel.Results.AreaForceShell(area_name, 0)
num_results = ret[0]
if num_results > 0:
    print(f"Numero de puntos de salida: {num_results}")
    M11 = ret[14]
    M22 = ret[15]
    M12 = ret[16]
    print(f"\nMomentos promedio:")
    print(f"  M11 = {np.mean(M11):.6f}")
    print(f"  M22 = {np.mean(M22):.6f}")
    print(f"  M12 = {np.mean(M12):.6f}")

# ============================================================
# 13. COMPARACION CON CALCPAD
# ============================================================
print("\n" + "="*60)
print("COMPARACION DE RESULTADOS")
print("="*60)

print("""
NOTA IMPORTANTE:
================
SAP2000 no expone directamente la matriz de rigidez del elemento.
La comparacion directa de K_b, K_s, K_T no es posible mediante la API.

Sin embargo, podemos verificar indirectamente:
1. Que SAP2000 use la formulacion Mindlin (Shell-Thick)
2. Que los desplazamientos bajo cargas conocidas coincidan

Para una comparacion directa de matrices de rigidez:
- Usar SAP2000 Menu: Display > Show Tables > Analysis > Assembled Joint Stiffness
- O exportar el modelo a formato CSI y analizar el archivo
""")

# Calcular rigidez a flexion teorica
D = E * t**3 / (12 * (1 - nu**2))
print(f"\nRigidez a flexion D = E*t^3/(12*(1-nu^2)) = {D:.6f}")

# Area del elemento
A = 1.0 * 1.0  # Elemento de 1x1 m
print(f"Area del elemento = {A} m^2")

# Rigidez teorica simplificada (placa rectangular uniforme)
K_approx = D * A / (t**2)
print(f"Rigidez aproximada K aprox {K_approx:.2f}")

print("\n--- VALORES DEL PDF (Ing. Pompilla Yabar) ---")
print(f"K_b(2,2) = 6.593")
print(f"K_s(1,1)x10^3 = 64.103")
print(f"K_T(2,2)x10^3 = 8.019")

print("\n--- VERIFICACION ---")
print("El modelo SAP2000 esta configurado con:")
print(f"  - Material: E={E:.2e}, nu={nu}")
print(f"  - Seccion Shell-Thick (Mindlin): t={t}")
print(f"  - Elemento Q4 con nodos en posiciones correctas")
print("  - Integracion tipo Mindlin-Reissner para corte")

# ============================================================
# 14. GUARDAR MODELO
# ============================================================
print("\n--- GUARDANDO MODELO ---")
ruta_modelo = r"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_Placa_Gruesa_Q4.sdb"
ret = SapModel.File.Save(ruta_modelo)
if ret == 0:
    print(f"Modelo guardado en: {ruta_modelo}")
else:
    print(f"Advertencia al guardar: codigo {ret}")

print("\n" + "="*60)
print("SCRIPT COMPLETADO")
print("="*60)
print("""
Proximos pasos para comparacion manual:
1. En SAP2000: Display > Show Tables > Analysis > Assembled Joint Stiffness
2. Exportar la matriz de rigidez ensamblada
3. Comparar con los valores de Calcpad
""")
