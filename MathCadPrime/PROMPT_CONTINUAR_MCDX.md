# Prompt para Continuar - Conversión MCDX a CPD

## Contexto del Proyecto

Estamos trabajando en mejorar la conversión de archivos Mathcad Prime (.mcdx) a Calcpad (.cpd).

### Lo que ya está hecho:

1. ✅ **Análisis de estructura .mcdx**:
   - Los archivos .mcdx son archivos ZIP
   - El archivo principal es `mathcad/worksheet.xml`
   - Contiene regiones con: texto, matemáticas, gráficas, imágenes, solve blocks

2. ✅ **Convertidor existente** (`Calcpad.Common/McdxConverter.cs`):
   - Convierte variables con unidades
   - Convierte matrices y vectores
   - Convierte operadores básicos
   - Convierte imágenes a Base64
   - NO convierte gráficas (solo pone comentarios)
   - NO convierte solve blocks (EDOs)

3. ✅ **Archivos de ejemplo creados**:
   - `Grafica_Correcto.cpd`: Vector con unidades + tabla HTML
   - `Ecuacion_Diferencial_Vibracion.cpd`: Solución analítica de EDO
   - `Ecuacion_Diferencial_Con_Grafica.cpd`: Con código Python/Matplotlib

4. ✅ **Documentación**:
   - `RESUMEN_GRAFICAS_MATHCAD_VS_CALCPAD.md`: Opciones de gráficas
   - `INSTRUCCIONES_CONVERSION_MCDX.md`: Guía completa de conversión

### Archivos de prueba disponibles:

En `MathCadPrime/`:
- `Grafica.mcdx` → Gráfica simple con tabla de datos
- `Solucion de una ecuacion diferencial.mcdx` → EDO con solve block
- `Modos de vibracion.mcdx` → Ejemplo con múltiples elementos
- `Ensamblaje_Placas.mcdx` → Ejemplo de matrices grandes

### Sintaxis clave de Calcpad:

**Vectores**:
```calcpad
v = [1; 2; 3]'m  ' Vector columna con unidades
```

**Gráficas** (actualmente):
```calcpad
' Opción 1: Python/Matplotlib
#columns 1 python
import matplotlib.pyplot as plt
plt.plot(x, y)
plt.legend(['Serie 1'])
plt.show()
#end columns

' Opción 2: Plotly (JavaScript embebido)
' Ver Examples/Demos/Plotly.cpd

' Opción 3: Primitivas SVG
$svg{width:500; height:300}
' ... código SVG manual ...
```

## Tareas Pendientes

### 1. Mejorar McdxConverter.cs para gráficas

**Objetivo**: Cuando se detecta `<plot><xyPlot>`, generar automáticamente código Python/Matplotlib.

**Archivo**: `Calcpad.Common/McdxConverter.cs`

**Método a modificar**: `ProcessPlotRegion(XElement plot, XNamespace ns)` (línea ~521)

**Implementación sugerida**:
```csharp
private void ProcessPlotRegion(XElement plot, XNamespace ns)
{
    var xyPlot = plot.Descendants(ns + "xyPlot").FirstOrDefault();
    if (xyPlot == null) return;

    // Extraer ejes
    var axes = xyPlot.Descendants(ns + "axes").FirstOrDefault();
    var xAxis = axes?.Descendants(ns + "xAxis").FirstOrDefault();
    var yAxis = axes?.Descendants(ns + "yAxis").FirstOrDefault();

    // Extraer variables de los ejes
    var xVar = xAxis?.Descendants(_mlNs + "id").FirstOrDefault()?.Value;
    var yVar = yAxis?.Descendants(_mlNs + "id").FirstOrDefault()?.Value;

    if (string.IsNullOrEmpty(xVar) || string.IsNullOrEmpty(yVar))
    {
        _output.AppendLine("' [Gráfica no pudo ser convertida]");
        return;
    }

    // Generar código Python
    _output.AppendLine($"' Gráfica: {yVar} vs {xVar}");
    _output.AppendLine();
    _output.AppendLine("#columns 1 python");
    _output.AppendLine("import matplotlib.pyplot as plt");
    _output.AppendLine("import numpy as np");
    _output.AppendLine();
    _output.AppendLine($"# Convertir {xVar} y {yVar} a arrays numpy");
    _output.AppendLine($"x_data = np.array({xVar}) if hasattr({xVar}, '__iter__') else [{xVar}]");
    _output.AppendLine($"y_data = np.array({yVar}) if hasattr({yVar}, '__iter__') else [{yVar}]");
    _output.AppendLine();
    _output.AppendLine("plt.figure(figsize=(8, 5))");
    _output.AppendLine($"plt.plot(x_data, y_data, 'b-', linewidth=2, label='{yVar}')");
    _output.AppendLine($"plt.xlabel('{xVar}')");
    _output.AppendLine($"plt.ylabel('{yVar}')");
    _output.AppendLine("plt.grid(True, alpha=0.3)");
    _output.AppendLine("plt.legend()");
    _output.AppendLine("plt.tight_layout()");
    _output.AppendLine("plt.show()");
    _output.AppendLine("#end columns");
    _output.AppendLine();
}
```

### 2. Mejorar procesamiento de spec-table

**Objetivo**: Convertir tablas de especificaciones de Mathcad a definiciones de Calcpad.

**Método a agregar**: `ProcessSpecTableRegion(XElement specTable, XNamespace ns)`

