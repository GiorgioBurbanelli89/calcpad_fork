# Convertidor de DOCX a CPD - Calcpad CLI

## Descripción

El convertidor de DOCX a CPD es una nueva funcionalidad en Calcpad CLI que permite importar documentos de Microsoft Word (.docx) y convertirlos automáticamente al formato de Calcpad (.cpd).

## Archivos Implementados

### 1. `Calcpad.Common/DocxConverter.cs`
- **Ubicación**: `Calcpad.Common/DocxConverter.cs`
- **Descripción**: Clase que maneja la conversión de archivos DOCX a formato CPD
- **Funcionalidad**:
  - Extrae contenido de documentos DOCX (texto, formato, estructura)
  - Identifica encabezados, texto en negrita, ecuaciones matemáticas
  - Convierte unidades comunes a formato Calcpad
  - Preserva la estructura del documento original
  - Genera código Calcpad limpio y organizado

### 2. `Calcpad.Cli/Program.cs` (Modificado)
- **Cambios**:
  - Agregado soporte para archivos `.docx` como entrada
  - Opción `-cpd` para convertir DOCX → CPD sin procesar
  - Integración con el flujo de conversión existente (similar a .mcdx, .xlsx, .sm)

## Uso del Convertidor

### Sintaxis Básica

```bash
# Convertir DOCX a CPD (solo conversión)
Cli.exe "documento.docx" -cpd

# Especificar archivo de salida
Cli.exe "documento.docx" "salida.cpd" -cpd

# Convertir DOCX a HTML (procesa con motor de Calcpad)
Cli.exe "documento.docx" "salida.html"

# Modo silencioso (sin mensajes de progreso)
Cli.exe "documento.docx" -cpd -s
```

### Ejemplos

#### Ejemplo 1: Conversión Simple
```bash
cd Calcpad.Cli/bin/Debug/net10.0
./Cli.exe "Examples/Demos/Beam design with Markdown.docx" -cpd
```

**Salida**: `Examples/Demos/Beam design with Markdown.cpd`

#### Ejemplo 2: Conversión con Archivo de Salida Personalizado
```bash
./Cli.exe "mi_documento.docx" "resultado_final.cpd" -cpd
```

#### Ejemplo 3: Conversión y Procesamiento a HTML
```bash
./Cli.exe "calculo_estructural.docx" "calculo_estructural.html"
```

## Características del Convertidor

### 1. Extracción de Estructura
- **Encabezados**: Se convierten a títulos de sección con comillas (`"TÍTULO`)
- **Texto en negrita**: Se convierte a subtítulos con apóstrofe (`'Subtítulo`)
- **Texto normal**: Se convierte a comentarios (`'Texto explicativo`)

### 2. Detección de Ecuaciones
El convertidor intenta identificar expresiones matemáticas y convertirlas a formato Calcpad:
- Operadores: `+`, `-`, `*`, `/`, `^`
- Funciones: `sqrt()` → `sqr()`, `sin()`, `cos()`, `tan()`, `log()` → `ln()`
- Notación científica: `1.5E-2` → `0.015`

### 3. Conversión de Unidades
El convertidor reconoce y convierte unidades comunes:
- Longitud: `m`, `cm`, `mm`, `km`
- Área: `m2`, `m²` → `m^2`
- Volumen: `m3`, `m³` → `m^3`
- Fuerza: `N`, `kN`, `MN`
- Presión: `Pa`, `kPa`, `MPa`, `GPa`
- Ángulos: `deg` → `°`, `rad`

### 4. Detección de Definiciones
El convertidor identifica definiciones de variables con formato:
```
variable = valor unidad
```

Ejemplo:
```
Entrada DOCX: "h = 25 cm"
Salida CPD:   h = 25cm
```

## Formato del Archivo CPD Generado

El archivo CPD generado tiene la siguiente estructura:

```calcpad
' ============================================
' Importado de Word (.docx)
' Versión: Microsoft Office Word
' Archivo: documento.docx
' Fecha: 2026-01-24 12:48:43
' Título: Título del Documento
' ============================================

"SECCIÓN PRINCIPAL
'Descripción de la sección

'Subtítulo
'Texto explicativo

variable1 = 100
variable2 = 25cm
resultado = variable1 + variable2
```

## Limitaciones y Consideraciones

### Limitaciones Actuales
1. **Ecuaciones de Word**: Las ecuaciones insertadas con el editor de ecuaciones de Word no se extraen (solo aparecen como placeholders)
2. **Tablas Complejas**: Las tablas se convierten a HTML embebido, no a código Calcpad
3. **Imágenes**: Las imágenes se incluyen como base64 en HTML, aumentando el tamaño del archivo
4. **Formato Avanzado**: Color de texto, fuentes especiales, y otros formatos avanzados se pierden

