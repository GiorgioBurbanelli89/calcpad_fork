# -*- coding: utf-8 -*-
"""
Test SAP2000 API usando comtypes
Compatible con Python 3.12
"""
import sys
import os

print("="*70)
print("TEST SAP2000 API - COMTYPES")
print("="*70)

# Verificar Python
print(f"\nPython version: {sys.version}")

# Paso 1: Instalar comtypes si no esta
try:
    import comtypes
    print("[OK] comtypes esta instalado")
except ImportError:
    print("[ERROR] comtypes no esta instalado")
    print("\nInstalando comtypes...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "comtypes"])
    import comtypes
    print("[OK] comtypes instalado correctamente")

# Paso 2: Importar cliente
try:
    import comtypes.client
    print("[OK] comtypes.client importado")
except Exception as e:
    print(f"[ERROR] Error importando comtypes.client: {e}")
    sys.exit(1)

# Paso 3: Intentar conectar a SAP2000 existente
print("\n--- Intentando conectar a SAP2000 ---")
print("NOTA: SAP2000 debe estar abierto para este test")
print("Si no esta abierto, el script fallará")

try:
    # Conectar a instancia activa
    mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
    print("[OK] Conectado a SAP2000 activo")

    # Obtener SapModel
    SapModel = mySapObject.SapModel
    print("[OK] SapModel obtenido")

    # Obtener versión
    version = SapModel.GetVersion()
    print(f"[OK] SAP2000 Version: {version[0]}")

    # Obtener información del archivo actual
    file_path = SapModel.GetModelFilename()
    if file_path:
        print(f"[OK] Archivo actual: {file_path}")
    else:
        print("  No hay archivo abierto")

    # Contar objetos
    num_points = SapModel.PointObj.Count()
    print(f"[OK] Número de puntos en modelo: {num_points}")

    print("\n" + "="*70)
    print("[OK][OK][OK] API DE SAP2000 FUNCIONANDO CORRECTAMENTE [OK][OK][OK]")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    print("\n" + "="*70)
    print("RAZONES POSIBLES DEL ERROR:")
    print("="*70)
    print("1. SAP2000 no esta abierto")
    print("   Solución: Abre SAP2000 manualmente primero")
    print()
    print("2. SAP2000 no esta registrado en COM")
    print("   Solución: Reinstalar SAP2000 o ejecutar como administrador")
    print()
    print("3. Version incorrecta de SAP2000")
    print("   Solución: Verifica que tienes SAP2000 instalado")
    print("="*70)

    # Intentar crear nueva instancia (alternativa)
    print("\n--- Intentando crear nueva instancia de SAP2000 ---")
    try:
        helper = comtypes.client.CreateObject('SAP2000v1.Helper')
        helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
        mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
        mySapObject.ApplicationStart()
        SapModel = mySapObject.SapModel

        version = SapModel.GetVersion()
        print(f"[OK] Nueva instancia creada - Version: {version[0]}")

        # Cerrar
        mySapObject.ApplicationExit(False)
        print("[OK] Instancia cerrada correctamente")

        print("\n" + "="*70)
        print("[OK][OK][OK] API FUNCIONA (CREANDO NUEVA INSTANCIA) [OK][OK][OK]")
        print("="*70)

    except Exception as e2:
        print(f"[ERROR] También falló crear nueva instancia: {e2}")
        print("\nLa API de SAP2000 NO esta disponible en este sistema.")
        sys.exit(1)
