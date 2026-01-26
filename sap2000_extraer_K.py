# -*- coding: utf-8 -*-
"""
EXTRAER MATRIZ DE RIGIDEZ DE SAP2000
====================================
Este script extrae la matriz de rigidez del elemento area del modelo actual.
"""

import comtypes.client
import numpy as np

print("="*60)
print("EXTRACCION DE MATRIZ DE RIGIDEZ - SAP2000")
print("="*60)

# Conectar a SAP2000
print("\n--- CONECTANDO A SAP2000 ---")
try:
    mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
    SapModel = mySapObject.SapModel
    print("Conexion exitosa!")
    print(f"SAP2000 version: {SapModel.GetVersion()[0]}")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

# Obtener informacion del modelo
print("\n--- INFORMACION DEL MODELO ---")
n_joints = SapModel.PointObj.Count()
n_areas = SapModel.AreaObj.Count()
n_frames = SapModel.FrameObj.Count()
print(f"Nodos: {n_joints}")
print(f"Areas: {n_areas}")
print(f"Frames: {n_frames}")

# Listar areas
print("\n--- ELEMENTOS AREA ---")
ret = SapModel.AreaObj.GetNameList()
if ret[0] > 0:
    areas = list(ret[1])
    print(f"Areas: {areas}")

    for area in areas:
        # Obtener nodos del area
        ret = SapModel.AreaObj.GetPoints(area)
        nodos = list(ret[1])
        print(f"\n  {area}: nodos = {nodos}")

        # Obtener seccion
        ret = SapModel.AreaObj.GetProperty(area)
        seccion = ret[0]
        print(f"  Seccion: {seccion}")

# Obtener tablas disponibles
print("\n--- TABLAS DISPONIBLES (rigidez) ---")
try:
    ret = SapModel.DatabaseTables.GetAvailableTables()
    tablas = list(ret[1]) if ret[0] > 0 else []

    # Filtrar tablas relacionadas con rigidez
    for t in tablas:
        if 'stiff' in t.lower() or 'matrix' in t.lower():
            print(f"  {t}")
except Exception as e:
    print(f"Error: {e}")

# Intentar extraer matriz de rigidez ensamblada
print("\n--- MATRIZ DE RIGIDEZ ENSAMBLADA ---")
try:
    # La tabla "Assembled Joint Mass" y "Assembled Joint Stiffness"
    # contienen informacion de rigidez
    tabla = "Assembled Joint Stiffnesses"

    ret = SapModel.DatabaseTables.GetTableForDisplayArray(tabla, "", "")
    if ret[0] == 0:
        headers = list(ret[2])
        num_cols = len(headers)
        data = list(ret[4])
        num_rows = len(data) // num_cols if num_cols > 0 else 0

        print(f"Tabla: {tabla}")
        print(f"Columnas: {headers}")
        print(f"Filas: {num_rows}")

        if num_rows > 0:
            print("\nDatos:")
            for i in range(min(num_rows, 20)):  # Limitar a 20 filas
                fila = data[i*num_cols:(i+1)*num_cols]
                print(f"  {fila}")
    else:
        print(f"No se pudo obtener la tabla: {tabla}")

except Exception as e:
    print(f"Error: {e}")

# Listar todas las tablas de analisis
print("\n--- TABLAS DE ANALISIS ---")
try:
    ret = SapModel.DatabaseTables.GetAvailableTables()
    tablas = list(ret[1]) if ret[0] > 0 else []

    tablas_analisis = [t for t in tablas if 'analysis' in t.lower() or 'element' in t.lower()]
    for t in tablas_analisis[:20]:
        print(f"  {t}")
except:
    pass

# Obtener propiedades del material
print("\n--- PROPIEDADES DEL MATERIAL ---")
try:
    ret = SapModel.PropMaterial.GetNameList()
    if ret[0] > 0:
        materiales = list(ret[1])
        for mat in materiales:
            ret = SapModel.PropMaterial.GetMPIsotropic(mat)
            E = ret[0]
            nu = ret[1]
            print(f"  {mat}: E={E:.2e}, nu={nu}")
except Exception as e:
    print(f"Error: {e}")

# Obtener propiedades de la seccion shell
print("\n--- PROPIEDADES DE SECCION SHELL ---")
try:
    ret = SapModel.PropArea.GetNameList()
    if ret[0] > 0:
        secciones = list(ret[1])
        for sec in secciones:
            ret = SapModel.PropArea.GetShell_1(sec)
            shell_type = ret[0]  # 1=thin, 2=thick, etc.
            mat = ret[2]
            thick = ret[4]
            print(f"  {sec}: tipo={shell_type}, material={mat}, t={thick}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("NOTA SOBRE EXTRACCION DE MATRIZ K")
print("="*60)
print("""
SAP2000 NO expone la matriz de rigidez del elemento individual
directamente a traves de la API de OAPI.

Opciones para obtener la matriz K:
1. Display > Show Tables > Analysis > Assembled Joint Stiffness
   (Esta es la matriz K global ensamblada)

2. Exportar a archivo de texto:
   File > Export > SAP2000 Analysis Tables
   Seleccionar: Element Stiffness Matrices

3. Usar el metodo manual:
   - Aplicar cargas unitarias en cada GDL
   - Medir desplazamientos
   - Calcular K = F / U

Para comparar con Calcpad, lo mejor es:
- Verificar que los desplazamientos coincidan
- Verificar que las fuerzas internas coincidan
""")