### Recomendaciones
- Para mejor conversión, use texto plano con ecuaciones escritas en formato matemático estándar
- Mantenga la estructura del documento simple (encabezados, subtítulos, párrafos)
- Use texto en negrita para resaltar títulos importantes
- Escriba ecuaciones en formato lineal (ej: `x = (a + b) / 2` en lugar de fracciones visuales)

## Comparación con Otros Convertidores

| Característica | DOCX → CPD | MCDX → CPD | XLSX → CPD | SM → CPD |
|---------------|------------|------------|------------|----------|
| Ecuaciones matemáticas | ⚠️ Limitado | ✅ Completo | ✅ Completo | ✅ Completo |
| Estructura de documento | ✅ Bueno | ✅ Bueno | ✅ Bueno | ✅ Bueno |
| Unidades | ✅ Automático | ✅ Automático | ✅ Automático | ✅ Automático |
| Tablas | ⚠️ HTML | ⚠️ HTML | ✅ Código | ⚠️ HTML |
| Imágenes | ✅ Base64 | ✅ Base64 | ❌ No | ✅ Base64 |

## Flujo de Conversión

```
DOCX (Word Document)
    ↓
[DocxConverter.Convert()]
    ↓
Extrae XML del ZIP
    ↓
Parsea document.xml
    ↓
Identifica estructura (encabezados, párrafos, tablas)
    ↓
Convierte a formato Calcpad
    ↓
Genera archivo .cpd
    ↓
CPD (Calcpad Document)
```

## Desarrollo Futuro

### Mejoras Planeadas
1. **Soporte para ecuaciones de Word** usando Office Math ML
2. **Conversión de tablas** a código Calcpad en lugar de HTML
3. **Detección mejorada de variables** y definiciones
4. **Optimización de imágenes** (compresión, redimensionamiento)
5. **Soporte para estilos personalizados** de usuario

### Cómo Contribuir
Si desea mejorar el convertidor:
1. Modifique `Calcpad.Common/DocxConverter.cs`
2. Agregue pruebas en la carpeta `Calcpad.Tests/`
3. Compile y pruebe con `dotnet build` y `dotnet test`

## Ejemplos de Uso Avanzado

### Conversión en Batch
```powershell
# PowerShell: Convertir todos los DOCX de un directorio
Get-ChildItem -Path ".\docs" -Filter "*.docx" | ForEach-Object {
    ./Cli.exe $_.FullName -cpd
}
```

```bash
# Bash: Convertir todos los DOCX
for file in docs/*.docx; do
    ./Cli.exe "$file" -cpd
done
```

### Integración en Scripts
```python
# Python: Automatizar conversión
import subprocess
import os

docx_files = [f for f in os.listdir(".") if f.endswith(".docx")]
for docx in docx_files:
    subprocess.run(["./Cli.exe", docx, "-cpd"])
```

## Troubleshooting

### Problema: "No se encontró document.xml"
**Solución**: El archivo DOCX está corrupto. Intente abrirlo en Word y guardarlo nuevamente.

### Problema: "Error extrayendo texto"
**Solución**: El documento puede tener protección. Remueva la protección en Word antes de convertir.

### Problema: Ecuaciones no se convierten correctamente
**Solución**: Las ecuaciones de Word no son compatibles actualmente. Reescriba las ecuaciones como texto matemático lineal.

### Problema: Archivo CPD muy grande
**Solución**: El documento tiene muchas imágenes. Considere reducir el número de imágenes o su resolución.

## Referencias

- Documentación de Calcpad: [docs/calcpad-readme.docx](docs/calcpad-readme.docx)
- OpenXML SDK: [DocumentFormat.OpenXml](https://github.com/OfficeDev/Open-XML-SDK)
- Formato de archivo DOCX: [Office Open XML](https://en.wikipedia.org/wiki/Office_Open_XML)

## Licencia

Este convertidor es parte de Calcpad y está sujeto a la misma licencia que el proyecto principal.

## Contacto y Soporte

Para reportar problemas o sugerir mejoras:
- GitHub Issues: [https://github.com/Proektsoftbg/Calcpad](https://github.com/Proektsoftbg/Calcpad)
- Documentación: Ver archivos en la carpeta `Help/`

---

**Nota**: Este convertidor está en versión inicial. Se recomienda revisar manualmente los archivos CPD generados para verificar que las ecuaciones y la estructura se hayan convertido correctamente.
