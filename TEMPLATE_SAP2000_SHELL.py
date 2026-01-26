# -*- coding: utf-8 -*-
"""
TEMPLATE - Análisis de Placa con SAP2000 API Python
Usar este como base para futuros análisis de elementos Shell/Area
"""
import comtypes.client

# ========== CONFIGURACIÓN ==========
# Geometría
LONG_X = 2.0  # m
LONG_Y = 2.0  # m
ESPESOR = 0.2  # m

# Material (Concreto)
E_MODULO = 25000  # MPa
POISSON = 0.2
COEF_TERM = 0.00001

# Carga
CARGA_UNIFORME = 10  # kN/m2

# Archivo de salida
RUTA_MODELO = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\MODELO_PLACA.sdb'

# ========== INICIAR SAP2000 ==========
print("Iniciando SAP2000...")
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
SapObject.ApplicationStart()
SapModel = SapObject.SapModel

try:
    # ========== CREAR MODELO ==========
    print("Creando modelo...")
    SapModel.InitializeNewModel(6)  # kN, m, C
    SapModel.File.NewBlank()

    # ========== MATERIAL ==========
    print("Definiendo material...")
    MATERIAL_CONCRETE = 2
    SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)
    SapModel.PropMaterial.SetMPIsotropic('CONC', E_MODULO*1000, POISSON, COEF_TERM)

    # ========== PROPIEDAD DE SHELL ==========
    print("Definiendo propiedad de placa...")
    # IMPORTANTE: ShellType 4 = Plate-Thick (CON FLEXIÓN)
    # NO usar 5 (Membrane) porque no soporta flexión
    SapModel.PropArea.SetShell_1('PLACA', 4, False, 'CONC', 0, ESPESOR, ESPESOR, -1, "", "")

    # ========== CREAR GEOMETRÍA ==========
    print("Creando puntos...")
    x_coords = [0, LONG_X, LONG_X, 0]
    y_coords = [0, 0, LONG_Y, LONG_Y]
    z_coords = [0, 0, 0, 0]

    for i in range(4):
        SapModel.PointObj.AddCartesian(x_coords[i], y_coords[i], z_coords[i], f"P{i+1}")

    print("Creando área...")
    SapModel.AreaObj.AddByCoord(4, x_coords, y_coords, z_coords, "A1", "PLACA", "A1")
    SapModel.View.RefreshView(0, False)

    # ========== APOYOS ==========
    print("Aplicando apoyos...")
    # Apoyo simple: solo U3 restringido
    Restraint = [False, False, True, False, False, False]
    for i in range(1, 5):
        SapModel.PointObj.SetRestraint(f"P{i}", Restraint)

    # ========== CARGAS ==========
    print("Definiendo cargas...")
    LTYPE_OTHER = 8
    SapModel.LoadPatterns.Add('DEAD', LTYPE_OTHER, 1, True)

    # Dir = 6 es Gravity (hacia abajo)
    SapModel.AreaObj.SetLoadUniform("A1", 'DEAD', CARGA_UNIFORME, 6, True, "Global", 0)

    # ========== GUARDAR ==========
    print(f"Guardando: {RUTA_MODELO}")
    SapModel.File.Save(RUTA_MODELO)

    # ========== ANALIZAR ==========
    print("Ejecutando análisis...")
    SapModel.Analyze.RunAnalysis()

    # ========== CONFIGURAR SALIDA ==========
    print("Configurando salida...")
    SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    SapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")

    # ========== EXTRAER RESULTADOS ==========
    print("Extrayendo resultados...")

    # Inicializar variables
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
    ObjectElm = 0

    # Llamar a AreaForceShell
    [NumberResults, Obj, Elm, PointElm, LoadCase, StepType, StepNum,
     F11, F22, F12, FMax, FMin, FAngle, FVM,
     M11, M22, M12, MMax, MMin, MAngle,
     V13, V23, VMax, VAngle, ret] = \
        SapModel.Results.AreaForceShell("A1", ObjectElm, NumberResults, Obj, Elm,
                                        PointElm, LoadCase, StepType, StepNum,
                                        F11, F22, F12, FMax, FMin, FAngle, FVM,
                                        M11, M22, M12, MMax, MMin, MAngle,
                                        V13, V23, VMax, VAngle)

    # ========== MOSTRAR RESULTADOS ==========
    print(f"\nNúmero de resultados: {NumberResults}")
    print(f"Código de retorno: {ret}")

    if NumberResults > 0:
        max_m11 = max(abs(m) for m in M11)
        max_m22 = max(abs(m) for m in M22)
        max_v13 = max(abs(v) for v in V13)

        print("\n" + "="*60)
        print("RESULTADOS - MOMENTOS DE PLACA")
        print("="*60)
        print(f"M11 máximo = {max_m11:.6f} kN-m/m")
        print(f"M22 máximo = {max_m22:.6f} kN-m/m")
        print(f"V13 máximo = {max_v13:.6f} kN/m")
        print("="*60)

        print("\nPrimeros 4 puntos:")
        for i in range(min(NumberResults, 4)):
            print(f"  Punto {PointElm[i]}: M11={M11[i]:.4f}, M22={M22[i]:.4f}, V13={V13[i]:.4f}")
    else:
        print("\n[ERROR] No se obtuvieron resultados")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

finally:
    # ========== CERRAR SAP2000 ==========
    print("\nCerrando SAP2000...")
    SapObject.ApplicationExit(False)
    print("Finalizado")
