# -*- coding: utf-8 -*-
"""
Test simple: 1 elemento de shell
"""
import comtypes.client

print("="*70)
print("TEST SIMPLE - 1 ELEMENTO DE SHELL")
print("="*70)

try:
    # Iniciar
    print("\n[1] Iniciando SAP2000...")
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
    mySapObject.ApplicationStart()
    SapModel = mySapObject.SapModel
    print("    [OK]")

    # Modelo
    print("\n[2] Creando modelo...")
    SapModel.InitializeNewModel(6)  # kN, m, C
    SapModel.File.NewBlank()

    # Material
    print("\n[3] Material...")
    SapModel.PropMaterial.SetMaterial('CONC', 2)
    SapModel.PropMaterial.SetMPIsotropic('CONC', 25000000, 0.2, 0.00001)

    # Propiedad de shell
    print("\n[4] Propiedad shell...")
    # SetShell_1(Name, ShellType, MatProp, MatAng, MembraneThickness, BendingThickness, Color, Notes, GUID)
    # ShellType 5 = Plate-Thick (Mindlin)
    ret = SapModel.PropArea.SetShell_1('SHELL1', 5, False, 'CONC', 0, 0.1, 0.1, 0, "", "")
    print(f"    SetShell_1: ret={ret}")

    # 4 puntos
    print("\n[5] Creando 4 puntos...")
    SapModel.PointObj.AddCartesian(0, 0, 0, "1")
    SapModel.PointObj.AddCartesian(1, 0, 0, "2")
    SapModel.PointObj.AddCartesian(1, 1, 0, "3")
    SapModel.PointObj.AddCartesian(0, 1, 0, "4")
    num_pts = SapModel.PointObj.Count()
    print(f"    [OK] {num_pts} puntos")

    # 1 área
    print("\n[6] Creando 1 área...")
    print(f"    Puntos: 1, 2, 3, 4")
    print(f"    Propiedad: SHELL1")

    # Intentar con AddByPoint
    ret = SapModel.AreaObj.AddByPoint(4, ["1", "2", "3", "4"], "A1", "SHELL1", "A1")
    print(f"    AddByPoint ret: {ret}")
    print(f"    Tipo ret: {type(ret)}")

    num_areas = SapModel.AreaObj.Count()
    print(f"    AreaObj.Count(): {num_areas}")

    if num_areas == 0:
        print("\n    [ERROR] No se creó el área")
        print("    Intentando método alternativo...")

        # Intentar AddByCoord
        x = [0, 1, 1, 0]
        y = [0, 0, 1, 1]
        z = [0, 0, 0, 0]
        ret2 = SapModel.AreaObj.AddByCoord(4, x, y, z, "A1", "SHELL1", "A1")
        print(f"    AddByCoord ret: {ret2}")

        num_areas = SapModel.AreaObj.Count()
        print(f"    AreaObj.Count(): {num_areas}")

    # Guardar
    ModelPath = R'C:\Users\j-b-j\Documents\Calcpad-7.5.7\TEST_SHELL_SIMPLE.sdb'
    SapModel.File.Save(ModelPath)
    print(f"\n[7] Guardado: {ModelPath}")

    # Cerrar
    print("\n[8] Cerrando...")
    mySapObject.ApplicationExit(False)
    print("    [OK]")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n[FIN]")
