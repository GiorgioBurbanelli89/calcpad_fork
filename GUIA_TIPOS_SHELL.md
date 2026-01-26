# GUÍA RÁPIDA - Tipos de Shell en SAP2000

## Función: SetShell_1()

```python
SapModel.PropArea.SetShell_1(Name, ShellType, IncludeDrillingDOF, MatProp,
                              MatAng, Thickness, Bending, Color, Notes, GUID)
```

## Parámetro ShellType - ¿Cuál Usar?

| Tipo | Nombre | Teoría | Flexión | Membrana | Cortante | Uso |
|------|--------|--------|---------|----------|----------|-----|
| 1 | Shell-Thin | Kirchhoff | ✓ | ✓ | ✗ | Cascarones delgados |
| 2 | **Shell-Thick** | **Mindlin** | **✓** | **✓** | **✓** | **Cascarones gruesos** |
| 3 | Plate-Thin | Kirchhoff | ✓ | ✗ | ✗ | Placas delgadas |
| 4 | **Plate-Thick** | **Mindlin** | **✓** | **✗** | **✓** | **Placas gruesas** |
| 5 | Membrane | - | ✗ | ✓ | ✗ | Solo membrana (sin flexión) |
| 6 | Layered | Variable | ✓ | ✓ | ✓ | Elementos multicapa |

## ¿Cuándo Usar Cada Tipo?

### Shell-Thick (Tipo 2) - MÁS RECOMENDADO PARA LOSAS
```python
SapModel.PropArea.SetShell_1('LOSA', 2, False, 'CONC', 0, 0.2, 0.2, -1, "", "")
```
**Usar cuando:**
- Losas de concreto de cualquier espesor
- Muros de concreto armado
- Elementos que pueden tener flexión Y fuerzas en plano
- **Teoría:** Mindlin-Reissner (incluye deformación por cortante)

**Resultados disponibles:**
- M11, M22, M12 (momentos de flexión) ✓
- V13, V23 (cortantes transversales) ✓
- F11, F22, F12 (fuerzas de membrana) ✓

---

### Plate-Thick (Tipo 4) - PARA PLACAS PURAS
```python
SapModel.PropArea.SetShell_1('PLACA', 4, False, 'CONC', 0, 0.2, 0.2, -1, "", "")
```
**Usar cuando:**
- Análisis de flexión pura de placas
- No hay fuerzas en el plano del elemento
- Espesor moderado a grueso (t/L > 1/20)

**Resultados disponibles:**
- M11, M22, M12 (momentos de flexión) ✓
- V13, V23 (cortantes transversales) ✓
- F11, F22, F12 = 0 (sin membrana)

---

### Shell-Thin (Tipo 1) - PARA CASCARONES DELGADOS
```python
SapModel.PropArea.SetShell_1('CASCARON', 1, False, 'ACERO', 0, 0.01, 0.01, -1, "", "")
```
**Usar cuando:**
- Cascarones metálicos muy delgados
- t/L < 1/100
- **Teoría:** Kirchhoff (SIN deformación por cortante)

**Limitación:** No captura efectos de cortante transversal

---

### Membrane (Tipo 5) - ⚠️ NO USAR PARA LOSAS
```python
SapModel.PropArea.SetShell_1('MEMBRANA', 5, False, 'CONC', 0, 0.2, 0.2, -1, "", "")
```
**Usar cuando:**
- Paredes de tanques (solo tracción/compresión en plano)
- Membranas tensadas
- **NO para losas o placas**

**Resultados disponibles:**
- F11, F22, F12 (fuerzas de membrana) ✓
- M11, M22, M12 = 0 (sin flexión) ❌
- V13, V23 = 0 (sin cortante) ❌

---

## Comparación de Teorías

### Kirchhoff (Tipos 1 y 3)
- Placas/cascarones **DELGADOS**
- NO incluye deformación por cortante
- Requiere t/L < 1/20
- Más simple, menos DOFs

### Mindlin-Reissner (Tipos 2 y 4)
- Placas/cascarones de **CUALQUIER ESPESOR**
- SÍ incluye deformación por cortante
- Válido para t/L > 1/20
- Más preciso para elementos gruesos

## Recomendación General

**Para análisis de losas de concreto:**
```python
# USAR ESTO (Shell-Thick tipo 2)
SapModel.PropArea.SetShell_1('LOSA', 2, False, 'CONC', 0, espesor, espesor, -1, "", "")
```

**NUNCA usar tipo 5 (Membrane) para losas** - retornará momentos en cero.

## Ejemplo Completo

```python
import comtypes.client

# Conectar a SAP2000
helper = comtypes.client.CreateObject('SAP2000v1.Helper')
helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")
SapObject.ApplicationStart()
SapModel = SapObject.SapModel

# Crear modelo
SapModel.InitializeNewModel(6)  # kN, m, C
SapModel.File.NewBlank()

# Material
SapModel.PropMaterial.SetMaterial('CONC', 2)  # Concrete
SapModel.PropMaterial.SetMPIsotropic('CONC', 25000000, 0.2, 0.00001)

# CORRECTO: Shell-Thick para losa con flexión
SapModel.PropArea.SetShell_1('LOSA', 2, False, 'CONC', 0, 0.2, 0.2, -1, "", "")
#                                     ^
#                               Shell-Thick (con flexión)

# Crear geometría, cargas, analizar, etc...

# Cerrar
SapObject.ApplicationExit(False)
```

## Referencias
- Documentación oficial: `SetShell_1.htm`
- Ejemplo funcionando: `test_shell_SHELL_THICK_CORRECTO.py`
- Template: `TEMPLATE_SAP2000_SHELL.py`
