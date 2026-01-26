# -*- coding: utf-8 -*-
"""
IMPORTAR ARCHIVOS .s2k ANTIGUOS - Método Correcto
Basado en documentación oficial de OpenFile
"""
import comtypes.client

print("="*70)
print("IMPORTAR ARCHIVO .s2k ANTIGUO A SAP2000")
print("="*70)

# Ruta al archivo .s2k original
s2k_file = R'C:\Users\j-b-j\Documents\Calcpad\Examples\Mechanics\Finite Elements\SAP 2000\Plate-6x4.s2k'
sdb_file = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\Plate_6x4_imported.sdb'

try:
    # ========== INICIAR SAP2000 ==========
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    SapObject.ApplicationStart()
    SapModel = SapObject.SapModel
    print("    [OK] Iniciado")

    # ========== IMPORTANTE: NO LLAMAR InitializeNewModel ==========
    # Según la documentación VBA de OpenFile, NO se debe llamar
    # a InitializeNewModel antes de abrir un archivo existente

    # ========== ABRIR ARCHIVO .s2k DIRECTAMENTE ==========
    print(f"\n[2] Importando archivo .s2k como texto...")
    print(f"    Archivo: {s2k_file}")
    print(f"    Segun documentacion: archivos .s2k se importan como texto")

    # OpenFile debería importar automáticamente archivos .s2k
    ret = SapModel.File.OpenFile(s2k_file)
    print(f"    Resultado: ret={ret}")

    if ret == 0:
        print("    [OK] Archivo importado exitosamente")
    else:
        print(f"    [AVISO] Codigo de retorno: {ret}")

    # ========== VERIFICAR IMPORTACION ==========
    print(f"\n[3] Verificando modelo importado...")

    # Intentar obtener información del modelo
    try:
        # Obtener nombre del archivo abierto
        model_file = SapModel.GetModelFilename()
        print(f"    Archivo actual: {model_file}")
    except:
        print("    [INFO] No se pudo obtener nombre del archivo")

    # Verificar objetos
    try:
        num_points = SapModel.PointObj.Count()
        print(f"    Puntos: {num_points}")
    except Exception as e:
        print(f"    [ERROR contando puntos] {e}")
        num_points = 0

    try:
        num_areas = SapModel.AreaObj.Count()
        print(f"    Areas: {num_areas}")
    except Exception as e:
        print(f"    [ERROR contando areas] {e}")
        num_areas = 0

    # Intentar obtener nombres de objetos
    try:
        ret_names = SapModel.AreaObj.GetNameList()
        if ret_names[0] > 0:
            print(f"    Areas por nombre: {ret_names[0]}")
            area_names = ret_names[1]
            print(f"    Primeras 5 areas: {area_names[:5]}")
        else:
            print("    [INFO] No se obtuvieron nombres de areas")
            area_names = []
    except Exception as e:
        print(f"    [ERROR obteniendo nombres] {e}")
        area_names = []

    # ========== SI HAY OBJETOS, GUARDAR Y ANALIZAR ==========
    if num_areas > 0 or len(area_names) > 0:
        print(f"\n[4] Modelo tiene objetos - Guardando...")
        ret = SapModel.File.Save(sdb_file)
        print(f"    [OK] Guardado: {sdb_file} (ret={ret})")

        print("\n[5] Ejecutando analisis...")
        ret = SapModel.Analyze.RunAnalysis()
        print(f"    [OK] Analisis (ret={ret})")

        print("\n[6] Configurando output...")
        SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

        # Intentar con diferentes nombres de caso de carga
        load_cases = ["LOAD1", "DEFAULT", "DEAD", "Dead"]
        for lc in load_cases:
            try:
                ret = SapModel.Results.Setup.SetCaseSelectedForOutput(lc)
                if ret == 0:
                    print(f"    [OK] Caso '{lc}' seleccionado")
                    selected_case = lc
                    break
            except:
                continue

        # ========== EXTRAER RESULTADOS ==========
        if len(area_names) > 0:
            print(f"\n[7] Extrayendo resultados del primer elemento...")
            first_area = area_names[0]

            NumberResults = 0
            Obj = []
            Elm = []
            PointElm = []
            LoadCase = []
            StepType = []
            StepNum = []
            F11 = []
            F22 = []
            F12 = []
            FMax = []
            FMin = []
            FAngle = []
            FVM = []
            M11 = []
            M22 = []
            M12 = []
            MMax = []
            MMin = []
            MAngle = []
            V13 = []
            V23 = []
            VMax = []
            VAngle = []

            [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
             F11, F22, F12, FMax, FMin, FAngle, FVM,
             M11, M22, M12, MMax, MMin, MAngle,
             V13, V23, VMax, VAngle, ret] = \
                SapModel.Results.AreaForceShell(first_area, 0, 0, [], [],
                                                [], [], [], [],
                                                [], [], [], [], [], [], [],
                                                [], [], [], [], [], [],
                                                [], [], [], [])

            print(f"    Area: {first_area}")
            print(f"    NumberResults: {NumberResults}")
            print(f"    ret: {ret}")

            if NumberResults > 0:
                max_m11 = max(abs(m) for m in M11)
                max_m22 = max(abs(m) for m in M22)
                print(f"\n    [EXITO] Momentos extraidos:")
                print(f"      M11 max = {max_m11:.6f} kN-m/m")
                print(f"      M22 max = {max_m22:.6f} kN-m/m")
            else:
                print("    [INFO] Sin resultados de momentos")
    else:
        print("\n[4] [ERROR] Modelo vacio - no se importaron objetos")
        print("    Posibles causas:")
        print("    - Archivo de version muy antigua (pre-v8)")
        print("    - Formato incompatible")
        print("    - Necesita traduccion manual")

    # ========== CERRAR ==========
    print("\n[8] Cerrando...")
    SapObject.ApplicationExit(False)
    print("    [OK] Cerrado")

except Exception as e:
    print(f"\n[ERROR GENERAL] {e}")
    import traceback
    traceback.print_exc()

    try:
        if 'SapObject' in locals():
            SapObject.ApplicationExit(False)
    except:
        pass

print("\n" + "="*70)
print("ALTERNATIVAS SI NO FUNCIONA:")
print("="*70)
print("1. Abrir Plate-6x4.s2k manualmente en SAP2000 GUI")
print("2. Guardar como .sdb desde el menu File > Save As")
print("3. Luego abrir el .sdb con la API Python")
print("-"*70)
print("4. O modificar manualmente la version en el archivo .s2k:")
print("   - Abrir Plate-6x4.s2k en un editor de texto")
print("   - Buscar la linea con 'PROGRAM'")
print("   - Cambiar version a una mas reciente (ej: 12.0.0)")
print("   - Guardar y volver a intentar")
print("="*70)

print("\n[FIN]")
