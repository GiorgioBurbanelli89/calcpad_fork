# Plan de Implementación: Editor Visual MathCad Prime

## 🎯 Objetivo
Crear un editor visual completo para archivos .mcdx (MathCad Prime) integrado en Calcpad,
similar al MathCad Prime original, con rejilla editable y todas las funcionalidades.

## 📋 Análisis Actual

### Recursos Disponibles
1. **MathEditor existente** (`Calcpad.Wpf/MathEditor/`) - Base funcional
2. **McdxConverter** (`Calcpad.Common/McdxConverter.cs`) - Lee archivos .mcdx
3. **Archivo de ejemplo**: `Modos de vibracion.mcdx` - Análisis modal
4. **PDF de referencia**: Muestra cómo debe verse el resultado

### Estructura del archivo .mcdx
```
mcdx (ZIP)
├── mathcad/
│   ├── worksheet.xml          ← DOCUMENTO PRINCIPAL
│   ├── xaml/FlowDocument*.XamlPackage
│   ├── media/Image*.png
│   ├── settings/
│   │   ├── calculation.xml
│   │   └── presentation.xml
│   ├── result.xml
│   └── _rels/worksheet.xml.rels
├── docProps/
│   ├── core.xml
│   └── app.xml
└── [Content_Types].xml
```

### Estructura de worksheet.xml
```xml
<worksheet>
  <regions>
    <region region-id="0" top="18.89" left="18.89" width="622.66">
      <text>...</text>  ← Texto/Comentario
    </region>
    <region region-id="3" top="198.42" left="0">
      <math resultRef="0">  ← Ecuación Matemática
        <ml:define>...</ml:define>
      </math>
    </region>
    <region region-id="2" top="85.03" left="425.19">
      <picture>...</picture>  ← Imagen/Gráfico
    </region>
  </regions>
</worksheet>
```

## 🚀 Plan de Implementación

### FASE 1: Editor Base con Rejilla ✨
**Archivo**: `Calcpad.Wpf/MathcadPrimeEditor/MathcadPrimeEditorControl.xaml`

#### Características:
- ✅ Canvas infinito con rejilla visible (grid lines)
- ✅ Zoom (25% - 400%)
- ✅ Reglas horizontales y verticales (en puntos/cm)
- ✅ Snap-to-grid opcional
- ✅ Indicador de posición del cursor

#### Layout:
```
┌─────────────────────────────────────────┐
│ [Toolbar: Nuevo | Abrir | Guardar]     │
├─────┬───────────────────────────────────┤
│  R  │  ┌──────────────────────────┐    │
│  u  │  │                          │    │
│  l  │  │    Canvas con Rejilla    │    │
│  e  │  │      (Regiones)          │    │
│  r  │  │                          │    │
│     │  └──────────────────────────┘    │
│     │         Ruler Horizontal         │
└─────┴───────────────────────────────────┘
```

### FASE 2: Regiones Editables 📝
**Archivo**: `MathcadRegion.cs`

#### Tipos de Regiones:
1. **TextRegion** - Texto/Comentarios (FlowDocument)
2. **MathRegion** - Ecuaciones (Editor matemático)
3. **ImageRegion** - Gráficos/Imágenes
4. **PlotRegion** - Gráficos 2D/3D (futuro)

#### Funciones por Región:
- Mover (drag & drop)
- Redimensionar (handles en bordes)
- Editar contenido (doble click)
- Eliminar (Delete)
- Copiar/Pegar (Ctrl+C/V)
- Propiedades (click derecho)

### FASE 3: Editor Matemático Avanzado 🧮
**Archivo**: `MathcadMathRegionEditor.xaml`

#### Elementos Matemáticos:
- ✅ Definiciones: `Mm := [matriz]`
- ✅ Evaluaciones: `w = sqrt(w2)`
- ✅ Matrices: Editor visual de matrices
- ✅ Vectores: Editor de vectores
- ✅ Funciones: `eigenvals()`, `eigenvec()`, `sort()`
- ✅ Operadores: `+`, `-`, `*`, `/`, `^`, `√`
- ✅ Subíndices/Superíndices
- ✅ Integrales, Derivadas, Sumatorias

#### Sintaxis MathCad:
```
Mm := [matriz 9x9]           ← Definición
λ := Mm^(-1) * KEDIFICIO     ← Operación
w2 := sort(eigenvals(λ))     ← Función
w := √w2                     ← Raíz
Te := (2·π)/w                ← División
```

### FASE 4: Lectura y Escritura .mcdx 💾
**Archivos**:
- `McdxReader.cs` (ya existe en McdxConverter)
- `McdxWriter.cs` (nuevo)

#### Lectura (McdxReader):
1. Descomprimir ZIP
2. Parsear worksheet.xml
3. Extraer regiones
4. Cargar al Canvas

#### Escritura (McdxWriter):
1. Serializar regiones a XML
2. Generar worksheet.xml
3. Crear estructura ZIP
4. Guardar como .mcdx

### FASE 5: Barra de Herramientas 🛠️
**Archivo**: `MathcadPrimeToolbar.xaml`

#### Herramientas:
```
[Archivo]  [Editar]  [Insertar]  [Formato]  [Calcular]  [Vista]

Insertar:
- 📝 Región de Texto
- 🧮 Región Matemática
- 🖼️ Imagen
- 📊 Gráfico (futuro)
- ➕ Matriz
- ➕ Vector

Calcular:
- ▶️ Calcular Todo
- ⏸️ Calcular Hasta Aquí
- 🔄 Recalcular
```

