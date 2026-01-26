# -*- coding: utf-8 -*-
"""
Test rapido de conexion a SAP2000
"""

import comtypes.client
import sys

print("Conectando a SAP2000...")

try:
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    mySapObject = helper.GetObject("CSI.SAP2000.API.SapObject")
    SapModel = mySapObject.SapModel
    print(f"Conectado: SAP2000 {SapModel.GetVersion()[0]}")
    print(f"Bloqueado: {SapModel.GetModelIsLocked()}")

    # Ver archivo actual
    ret = SapModel.GetModelFilename()
    print(f"Archivo: {ret}")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
