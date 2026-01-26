# Gráficas en Mathcad Prime vs Calcpad

## Estado Actual

### Mathcad Prime tiene:
- **xyPlot**: Gráficas 2D con múltiples series
- **Leyendas**: Automáticas para cada serie
- **Múltiples ejes**: X e Y con configuración independiente
- **Tipos de gráfica**: Líneas, puntos, barras
- **ChartComponent**: Componentes interactivos de gráfica
- **Formato avanzado**: Colores, estilos de línea, símbolos

### Calcpad actualmente tiene:

1. **Python/Matplotlib con #columns**:
   - ✅ Múltiples series
   - ✅ Leyendas completas
   - ✅ Control total de formato
   - ❌ Requiere Python instalado
   - ✅ Genera archivos PNG/SVG

2. **Octave con gnuplot**:
   - ✅ Múltiples series
   - ✅ Leyendas
   - ❌ Requiere Octave instalado
   - ✅ Genera SVG

3. **Plotly con JavaScript**:
   - ✅ Gráficas interactivas
   - ✅ Leyendas
   - ✅ 3D disponible
   - ❌ Requiere conexión a internet
   - ✅ Embebido en HTML

4. **Primitivas SVG nativas**:
   - ✅ No requiere software externo
   - ❌ No tiene leyendas automáticas
   - ❌ Muy manual
   - ✅ Muy rápido

## Opciones para Mejorar

### Opción 1: Extender el convertidor McdxConverter.cs

Agregar generación automática de código Python/Matplotlib cuando se detecta un `<plot>` o `<chartComponent>`:

```csharp
private void ProcessPlotRegion(XElement plot, XNamespace ns)
{
    // Extraer datos del plot
    var xyPlot = plot.Descendants(ns + "xyPlot").FirstOrDefault();

    // Generar código Python automáticamente
    _output.AppendLine("#columns 1 python");
    _output.AppendLine("import matplotlib.pyplot as plt");
    _output.AppendLine("# ... código generado ...");
    _output.AppendLine("#end columns");
}
```

**Ventajas**:
- Conversión automática completa
- Mantiene la visualización original
- No modifica el core de Calcpad

**Desventajas**:
- Requiere Python
- Archivos más grandes

### Opción 2: Crear función $plot{} extendida en Calcpad

Agregar soporte nativo para leyendas y múltiples series:

```calcpad
' Sintaxis propuesta:
$plot{
    x: t_values
    y1: displacement (label: "u (mm)", color: blue)
    y2: velocity (label: "u' (cm/s)", color: green)  y3: acceleration (label: "u'' (m/s²)", color: red, style: dashed)
    title: "Vibración Libre"
    xlabel: "Tiempo (s)"
    ylabel: "Respuesta"
    legend: true
}
```

**Ventajas**:
- Nativo de Calcpad
- Sintaxis limpia
- No requiere software externo

**Desventajas**:
- Requiere modificar el core
- Necesita implementar rendering SVG complejo

### Opción 3: Wrapper de Plotly mejorado

Crear una macro/función que simplifique el uso de Plotly:

```calcpad
#include "plotly_helpers.cpd"

$PlotlyMultiLine{
    data: [t, u_mm, u_v, u_a]
    labels: ["u (mm)", "u' (cm/s)", "u'' (m/s²)"]
    colors: [blue, green, red]
    title: "Vibración Libre"
}
```

**Ventajas**:
- Flexible
- Gráficas interactivas
- No modifica el core

**Desventajas**:
- Requiere conexión a internet
- Más lento que SVG nativo

## Recomendación

Para conversión de archivos .mcdx:

1. **Corto plazo**: Usar **Opción 1** (generar código Python automáticamente)
   - Fácil de implementar
   - Conversión completa
   - Mantiene todas las características

2. **Mediano plazo**: Implementar **Opción 2** ($plot{} extendido)
   - Mejor experiencia de usuario
   - No requiere dependencias externas
   - Coherente con la filosofía de Calcpad

3. **Complemento**: Tener **Opción 3** (Plotly) para gráficas interactivas avanzadas

## Archivos de Ejemplo Creados

1. `Grafica_Correcto.cpd`: Conversión simple con tabla de datos
2. `Ecuacion_Diferencial_Vibracion.cpd`: Conversión con solución analítica
3. `Ecuacion_Diferencial_Con_Grafica.cpd`: Conversión con gráfica Python/Matplotlib

## Sintaxis de Vectores y Matrices en Calcpad

```calcpad
' Vector columna (separado por ;)
v = [1; 2; 3]

' Vector fila (separado por ,)
v = [1, 2, 3]

' Matriz (filas separadas por |)
M = [1; 2; 3 | 4; 5; 6 | 7; 8; 9]

' Con unidades
x = [2; 2; 6]'m
F = [2; 3; 5]'tonf
```

## Próximos Pasos

1. Probar los archivos .cpd generados
2. Decidir qué opción de gráficas implementar
3. Extender McdxConverter.cs con la opción elegida
4. Agregar soporte para:
   - Solve blocks (odesolve) -> Generar código Python con scipy.integrate.odeint
   - Imágenes embebidas (ya soportado con Base64)
   - Tablas de especificaciones (spec-table)
