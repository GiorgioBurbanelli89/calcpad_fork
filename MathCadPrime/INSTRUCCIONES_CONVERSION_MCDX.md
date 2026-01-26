# Instrucciones para Convertir archivos .mcdx a .cpd

## Proceso Paso a Paso

### 1. Descomprimir el archivo .mcdx

Los archivos .mcdx son archivos ZIP. Para analizarlos:

```bash
# Renombrar a .zip
cp archivo.mcdx archivo.zip

# Descomprimir
unzip archivo.zip -d archivo_extracted

# Ver estructura
ls -la archivo_extracted/mathcad/
```

### 2. Revisar el worksheet.xml

El archivo principal está en `mathcad/worksheet.xml`:

```bash
cat archivo_extracted/mathcad/worksheet.xml | xmllint --format -
```

Estructura típica:
- `<regions>`: Contenedor de todas las regiones
  - `<region>`: Cada región es un elemento (texto, matemática, gráfica, imagen)
    - `<text>`: Bloques de texto
    - `<math>`: Expresiones matemáticas
      - `<ml:define>`: Definición de variables
      - `<ml:eval>`: Evaluación de expresiones
      - `<ml:matrix>`: Matrices/vectores
      - `<ml:apply>`: Operadores (plus, minus, mult, div, pow, scale)
    - `<plot>`: Gráficas 2D
    - `<picture>`: Imágenes embebidas
    - `<solveblock>`: Bloques de solver (EDOs, sistema de ecuaciones)
    - `<spec-table>`: Tablas de especificaciones

### 3. Mapeo de elementos Mathcad → Calcpad

#### Variables y expresiones

**Mathcad XML**:
```xml
<ml:define>
  <ml:id>K</ml:id>
  <ml:apply>
    <ml:scale />
    <ml:real>1766.568</ml:real>
    <ml:apply>
      <ml:div />
      <ml:id>tonnef</ml:id>
      <ml:id>m</ml:id>
    </ml:apply>
  </ml:apply>
</ml:define>
```

**Calcpad**:
```calcpad
K = 1766.568'tonnef/m
```

#### Vectores y Matrices

**Mathcad XML**:
```xml
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
```

**Calcpad**:
```calcpad
' Vector columna con unidad
x = [2; 2; 6]'m
```

#### Gráficas

**Mathcad XML**:
```xml
<plot>
  <xyPlot>
    <axes>
      <xAxis>
        <plotEquations>
          <plotEquation>
            <math><ml:id>x</ml:id></math>
          </plotEquation>
        </plotEquations>
      </xAxis>
      <yAxis>
        <plotEquations>
          <plotEquation>
            <math><ml:id>F</ml:id></math>
          </plotEquation>
        </plotEquations>
      </yAxis>
    </axes>
  </xyPlot>
</plot>
```

**Calcpad (Opción 1 - Python)**:
```calcpad
#columns 1 python
import matplotlib.pyplot as plt
plt.plot(x_data, F_data)
plt.xlabel('x')
plt.ylabel('F')
plt.legend(['F vs x'])
plt.show()
#end columns
```

**Calcpad (Opción 2 - Tabla de datos)**:
```calcpad
#show
'<table border="1">
'<tr><th>x</th><th>F</th></tr>
'<tr><td>$x_1$</td><td>$F_1$</td></tr>
'<tr><td>$x_2$</td><td>$F_2$</td></tr>
'</table>
#hide
```

#### Solve Blocks (EDOs)

**Mathcad XML**:
```xml
<solveblock>
  <regions>
    <region solve-block-category="constraint">
      <math>
        <ml:apply>
          <ml:equal />
          <ml:apply>
            <ml:plus />
            <ml:apply><ml:mult /><ml:id>M</ml:id>...</ml:apply>
            <ml:apply><ml:mult /><ml:id>K</ml:id>...</ml:apply>
          </ml:apply>
          <ml:real>0</ml:real>
        </ml:apply>
      </math>
    </region>
    <region solve-block-category="solver">
      <math>
        <ml:define>
          <ml:id>xa</ml:id>
          <ml:apply>
            <ml:id labels="KEYWORD">odesolve</ml:id>
            ...
          </ml:apply>
        </ml:define>
      </math>
    </region>
  </regions>
</solveblock>
```