### FASE 6: Integración con MainWindow 🔗
**Archivo**: `Calcpad.Wpf/MainWindow.xaml.cs`

#### Botón en Toolbar:
```xml
<Button Click="OpenMathcadPrimeEditor_Click">
  <Image Source="mathcad_icon.png"/>
  <TextBlock>MathCad Prime</TextBlock>
</Button>
```

#### Comando CLI:
```bash
Cli.exe --mathcad archivo.mcdx
```

## 📁 Estructura de Archivos

```
Calcpad.Wpf/
├── MathcadPrimeEditor/
│   ├── MathcadPrimeEditorControl.xaml      ← Editor principal
│   ├── MathcadPrimeEditorControl.xaml.cs
│   ├── MathcadPrimeEditorWindow.xaml       ← Ventana standalone
│   ├── MathcadPrimeEditorWindow.xaml.cs
│   ├── Models/
│   │   ├── MathcadRegion.cs                ← Clase base región
│   │   ├── TextRegion.cs
│   │   ├── MathRegion.cs
│   │   └── ImageRegion.cs
│   ├── Controls/
│   │   ├── GridCanvas.cs                   ← Canvas con rejilla
│   │   ├── MathcadToolbar.xaml
│   │   ├── MathRegionEditor.xaml           ← Editor matemático
│   │   └── MatrixEditor.xaml               ← Editor de matrices
│   └── Utils/
│       ├── McdxWriter.cs                   ← Escritura .mcdx
│       └── RegionSerializer.cs

Calcpad.Common/
├── McdxConverter.cs                         ← Ya existe (leer)
└── McdxWriter.cs                            ← Nuevo (escribir)
```

## 🎨 Diseño Visual

### Rejilla (Grid)
- **Líneas principales**: Cada 50 px (gris #CCCCCC)
- **Líneas secundarias**: Cada 10 px (gris claro #EEEEEE)
- **Snap tolerance**: 5 px
- **Colores**: Fondo blanco #FFFFFF

### Regiones
- **Borde**: Azul claro #1976D2 cuando seleccionada
- **Handles**: Círculos azules en esquinas
- **Hover**: Borde gris #CCCCCC
- **Fondo**: Blanco transparente

### Toolbar
- **Altura**: 40px
- **Iconos**: 24x24px
- **Separadores**: Línea vertical gris

## 🧪 Casos de Uso

### Caso 1: Abrir archivo .mcdx existente
1. Usuario: Click en botón "Abrir MathCad"
2. Sistema: Muestra diálogo de archivo
3. Usuario: Selecciona `Modos de vibracion.mcdx`
4. Sistema:
   - Descomprime .mcdx
   - Parsea worksheet.xml
   - Crea regiones en canvas
   - Muestra editor con contenido

### Caso 2: Crear nuevo documento
1. Usuario: Click en "Nuevo MathCad"
2. Sistema: Abre editor vacío con rejilla
3. Usuario: Inserta región matemática
4. Usuario: Escribe `Mm := [9x9 matrix]`
5. Sistema: Renderiza ecuación
6. Usuario: Guarda como .mcdx

### Caso 3: Editar ecuación
1. Usuario: Doble click en región matemática
2. Sistema: Abre editor de ecuaciones
3. Usuario: Modifica `w2 := sort(eigenvals(λ))`
4. Usuario: Presiona Enter
5. Sistema: Recalcula y actualiza resultado

## 📊 Ejemplo del PDF

```
Región 0 (Texto):
  "Ejemplo 22: Vectores y valores propios"

Región 3 (Math):
  Mm := [matriz 9x9 con valores]

Región 2 (Image):
  [Estructura 3D del edificio]

Región 9 (Math):
  λ := Mm^(-1) · KEDIFICIO

Región 10 (Math):
  w2 := sort(eigenvals(λ))

Región 13-14 (Math):
  w := √w2
  Te := 2π/w
```

## 🔧 Tecnologías

- **WPF Canvas**: Layout principal
- **XAML FlowDocument**: Regiones de texto
- **AvalonEdit**: Editor de código/ecuaciones
- **System.IO.Compression**: Manejo .mcdx (ZIP)
- **System.Xml.Linq**: Parseo XML
- **MathML**: Representación ecuaciones

## 📝 Próximos Pasos

### Implementación Inmediata (Sesión Actual)
1. ✅ Crear `GridCanvas.cs` - Canvas con rejilla
2. ✅ Crear `MathcadPrimeEditorControl.xaml` - Control principal
3. ✅ Crear `MathcadRegion.cs` - Modelo de región
4. ✅ Implementar lectura básica de .mcdx
5. ✅ Mostrar regiones en canvas

### Mejoras Futuras
- Cálculo simbólico integrado
- Gráficos 2D/3D interactivos
- Exportar a PDF con formato
- Colaboración en tiempo real
- Plugin de Python/Julia

## 🎯 Criterios de Éxito

1. ✅ Abrir `Modos de vibracion.mcdx` correctamente
2. ✅ Mostrar todas las regiones (texto, math, imágenes)
3. ✅ Rejilla visual tipo MathCad original
4. ✅ Editar ecuaciones y guardar cambios
5. ✅ Exportar a .mcdx válido

---

**Nota**: Este es un editor "idealizado" de MathCad Prime, no una copia exacta.
Se enfoca en las funcionalidades más importantes para cálculos de ingeniería.
