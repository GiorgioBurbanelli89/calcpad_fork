# -*- coding: utf-8 -*-
"""
SAP2000 API - Extraccion de Resultados via DatabaseTables
Metodo alternativo cuando Results API no funciona
"""
import sys
import comtypes.client

print("="*70)
print("SAP2000 - EXTRACCION VIA DATABASE TABLES")
print("="*70)

try:
    # Conectar a SAP2000
    print("\n[1] Conectando a SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    sap = helper.CreateObjectProgID("CSI.SAP2000.API.SAPObject")
    sap.ApplicationStart()
    model = sap.SapModel
    print("    [OK] Conectado")

    # Crear modelo simple
    print("\n[2] Creando modelo simple...")
    model.InitializeNewModel(6)  # kN, m, C
    model.File.NewBlank()

    # Material
    model.PropMaterial.SetMaterial("CONC", 2)
    model.PropMaterial.SetMPIsotropic("CONC", 25000000, 0.2, 0.0000099)

    # Viga simple
    model.PropFrame.SetRectangle("R1", "CONC", 0.3, 0.3)
    model.PointObj.AddCartesian(0, 0, 0, "1")
    model.PointObj.AddCartesian(3, 0, 0, "2")
    model.FrameObj.AddByPoint("1", "2", "", "R1", "VIGA1")

    # Apoyo empotrado
    model.PointObj.SetRestraint("1", [True, True, True, True, True, True], 0)

    # Carga
    model.PointObj.SetLoadForce("2", "DEAD", [0, 0, -10, 0, 0, 0], False, "", 0)
    print("    [OK] Modelo creado")

    # Analizar
    print("\n[3] Ejecutando analisis...")
    model.Analyze.CreateAnalysisModel()
    ret = model.Analyze.RunAnalysis()
    print(f"    [OK] Analisis completado (ret={ret})")

    # Guardar
    path_file = R"C:\Users\j-b-j\Documents\Calcpad-7.5.7\SAP2000_TABLES_TEST.sdb"
    model.File.Save(path_file)
    print(f"    [OK] Guardado: {path_file}")

    # METODO 1: Usar SetModelIsLocked
    print("\n[4] Desbloqueando modelo...")
    model.SetModelIsLocked(False)
    print("    [OK] Modelo desbloqueado")

    # METODO 2: DatabaseTables API
    print("\n[5] Extrayendo resultados via DatabaseTables...")

    # Tablas disponibles en SAP2000:
    # - "Joint Displacements"
    # - "Joint Reactions"
    # - "Element Forces - Frames"

    # Preparar variables para GetTableForDisplayArray
    FieldKeyList = []
    GroupName = ""

    # Tabla de desplazamientos
    print("\n--- Tabla: Joint Displacements ---")
    TableKey = "Joint Displacements"
    ret = model.DatabaseTables.GetTableForDisplayArray(TableKey, FieldKeyList, GroupName)

    if ret[0] == 0:  # Success
        TableVersion = ret[1]
        FieldsKeysIncluded = ret[2]
        NumberRecords = ret[3]
        TableData = ret[4]

        print(f"[OK] {NumberRecords} registros encontrados")
        print(f"[OK] Campos: {len(FieldsKeysIncluded)}")

        # Mostrar primeros resultados
        if NumberRecords > 0 and len(TableData) > 0:
            print("\nPrimeros 10 registros:")
            num_cols = len(FieldsKeysIncluded)

            # Header
            header = " | ".join(FieldsKeysIncluded)
            print(f"\n{header}")
            print("-" * len(header))

            # Data (TableData es un array 1D: [row1col1, row1col2, ..., row2col1, row2col2, ...])
            for i in range(min(10, NumberRecords)):
                row_start = i * num_cols
                row_end = row_start + num_cols
                row_data = TableData[row_start:row_end]
                row_str = " | ".join(str(val) for val in row_data)
                print(row_str)
        else:
            print("[WARN] No hay datos en la tabla")
    else:
        print(f"[ERROR] No se pudo obtener tabla (ret={ret[0]})")

    # Tabla de reacciones
    print("\n--- Tabla: Joint Reactions ---")
    TableKey = "Joint Reactions"
    ret = model.DatabaseTables.GetTableForDisplayArray(TableKey, FieldKeyList, GroupName)

    if ret[0] == 0:
        NumberRecords = ret[3]
        TableData = ret[4]
        FieldsKeysIncluded = ret[2]

        print(f"[OK] {NumberRecords} registros encontrados")

        if NumberRecords > 0 and len(TableData) > 0:
            num_cols = len(FieldsKeysIncluded)
            print("\nPrimeros 5 registros:")

            # Header
            header = " | ".join(FieldsKeysIncluded)
            print(f"\n{header}")
            print("-" * len(header))

            for i in range(min(5, NumberRecords)):
                row_start = i * num_cols
                row_end = row_start + num_cols
                row_data = TableData[row_start:row_end]
                row_str = " | ".join(str(val) for val in row_data)
                print(row_str)
    else:
        print(f"[ERROR] No se pudo obtener tabla (ret={ret[0]})")

    # Tabla de fuerzas en frames
    print("\n--- Tabla: Element Forces - Frames ---")
    TableKey = "Element Forces - Frames"
    ret = model.DatabaseTables.GetTableForDisplayArray(TableKey, FieldKeyList, GroupName)

    if ret[0] == 0:
        NumberRecords = ret[3]
        TableData = ret[4]
        FieldsKeysIncluded = ret[2]

        print(f"[OK] {NumberRecords} registros encontrados")

        if NumberRecords > 0 and len(TableData) > 0:
            num_cols = len(FieldsKeysIncluded)
            print("\nPrimeros 5 registros:")

            # Header
            header = " | ".join(FieldsKeysIncluded)
            print(f"\n{header}")
            print("-" * len(header))

            for i in range(min(5, NumberRecords)):
                row_start = i * num_cols
                row_end = row_start + num_cols
                row_data = TableData[row_start:row_end]
                row_str = " | ".join(str(val) for val in row_data)
                print(row_str)
    else:
        print(f"[ERROR] No se pudo obtener tabla (ret={ret[0]})")

    print("\n" + "="*70)
    print("VERIFICACION TEORICA")
    print("="*70)
    print("\nViga en voladizo L=3m, P=10kN:")
    print("  Deflexion teorica = PL^3/(3EI)")
    print("  E = 25000 MPa = 25000000 kN/m2")
    print("  I = bh^3/12 = 0.3*0.3^3/12 = 0.000675 m4")
    print("  delta = 10*3^3/(3*25000000*0.000675) = 0.00053 m = 0.53 mm")
    print("  Momento = PL = 10*3 = 30 kNm")
    print("  Reaccion = P = 10 kN")

    print("\n" + "="*70)
    print("Modelo guardado y SAP2000 dejado abierto")
    print(f"Archivo: {path_file}")
    print("="*70)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