**Calcpad (Solución analítica o Python)**:
```calcpad
' Para ecuaciones diferenciales simples, usar solución analítica
ω_n = sqr(K/M)
x_t = A*cos(ω_n*t) + B*sin(ω_n*t)

' Para EDOs complejas, usar Python con scipy
#columns 1 python
from scipy.integrate import odeint
# ... código de solver ...
#end columns
```

### 4. Usar el convertidor integrado

Calcpad tiene un convertidor integrado en `McdxConverter.cs`:

```bash
# En línea de comandos (cuando se implemente la opción -cpd)
dotnet Cli.dll archivo.mcdx -cpd salida.cpd
```

**Estado actual del convertidor**:
- ✅ Variables con unidades
- ✅ Matrices y vectores
- ✅ Operadores básicos (+, -, *, /, ^)
- ✅ Imágenes (convertidas a Base64)
- ⚠️ Gráficas (solo comentarios, no renderiza)
- ⚠️ Solve blocks (solo comentarios)

### 5. Archivos de ejemplo

En `MathCadPrime/` encontrarás:

1. **Grafica.mcdx** / **Grafica_Correcto.cpd**:
   - Vectores con unidades
   - Tabla de datos
   - Ejemplo simple

2. **Solucion de una ecuacion diferencial.mcdx** / **Ecuacion_Diferencial_Con_Grafica.cpd**:
   - Solve block de EDO
   - Gráfica con múltiples series
   - Ejemplo complejo con Python

### 6. Mejoras Futuras

#### Para McdxConverter.cs

1. **Agregar generación automática de código Python para gráficas**:
   ```csharp
   private void ProcessPlotRegion(XElement plot, XNamespace ns)
   {
       var xVar = ExtractXAxisVariable(plot, ns);
       var yVar = ExtractYAxisVariable(plot, ns);

       _output.AppendLine("#columns 1 python");
       _output.AppendLine("import matplotlib.pyplot as plt");
       _output.AppendLine($"plt.plot({xVar}_data, {yVar}_data)");
       _output.AppendLine("plt.show()");
       _output.AppendLine("#end columns");
   }
   ```

2. **Convertir solve blocks a código Python**:
   ```csharp
   private void ProcessSolveBlockRegion(XElement solveblock, XNamespace ns)
   {
       // Extraer ecuación diferencial
       // Extraer condiciones iniciales
       // Generar código scipy.integrate.odeint
   }
   ```

3. **Mejorar procesamiento de spec-table**:
   ```csharp
   private void ProcessSpecTableRegion(XElement specTable, XNamespace ns)
   {
       // Extraer todas las definiciones de la tabla
       // Generar código Calcpad equivalente
   }
   ```

## Sintaxis Rápida

### Vectores y Matrices
```calcpad
v_col = [1; 2; 3]           ' Vector columna
v_row = [1, 2, 3]           ' Vector fila
M = [1; 2 | 3; 4]          ' Matriz 2x2
M_unit = [1; 2; 3]'m       ' Vector con unidad
```

### Unidades
```calcpad
F = 100'kN                  ' Fuerza en kilonewtons
M = 3.877'tonnef*s²/m      ' Unidad compuesta
x = 5'cm                    ' Longitud en centímetros
```

### Tablas HTML
```calcpad
#show
'<table border="1">
'<tr><th>Header</th></tr>
'<tr><td>$variable$</td></tr>
'</table>
#hide
```

### Código Externo
```calcpad
#columns 1 python
import numpy as np
# código Python aquí
#end columns
```

## Comandos Útiles

```bash
# Compilar CLI
cd Calcpad.Cli
dotnet build -c Debug

# Procesar archivo .cpd
dotnet Cli.dll archivo.cpd salida.html

# Convertir .mcdx manualmente
cd MathCadPrime
cp archivo.mcdx archivo.zip
unzip archivo.zip -d extracted
# ... editar manualmente ...

# Ejecutar convertidor Python
python mcdx_to_cpd_converter.py
```

## Referencias

- Calcpad Syntax: `Help/Users-Guide-EN.html`
- Mathcad XML Schema: Namespace `http://schemas.mathsoft.com/worksheet50`
- Convertidor: `Calcpad.Common/McdxConverter.cs`
