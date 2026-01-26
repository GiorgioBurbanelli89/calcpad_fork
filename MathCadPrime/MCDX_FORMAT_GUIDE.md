# Guía Completa del Formato MCDX (Mathcad Prime)

## Índice
1. [Introducción](#introducción)
2. [Estructura del Archivo](#estructura-del-archivo)
3. [Cómo Extraer el Contenido](#cómo-extraer-el-contenido)
4. [Archivos Principales](#archivos-principales)
5. [Tipos de Regiones](#tipos-de-regiones)
6. [Gráficas: xyPlot vs chartComponent](#gráficas-xyplot-vs-chartcomponent)
7. [Expresiones Matemáticas](#expresiones-matemáticas)
8. [Unidades y Escalado](#unidades-y-escalado)
9. [Matrices y Vectores](#matrices-y-vectores)
10. [Imágenes y Media](#imágenes-y-media)
11. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## Introducción

Los archivos `.mcdx` son el formato nativo de **PTC Mathcad Prime**. A diferencia del formato `.xmcd` de Mathcad 15, los archivos MCDX usan el estándar **Open Packaging Conventions (OPC)**, el mismo usado por los archivos de Microsoft Office (.docx, .xlsx).

**Características principales:**
- Es un archivo **ZIP** con extensión `.mcdx`
- Contiene **XML** estructurado según esquemas de Mathsoft/PTC
- Puede incluir **imágenes**, **gráficas OLE** y **documentos XAML**
- Versiones: Prime 1.0 (schema50) hasta Prime 10.0+ (schema110)

---

## Estructura del Archivo

Al descomprimir un archivo `.mcdx`, se obtiene esta estructura:

```
archivo.mcdx (ZIP)
│
├── [Content_Types].xml          # Tipos MIME de los archivos
├── _rels/
│   └── .rels                    # Relaciones del paquete raíz
│
├── docProps/
│   ├── app.xml                  # Metadatos de aplicación (versión)
│   └── core.xml                 # Metadatos Dublin Core (autor, fecha)
│
└── mathcad/
    ├── worksheet.xml            # ★ DOCUMENTO PRINCIPAL ★
    ├── result.xml               # Resultados cacheados de cálculos
    ├── integration.xml          # Configuración de integradores/ODE
    ├── header.xml               # Encabezado del documento
    ├── footer.xml               # Pie de página
    │
    ├── settings/
    │   ├── calculation.xml      # Configuración de cálculo
    │   └── presentation.xml     # Configuración de presentación
    │
    ├── _rels/
    │   └── worksheet.xml.rels   # ★ RELACIONES DE IMÁGENES/CHARTS ★
    │
    ├── media/                   # Imágenes embebidas
    │   ├── Image1.png
    │   ├── Image2.jpg
    │   └── ...
    │
    ├── xaml/                    # Documentos XAML (texto formateado)
    │   ├── FlowDocument0.XamlPackage
    │   └── ...
    │
    └── chart/                   # Gráficas OLE (MathChart)
        ├── chart30.ole
        └── ...
```

---

## Cómo Extraer el Contenido

### Método 1: Cambiar extensión a .zip
```bash
# Windows
copy archivo.mcdx archivo.zip
# Luego descomprimir con Windows Explorer o 7-Zip
```

### Método 2: PowerShell
```powershell
Expand-Archive -Path "archivo.mcdx" -DestinationPath "archivo_extracted"
```

### Método 3: Python
```python
import zipfile
import os

def extract_mcdx(mcdx_path, output_dir):
    """Extrae el contenido de un archivo MCDX"""
    with zipfile.ZipFile(mcdx_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    # El archivo principal está en:
    worksheet_path = os.path.join(output_dir, "mathcad", "worksheet.xml")
    return worksheet_path

# Uso
extract_mcdx("Grafica.mcdx", "Grafica_extracted")
```

### Método 4: C# (.NET)
```csharp
using System.IO.Compression;

public void ExtractMcdx(string mcdxPath, string outputDir)
{
    // MCDX es un ZIP estándar
    ZipFile.ExtractToDirectory(mcdxPath, outputDir);

    // Leer worksheet.xml
    string worksheetPath = Path.Combine(outputDir, "mathcad", "worksheet.xml");
    var doc = XDocument.Load(worksheetPath);
}
```

---

## Archivos Principales

### worksheet.xml (Documento Principal)

Este es el archivo más importante. Contiene todas las regiones del documento.

**Namespaces importantes:**
```xml
xmlns:ws="http://schemas.mathsoft.com/worksheet50"   <!-- Worksheet -->
xmlns:ml="http://schemas.mathsoft.com/math50"        <!-- Math Language -->
xmlns:u="http://schemas.mathsoft.com/units10"        <!-- Units -->
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
```

**Estructura básica:**
```xml
<worksheet xmlns="http://schemas.mathsoft.com/worksheet50" ...>
  <regions>
    <region region-id="0" top="100" left="50" ...>
      <!-- Contenido de la región -->
    </region>
    <region region-id="1" ...>
      <!-- Otra región -->
    </region>
  </regions>
</worksheet>
```

### worksheet.xml.rels (Relaciones)

Mapea IDs a archivos de media:
```xml
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    Target="/mathcad/media/Image3.png"
    Id="R91ba0f034d3b43e9" />
  <Relationship
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart"
    Target="/mathcad/chart/chart30.ole"
    Id="R6011d9ed3c95494c" />
</Relationships>
```

### app.xml (Versión de Mathcad)

```xml
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>PTC Mathcad Prime</Application>
  <AppVersion>10.0.0.0</AppVersion>
</Properties>
```

**Mapeo de versiones de schema:**
| Schema    | Versión Prime |
|-----------|---------------|
| schema50  | 1.0 - 4.0     |
| schema60  | 5.0           |
| schema70  | 6.0           |
| schema80  | 7.0           |
| schema90  | 8.0           |
| schema100 | 9.0           |
| schema110 | 10.0+         |

---

## Tipos de Regiones

Cada `<region>` en worksheet.xml puede contener diferentes tipos de contenido:

### 1. Región de Texto (`<text>`)
```xml
<region region-id="0">
  <text item-idref="R85b85e4f76354d9c">
    <FlowDocument FontFamily="Euclid" FontSize="14.6666">
      <!-- Contenido en XAML referenciado por item-idref -->
    </FlowDocument>
  </text>
</region>
```

### 2. Región Matemática (`<math>`)
```xml
<region region-id="1">
  <math resultRef="0">
    <ml:define>
      <ml:id>x</ml:id>
      <ml:real>5</ml:real>
    </ml:define>
  </math>
</region>
```

### 3. Tabla de Especificaciones (`<spec-table>`)
Para múltiples definiciones agrupadas:
```xml
<region region-id="2">
  <spec-table>
    <math resultRef="0">
      <ml:define>...</ml:define>
    </math>
    <math resultRef="1">
      <ml:define>...</ml:define>
    </math>
  </spec-table>
</region>
```

### 4. Imagen (`<picture>`)
```xml
<region region-id="3">
  <picture>
    <png item-idref="R91ba0f034d3b43e9"
         display-width="329.53"
         display-height="224.39" />
  </picture>
</region>
```

### 5. Gráfica Normal (`<plot>`)
```xml
<region region-id="4">
  <plot origin-positioning="true">
    <xyPlot>
      <!-- Ver sección de gráficas -->
    </xyPlot>
  </plot>
</region>
```

### 6. Gráfica MathChart (`<chartComponent>`)
```xml
<region region-id="5">
  <chartComponent resultRef="16">
    <regions>
      <!-- Definiciones de series X[n], Y[n] -->
    </regions>
  </chartComponent>
</region>
```

### 7. Bloque de Resolución (`<solveblock>`)
```xml
<region region-id="6">
  <solveblock>
    <regions>
      <!-- Restricciones y solver -->
    </regions>
  </solveblock>
</region>
```

---

## Gráficas: xyPlot vs chartComponent

### **TIPO 1: xyPlot (Gráfica Normal)**

Se usa para gráficas simples con datos de vectores definidos previamente.

```xml
<plot origin-positioning="true">
  <xyPlot>
    <title>Mi Gráfica</title>
    <legend />

    <traces>
      <trace resultRef="2">
        <traceStyle
          color="#FF00008B"      <!-- AARRGGBB -->
          symbol="none"          <!-- none, circle, square, diamond... -->
          line-weight="1"        <!-- Grosor de línea -->
          line-style="Solid">    <!-- Solid, Dash, Dot, DashDot -->
          lines                  <!-- Modo: lines, points, both -->
        </traceStyle>
      </trace>
    </traces>

    <graph-size width="230.4" height="230.4" />

    <axes>
      <xAxis rank="1"
             legend-position="PlotBoundaryBottom"
             start="2" end="6">
        <axisLine position="bottom" />
        <axisGrid>
          <gridFrequency>11</gridFrequency>
          <gridLabels display="true" />
          <tickMarks display="true" />
        </axisGrid>
        <plotEquations>
          <plotEquation>
            <math><ml:id>x</ml:id></math>  <!-- Variable X -->
          </plotEquation>
        </plotEquations>
        <xyDomain scale-type="linear" auto-scale="true" />
      </xAxis>

      <yAxis rank="1" start="17500" end="45000">
        <plotEquations>
          <plotEquation>
            <math><ml:id>F</ml:id></math>  <!-- Variable Y -->
          </plotEquation>
        </plotEquations>
      </yAxis>
    </axes>
  </xyPlot>
</plot>
```

**Características de xyPlot:**
- Variables definidas fuera del plot (x, F)
- Configuración visual en XML
- Fácil de parsear
- Una trace por serie

### **TIPO 2: chartComponent (MathChart)**

Se usa para gráficas avanzadas con múltiples series, derivadas, y configuración visual compleja.

```xml
<chartComponent resultRef="16">
  <regions>
    <!-- Definición de Serie 1 -->
    <region region-id="24">
      <math resultRef="10">
        <ml:define>
          <ml:apply>
            <ml:indexer />
            <ml:id labels="*">X</ml:id>
            <ml:real>1</ml:real>
          </ml:apply>
          <ml:id labels="VARIABLE">t'</ml:id>  <!-- X[1] := t' -->
        </ml:define>
      </math>
    </region>

    <region region-id="25">
      <math resultRef="11">
        <ml:define>
          <ml:apply>
            <ml:indexer />
            <ml:id labels="*">Y</ml:id>
            <ml:real>1</ml:real>
          </ml:apply>
          <ml:apply>
            <ml:div />
            <ml:apply>
              <ml:id>x_a</ml:id>      <!-- Función -->
              <ml:id>t'</ml:id>       <!-- Argumento -->
            </ml:apply>
            <ml:id labels="UNIT">mm</ml:id>  <!-- Y[1] := x_a(t')/mm -->
          </ml:apply>
        </ml:define>
      </math>
    </region>

    <!-- Más series X[2], Y[2], X[3], Y[3]... -->

    <!-- Objeto OLE con la gráfica renderizada -->
    <region region-id="30">
      <chartOleObject item-idref="R6011d9ed3c95494c">
        <OleViewportSize width="443.18" height="244.8" />
        <SizeInPixels width="899" height="494" />
      </chartOleObject>
    </region>
  </regions>

  <InputSection Visibility="Collapsed" Height="188.97" />
</chartComponent>
```

**Características de chartComponent:**
- Series definidas como `X[n]`, `Y[n]`
- Soporta derivadas (`functionDerivative`)
- Configuración visual en archivo OLE (binario)
- Se edita con PTC Mathcad Chart (aplicación externa)
- Más complejo de parsear

### **Tabla Comparativa**

| Aspecto | xyPlot | chartComponent |
|---------|--------|----------------|
| Elemento raíz | `<plot><xyPlot>` | `<chartComponent>` |
| Datos | Variables directas | Series X[n], Y[n] |
| Config. visual | En XML | En OLE binario |
| Multi-serie | Una por trace | Múltiples Y[n] |
| Derivadas | No | Sí |
| Archivo extra | Ninguno | chart/chartNN.ole |
| Edición | Mathcad Prime | Mathcad Chart |

---

## Expresiones Matemáticas

### Estructura de `<ml:define>` (Asignación)

```xml
<ml:define>
  <ml:id>nombre_variable</ml:id>   <!-- Lado izquierdo -->
  <ml:real>valor</ml:real>          <!-- Lado derecho -->
</ml:define>
```

### Elementos Matemáticos Comunes

| Elemento | Descripción | Ejemplo XML |
|----------|-------------|-------------|
| `<ml:id>` | Identificador | `<ml:id>x</ml:id>` |
| `<ml:real>` | Número real | `<ml:real>3.14159</ml:real>` |
| `<ml:str>` | Cadena de texto | `<ml:str>hello</ml:str>` |
| `<ml:matrix>` | Matriz/Vector | Ver sección |
| `<ml:apply>` | Aplicar operador | Ver sección |
| `<ml:parens>` | Paréntesis | `<ml:parens>...</ml:parens>` |
| `<ml:sequence>` | Secuencia de args | `<ml:sequence>a, b, c</ml:sequence>` |
| `<ml:placeholder>` | Placeholder vacío | `<ml:placeholder />` |

### Operadores en `<ml:apply>`

```xml
<ml:apply>
  <ml:plus />        <!-- Primer hijo: operador -->
  <ml:id>a</ml:id>   <!-- Segundo hijo: operando 1 -->
  <ml:id>b</ml:id>   <!-- Tercer hijo: operando 2 -->
</ml:apply>
```

**Operadores disponibles:**
| Operador | Símbolo | Resultado |
|----------|---------|-----------|
| `<ml:plus />` | + | a + b |
| `<ml:minus />` | - | a - b |
| `<ml:mult />` | × | a * b |
| `<ml:div />` | ÷ | a / b |
| `<ml:pow />` | ^ | a^b |
| `<ml:equal />` | = | a = b (ecuación) |
| `<ml:scale />` | · | valor · unidad |
| `<ml:indexer />` | [] | X[1] |
| `<ml:functionDerivative />` | d/dt | derivada |

### Funciones Matemáticas

```xml
<ml:apply>
  <ml:id>sin</ml:id>    <!-- Nombre de función -->
  <ml:id>x</ml:id>      <!-- Argumento -->
</ml:apply>
```

**Funciones comunes:**
- Trigonométricas: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
- Hiperbólicas: `sinh`, `cosh`, `tanh`
- Exponenciales: `exp`, `ln`, `log`
- Otras: `sqrt` → `sqr` en Calcpad, `abs`, `floor`, `ceil`

### Subíndices en Variables

```xml
<ml:id>
  <Span xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation">
    x<pw:Subscript>0</pw:Subscript>
  </Span>
</ml:id>
```
Resultado: x₀

---

## Unidades y Escalado

### Formato de Unidad con `<ml:scale>`

```xml
<ml:apply>
  <ml:scale />
  <ml:real>100</ml:real>              <!-- Valor numérico -->
  <ml:id labels="UNIT">kN</ml:id>     <!-- Unidad -->
</ml:apply>
```
Resultado: `100'kN` en Calcpad

### Unidades Compuestas

```xml
<ml:apply>
  <ml:scale />
  <ml:real>9.81</ml:real>
  <ml:apply>
    <ml:div />
    <ml:id labels="UNIT">m</ml:id>
    <ml:apply>
      <ml:pow />
      <ml:id labels="UNIT">s</ml:id>
      <ml:real>2</ml:real>
    </ml:apply>
  </ml:apply>
</ml:apply>
```
Resultado: `9.81'm/s^2` en Calcpad

---

## Matrices y Vectores

### Almacenamiento en Orden de Columnas (Column-Major)

Mathcad almacena matrices en **orden de columnas**, no de filas:

```xml
<ml:matrix rows="2" cols="3">
  <ml:real>1</ml:real>    <!-- M[0,0] -->
  <ml:real>2</ml:real>    <!-- M[1,0] -->
  <ml:real>3</ml:real>    <!-- M[0,1] -->
  <ml:real>4</ml:real>    <!-- M[1,1] -->
  <ml:real>5</ml:real>    <!-- M[0,2] -->
  <ml:real>6</ml:real>    <!-- M[1,2] -->
</ml:matrix>
```

**Matriz resultante:**
```
| 1  3  5 |
| 2  4  6 |
```

### Conversión a Calcpad

**Vector columna** (cols=1):
```xml
<ml:matrix rows="3" cols="1">
  <ml:real>10</ml:real>
  <ml:real>20</ml:real>
  <ml:real>30</ml:real>
</ml:matrix>
```
Resultado Calcpad: `[10; 20; 30]`

**Matriz general:**
```
Calcpad: [fila1_col1; fila1_col2 | fila2_col1; fila2_col2]
         [1; 3; 5 | 2; 4; 6]
```

### Fórmula de Conversión

```
índice_xml = columna * filas + fila
índice_calcpad = fila * columnas + columna
```

---

## Imágenes y Media

### Localizar Imágenes

1. Buscar `<picture>` en worksheet.xml:
```xml
<picture>
  <png item-idref="R91ba0f034d3b43e9"
       display-width="329.53"
       display-height="224.39" />
</picture>
```

2. Buscar el ID en worksheet.xml.rels:
```xml
<Relationship
  Type=".../image"
  Target="/mathcad/media/Image3.png"
  Id="R91ba0f034d3b43e9" />
```

3. Extraer la imagen de `mathcad/media/Image3.png`

### Formatos Soportados

- PNG (más común)
- JPEG
- BMP
- GIF
- EMF (Enhanced Metafile)

### Conversión a Base64

Para embeber en Calcpad:
```csharp
byte[] imageBytes = File.ReadAllBytes(imagePath);
string base64 = Convert.ToBase64String(imageBytes);
string format = Path.GetExtension(imagePath).TrimStart('.');

// Formato Calcpad:
// @{image png base64}
// [datos base64]
// @{end image}
```

---

## Ejemplos Prácticos

### Ejemplo 1: Leer una Definición Simple

**XML:**
```xml
<math resultRef="0">
  <ml:define>
    <ml:id>x</ml:id>
    <ml:real>5</ml:real>
  </ml:define>
</math>
```

**Código C#:**
```csharp
var define = math.Descendants(_mlNs + "define").First();
var varName = define.Elements().First().Value;  // "x"
var value = define.Elements().Last().Value;      // "5"
// Resultado: x = 5
```

### Ejemplo 2: Leer un Vector con Unidad

**XML:**
```xml
<ml:define>
  <ml:id>F</ml:id>
  <ml:apply>
    <ml:scale />
    <ml:matrix rows="3" cols="1">
      <ml:real>2</ml:real>
      <ml:real>3</ml:real>
      <ml:real>5</ml:real>
    </ml:matrix>
    <ml:id labels="UNIT">tonf</ml:id>
  </ml:apply>
</ml:define>
```

**Código C#:**
```csharp
// Detectar scale
var apply = define.Elements().Last();
var scale = apply.Elements().First(); // <ml:scale />
var matrix = apply.Elements().ElementAt(1);
var unit = apply.Elements().Last();

// Extraer valores de matriz
var values = matrix.Elements()
    .Where(e => e.Name.LocalName == "real")
    .Select(e => e.Value)
    .ToList();

// Resultado: F = [2; 3; 5]'tonf
```

### Ejemplo 3: Detectar Tipo de Gráfica

**Código C#:**
```csharp
public string DetectPlotType(XElement region)
{
    // xyPlot: gráfica normal
    if (region.Descendants().Any(e => e.Name.LocalName == "xyPlot"))
        return "xyPlot";

    // chartComponent: MathChart avanzado
    if (region.Descendants().Any(e => e.Name.LocalName == "chartComponent"))
        return "chartComponent";

    return "none";
}
```

### Ejemplo 4: Extraer Series de chartComponent

**Código C#:**
```csharp
public void ExtractChartSeries(XElement chartComponent)
{
    var regions = chartComponent.Descendants()
        .Where(e => e.Name.LocalName == "region");

    foreach (var region in regions)
    {
        var define = region.Descendants()
            .FirstOrDefault(e => e.Name.LocalName == "define");

        if (define == null) continue;

        var leftSide = define.Elements().First();

        // Verificar si es X[n] o Y[n]
        if (leftSide.Name.LocalName == "apply")
        {
            var op = leftSide.Elements().First();
            if (op.Name.LocalName == "indexer")
            {
                var axis = leftSide.Elements().ElementAt(1).Value; // "X" o "Y"
                var index = leftSide.Elements().ElementAt(2).Value; // "1", "2"...

                var expression = ExtractExpression(define.Elements().Last());

                Console.WriteLine($"{axis}[{index}] := {expression}");
            }
        }
    }
}
```

---

## Herramientas Útiles

### Script Python para Analizar MCDX

```python
import zipfile
import xml.etree.ElementTree as ET
import json

def analyze_mcdx(mcdx_path):
    """Analiza un archivo MCDX y muestra su estructura"""

    namespaces = {
        'ws': 'http://schemas.mathsoft.com/worksheet50',
        'ml': 'http://schemas.mathsoft.com/math50'
    }

    with zipfile.ZipFile(mcdx_path, 'r') as zf:
        # Leer worksheet.xml
        with zf.open('mathcad/worksheet.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()

        # Contar tipos de regiones
        stats = {
            'text': 0,
            'math': 0,
            'plot': 0,
            'chartComponent': 0,
            'picture': 0,
            'solveblock': 0,
            'spec-table': 0
        }

        for region in root.iter():
            if 'region' in region.tag:
                for child in region:
                    local_name = child.tag.split('}')[-1]
                    if local_name in stats:
                        stats[local_name] += 1

        return stats

# Uso
stats = analyze_mcdx("archivo.mcdx")
print(json.dumps(stats, indent=2))
```

### Comando para Ver Estructura

```bash
# Linux/Mac
unzip -l archivo.mcdx

# Windows PowerShell
$zip = [System.IO.Compression.ZipFile]::OpenRead("archivo.mcdx")
$zip.Entries | Format-Table FullName, Length
$zip.Dispose()
```

---

## Referencias

- **Mathcad Prime Documentation**: [PTC Support](https://support.ptc.com/help/mathcad/)
- **Open Packaging Conventions**: [ECMA-376](https://www.ecma-international.org/publications-and-standards/standards/ecma-376/)
- **McdxConverter.cs**: Implementación de referencia en Calcpad

---

## Historial de Cambios

| Fecha | Versión | Cambios |
|-------|---------|---------|
| 2026-01-25 | 1.0 | Versión inicial con soporte xyPlot y chartComponent |

---

*Documento creado para el proyecto Calcpad - Conversor MCDX*