**Ejemplo de XML**:
```xml
<spec-table>
  <math resultRef="0">
    <ml:define>
      <ml:id>x</ml:id>
      <ml:apply>
        <ml:scale />
        <ml:matrix rows="3" cols="1">
          <ml:real>2</ml:real>
          <ml:real>2</ml:real>
          <ml:real>6</ml:real>
        </ml:matrix>
        <ml:id>m</ml:id>
      </ml:apply>
    </ml:define>
  </math>
  <math resultRef="1">
    <ml:define>
      <ml:id>F</ml:id>
      ...
    </ml:define>
  </math>
</spec-table>
```

**Debe generar**:
```calcpad
x = [2; 2; 6]'m
F = [2; 3; 5]'tonf
```

### 3. Convertir solve blocks a código Python

**Objetivo**: Cuando se detecta `<solveblock>` con `odesolve`, generar código scipy.

**Método a modificar**: `ProcessSolveBlockRegion(XElement solveblock, XNamespace ns)` (línea ~534)

**Ejemplo**:
```python
from scipy.integrate import odeint

def system(x, t):
    # x[0] = posición
    # x[1] = velocidad
    dxdt = [x[1], -(K/M)*x[0]]
    return dxdt

x0 = [0.05, 0.0]  # [x_0, v_0]
t = np.linspace(0, 2, 201)
sol = odeint(system, x0, t)
```

### 4. Agregar soporte para múltiples series en gráficas

**Objetivo**: Detectar `<traces>` con múltiples `<trace>` y generar varias líneas plt.plot().

**Estructura XML**:
```xml
<traces>
  <trace resultRef="2">
    <traceStyle color="#FF00008B" ...>lines</traceStyle>
  </trace>
  <trace resultRef="3">
    <traceStyle color="#FF00FF00" ...>lines</traceStyle>
  </trace>
</traces>
```

## Cómo Continuar

### Prompt Sugerido:

```
Continuar con la mejora del convertidor McdxConverter.cs para archivos Mathcad Prime:

1. CONTEXTO:
   - Proyecto: Calcpad (calculadora de ingeniería)
   - Archivo a modificar: Calcpad.Common/McdxConverter.cs
   - Archivos de prueba en: MathCadPrime/*.mcdx
   - Documentación en: MathCadPrime/INSTRUCCIONES_CONVERSION_MCDX.md

2. TAREAS PRIORITARIAS:
   a) Implementar ProcessPlotRegion() para generar código Python/Matplotlib automáticamente
   b) Agregar ProcessSpecTableRegion() para tablas de especificaciones
   c) Mejorar ProcessSolveBlockRegion() para convertir odesolve a scipy.integrate

3. ARCHIVOS DE PRUEBA:
   - Grafica.mcdx: Plot simple (x vs F)
   - Solucion de una ecuacion diferencial.mcdx: Solve block con odesolve
   - Usar: unzip Grafica.mcdx -d temp/ && cat temp/mathcad/worksheet.xml

4. REQUISITOS:
   - Generar código Python válido en bloques #columns 1 python
   - Mantener compatibilidad con conversiones existentes
   - Agregar warnings cuando la conversión no sea perfecta
   - Probar con: dotnet Cli.dll archivo.mcdx -cpd salida.cpd (cuando se implemente)

5. SINTAXIS DE VECTORES EN CALCPAD:
   - Vector columna: [1; 2; 3]
   - Vector con unidad: [1; 2; 3]'m
   - Matriz: [1; 2 | 3; 4]

Ver archivos de referencia:
- MathCadPrime/Grafica_Correcto.cpd (ejemplo funcional)
- MathCadPrime/Ecuacion_Diferencial_Con_Grafica.cpd (ejemplo con gráfica Python)
- MathCadPrime/RESUMEN_GRAFICAS_MATHCAD_VS_CALCPAD.md (opciones de gráficas)

Empezar por modificar ProcessPlotRegion() en McdxConverter.cs.
```

## Comandos Útiles

```bash
# Compilar
cd Calcpad.Common
dotnet build -c Debug

# Probar conversión manual
cd MathCadPrime
unzip -q Grafica.mcdx -d temp_grafica
cat temp_grafica/mathcad/worksheet.xml | xmllint --format -

# Ver estructura de región plot
xmllint --xpath "//ws:plot" temp_grafica/mathcad/worksheet.xml

# Limpiar
rm -rf temp_grafica
```

## Estado de Archivos

```
MathCadPrime/
├── Grafica.mcdx                              # Original Mathcad
├── Grafica_Correcto.cpd                      # ✅ Conversión manual funcional
├── grafica_correcto.html                     # ✅ Resultado procesado
├── Solucion de una ecuacion diferencial.mcdx # Original Mathcad
├── Ecuacion_Diferencial_Vibracion.cpd        # ✅ Conversión sin gráfica
├── Ecuacion_Diferencial_Con_Grafica.cpd      # ✅ Conversión con Python
├── RESUMEN_GRAFICAS_MATHCAD_VS_CALCPAD.md    # Documentación
├── INSTRUCCIONES_CONVERSION_MCDX.md          # Guía completa
└── mcdx_to_cpd_converter.py                  # Convertidor Python (alternativo)
```

## Próximos Pasos Inmediatos

1. **Modificar McdxConverter.cs**:
   - Implementar ProcessPlotRegion() mejorado
   - Agregar ProcessSpecTableRegion()
   - Probar con Grafica.mcdx

2. **Compilar y probar**:
   ```bash
   cd Calcpad.Common
   dotnet build
   cd ../MathCadPrime
   # Ejecutar conversión cuando CLI soporte -cpd
   ```

3. **Verificar resultado**:
   - Comparar .cpd generado con Grafica_Correcto.cpd
   - Procesar con CLI y revisar HTML
   - Verificar que código Python sea válido

4. **Iterar**:
   - Probar con otros .mcdx
   - Agregar más características
   - Documentar cambios
