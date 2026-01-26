# PROMPT PARA CONTINUAR - Convertidor MCDX a CPD y SMath Studio

## Contexto del Proyecto

**Ubicación**: `C:\Users\j-b-j\Documents\Calcpad-7.5.7`
**Versión actual**: 1.0.4
**Instalador generado**: `Installer/CalcpadFork-Setup-1.0.4.exe`

---

## TAREA PRINCIPAL: Mejorar Convertidor .mcdx → .cpd

### Archivo de prueba complejo
```
C:\Users\j-b-j\Downloads\Clase 06_Ensamblaje_Placas_gruesas (1).mcdx
```
(694 KB - contiene matrices complejas, fórmulas avanzadas de FEM placas gruesas)

### Archivos del convertidor actual

1. **Conversor Mathcad Prime**:
   - `Calcpad.Common/McdxConverter.cs` - Clase principal
   - Lee archivos .mcdx (ZIP con XML interno)
   - Convierte expresiones matemáticas a sintaxis Calcpad

2. **Conversor SMath Studio**:
   - `Calcpad.Common/SMathConverter.cs` - Clase principal
   - Lee archivos .sm (XML)
   - Convierte expresiones SMath a Calcpad

3. **Lector de archivos**:
   - `Calcpad.Common/CalcpadReader.cs` - Procesa directivas @{mathcad:} y @{smath:}

### Problemas conocidos del convertidor MCDX

El archivo `Clase 06_Ensamblaje_Placas_gruesas.mcdx` es más complejo y puede tener:
- Matrices grandes con subíndices
- Funciones personalizadas
- Gráficos 2D/3D
- Regiones de texto con formato
- Operadores especiales de FEM

### Cómo probar el convertidor

```bash
# Desde CLI
cd C:\Users\j-b-j\Documents\Calcpad-7.5.7
dotnet run --project Calcpad.Cli -- "C:\Users\j-b-j\Downloads\Clase 06_Ensamblaje_Placas_gruesas (1).mcdx" -cpd

# O abrir el archivo directamente en Calcpad WPF
```

---

## Archivos C++ de Mathcad CustomFunctions (para DLLs)

**Ubicación**: `C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests\`

### Archivos principales:
- `Tests/mathcad_fem.cpp` - DLL FEM principal
- `Tests/mathcad_fem/mathcad_fem.cpp` - Versión alternativa
- `Tests/mathcad_fem/mathcad_fem.C` - Código fuente C
- `Tests/verify_fem_beam.cpp` - Verificación vigas FEM
- `Tests/verify_triangle.cpp` - Verificación triángulos
- `Tests/plate_fem_example.cpp` - Ejemplo placas FEM

### DLL compilada:
- `Tests/mathcad_fem.dll`

### Scripts de compilación:
- `Tests/mathcad_fem/compile.bat`
- `Tests/COMPILE_MATHCAD_FEM.bat`

### Documentación:
- `Tests/MATHCAD_CUSTOM_FUNCTIONS_GUIDE.md`
- `Tests/COMO_CARGAR_DLLS_EN_CALCPAD.md`

---

## Cambios recientes (v1.0.4)

### Formateo de Vectores/Matrices
Los vectores y matrices ahora se muestran con formato visual (bordes) en lugar de texto plano.

**Archivos modificados**:
- `Calcpad.Core/Output/OutputWriter.cs` - Métodos FormatVectorExpression/FormatMatrixExpression
- `Calcpad.Core/Output/HtmWriter.cs` - HTML con clase .matrix
- `Calcpad.Core/Output/TextWriter.cs` - Texto plano
- `Calcpad.Core/Output/XmlWriter.cs` - XML para Word
- `Calcpad.Core/Parsers/MathParser/MathParser.Output.cs` - RenderVectorToken/RenderMatrixToken

**CSS del template**: `Calcpad.Wpf/doc/template.html` (clases .matrix, .tr, .td líneas 200-240)

---

## Pasos sugeridos

1. **Analizar el archivo MCDX complejo**:
   ```bash
   # Extraer y ver estructura
   unzip -l "C:\Users\j-b-j\Downloads\Clase 06_Ensamblaje_Placas_gruesas (1).mcdx"
   ```

2. **Identificar elementos no soportados**:
   - Ver warnings del convertidor actual
   - Comparar output con original

3. **Mejorar McdxConverter.cs**:
   - Agregar soporte para nuevos elementos
   - Mejorar parsing de matrices complejas
   - Manejar funciones especiales de FEM

4. **Probar con SMath Studio**:
   - El mismo archivo puede existir en formato .sm
   - Verificar compatibilidad cruzada

---

## Commits recientes

```
c058f0a build: Update to v1.0.4 with vector/matrix formatting
8050db4 feat: Format vectors/matrices with matrix style in all output modes
56f5c7e feat: Add inline import directives for Mathcad and SMath files
0c8fb79 feat: Add Mathcad Prime and SMath Studio import/export support
```

---

## Notas adicionales

- El template.html controla TODO el formateo visual en el WebView2
- Los conversores generan código Calcpad puro (.cpd)
- Las DLLs de C++ son para funciones personalizadas que se pueden llamar desde Calcpad
