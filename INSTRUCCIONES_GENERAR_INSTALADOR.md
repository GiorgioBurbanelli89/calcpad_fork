# INSTRUCCIONES - Generar Instalador v1.0.1

## FECHA: 2026-01-22
## VERSIÓN: Calcpad Fork 1.0.1

---

## RESUMEN

Todo está listo para generar el instalador de Calcpad Fork v1.0.1:

✅ **Código compilado** en modo Release
✅ **Instalador actualizado** a versión 1.0.1
✅ **CHANGELOG creado** con todos los cambios
✅ **Documentación incluida** en el instalador
✅ **Commits realizados** en Git

**Falta solo:** Generar el archivo setup.exe con Inno Setup

---

## OPCIÓN 1: Generar Instalador con Inno Setup (Recomendado)

### Paso 1: Verificar Inno Setup

**¿Tienes Inno Setup instalado?**

Si **NO**, descárgalo de: https://jrsoftware.org/isdl.php

Si **SÍ**, verifica la ubicación:
```
C:\Program Files (x86)\Inno Setup 6\iscc.exe
```

### Paso 2: Compilar el Script

**Opción A - Usando la interfaz gráfica:**

1. Abre **Inno Setup Compiler**
2. Ve a **File → Open**
3. Selecciona:
   ```
   C:\Users\j-b-j\Documents\Calcpad-7.5.7\CalcpadWpfInstaller.iss
   ```
4. Presiona **F9** o **Build → Compile**

**Opción B - Usando línea de comandos:**

```bash
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" CalcpadWpfInstaller.iss
```

### Paso 3: Ubicación del Instalador

El instalador se generará en:
```
C:\Users\j-b-j\Documents\Calcpad-7.5.7\Installer\CalcpadFork-Setup-1.0.1.exe
```

**Tamaño aproximado:** ~15-20 MB

---

## OPCIÓN 2: Generar Instalador con PowerShell

Si tienes Inno Setup instalado, puedes usar este script:

```powershell
# Buscar iscc.exe en ubicaciones comunes
$isccPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\iscc.exe",
    "C:\Program Files\Inno Setup 6\iscc.exe",
    "C:\Program Files (x86)\Inno Setup 5\iscc.exe",
    "C:\Program Files\Inno Setup 5\iscc.exe"
)

$iscc = $null
foreach ($path in $isccPaths) {
    if (Test-Path $path) {
        $iscc = $path
        break
    }
}

if ($iscc) {
    Write-Host "Encontrado Inno Setup en: $iscc"
    & $iscc "CalcpadWpfInstaller.iss"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Instalador generado correctamente!"
        Write-Host "Ubicación: .\Installer\CalcpadFork-Setup-1.0.1.exe"
    } else {
        Write-Host "❌ Error al generar instalador"
    }
} else {
    Write-Host "❌ No se encontró Inno Setup"
    Write-Host "Descarga desde: https://jrsoftware.org/isdl.php"
}
```

Guarda esto como `generar_instalador.ps1` y ejecuta:
```powershell
.\generar_instalador.ps1
```

---

## OPCIÓN 3: Distribución sin Instalador

Si no quieres usar un instalador, puedes distribuir los archivos directamente:

### Paso 1: Crear carpeta de distribución

```bash
mkdir Calcpad-Fork-1.0.1-Portable
```

### Paso 2: Copiar archivos necesarios

```bash
# Copiar binarios
cp -r Calcpad.Wpf/bin/Release/net10.0-windows/* Calcpad-Fork-1.0.1-Portable/

# Copiar documentación
cp README.md Calcpad-Fork-1.0.1-Portable/
cp CHANGELOG.md Calcpad-Fork-1.0.1-Portable/
cp LICENSE Calcpad-Fork-1.0.1-Portable/

# Copiar ejemplos (opcional)
cp -r Examples Calcpad-Fork-1.0.1-Portable/Examples

# Copiar documentación de fixes
mkdir Calcpad-Fork-1.0.1-Portable/Docs
cp AUDITORIA_COMPLETA_MATHEDITOR.md Calcpad-Fork-1.0.1-Portable/Docs/
cp FIXES_CRITICOS_MEMORY_LEAKS_APLICADOS.md Calcpad-Fork-1.0.1-Portable/Docs/
cp RESUMEN_FINAL_TODOS_LOS_FIXES.md Calcpad-Fork-1.0.1-Portable/Docs/
cp TODOS_LOS_FIXES_APLICADOS.md Calcpad-Fork-1.0.1-Portable/Docs/
```

### Paso 3: Comprimir

```bash
# Crear ZIP
tar -czf Calcpad-Fork-1.0.1-Portable.zip Calcpad-Fork-1.0.1-Portable/

# O usar 7-Zip
7z a -tzip Calcpad-Fork-1.0.1-Portable.zip Calcpad-Fork-1.0.1-Portable/
```

**Requisitos para el usuario:**
- .NET 10 Desktop Runtime instalado
- Windows 10/11

---

## VERIFICACIÓN POST-INSTALACIÓN

Después de generar el instalador, verifica:

### 1. Prueba de Instalación
- Ejecuta el setup.exe
- Verifica que se instale en `C:\Program Files\CalcpadFork`
- Verifica que se cree el acceso directo en el escritorio
- Verifica asociación de archivos .cpd

### 2. Prueba de Ejecución
- Abre Calcpad Fork desde el acceso directo
- Carga un archivo .cpd de prueba
- Verifica modo MathEditor (Visual)
- Prueba el preview editor:
  - Click en bloque de código externo
  - Click en preview bar
  - Editor debe abrir con cursor visible
  - Escribir y presionar Enter
  - Verificar que se puede reabrir

### 3. Prueba de Documentación
- Verifica que CHANGELOG.md esté en la carpeta de instalación
- Verifica que los archivos de Docs estén presentes
- Verifica que los ejemplos funcionen

---

## CONTENIDO DEL INSTALADOR v1.0.1

### Archivos principales:
- `Calcpad.exe` - Ejecutable principal
- `Calcpad.dll` - Librería principal WPF
- `Calcpad.Core.dll` - Motor de cálculos
- `Calcpad.Common.dll` - Utilidades comunes
- `Calcpad.OpenXml.dll` - Exportación a DOCX/PDF
- Todas las dependencias (AvalonEdit, WebView2, etc.)

### Documentación incluida:
- `README.md` - Readme general
- `CHANGELOG.md` - **NUEVO** - Historial de cambios
- `LICENSE.txt` - Licencia MIT
- `Docs/AUDITORIA_COMPLETA_MATHEDITOR.md` - **NUEVO**
- `Docs/FIXES_CRITICOS_MEMORY_LEAKS_APLICADOS.md` - **NUEVO**
- `Docs/RESUMEN_FINAL_TODOS_LOS_FIXES.md` - **NUEVO**
- `Docs/TODOS_LOS_FIXES_APLICADOS.md` - **NUEVO**
- Toda la documentación de HTML/CSS/TypeScript existente

### Ejemplos incluidos:
- Todos los archivos .cpd de la carpeta Examples

---

## NOVEDADES EN v1.0.1

### Bugs Corregidos:
1. ✅ Pipe duplicado en preview editor
2. ✅ Cursor no aparece al abrir editor
3. ✅ Editor no se puede volver a abrir
4. ✅ Editor se bloquea inmediatamente
5. ✅ Parameter count mismatch error

### Fixes Críticos:
6. ✅ Memory leak: cursor timer
7. ✅ Memory leak: preview editor timer
8. ✅ Validación Application.Current.MainWindow (4 ocurrencias)
9. ✅ Validación de índices en loops

**Total:** 9 mejoras sobre v1.0.0

---

## COMANDOS RÁPIDOS

### Compilar Release:
```bash
dotnet build Calcpad.Wpf/Calcpad.Wpf.csproj -c Release
```

### Generar Instalador (si tienes Inno Setup):
```bash
"C:\Program Files (x86)\Inno Setup 6\iscc.exe" CalcpadWpfInstaller.iss
```

### Ver estado Git:
```bash
git status
git log --oneline -5
```

---

## TROUBLESHOOTING

### Error: "No se encontró .NET 10"
El instalador verifica automáticamente .NET 10 y ofrece descargar.
URL: https://dotnet.microsoft.com/download/dotnet/10.0

### Error: "No se puede copiar archivo (en uso)"
Cierra todas las instancias de Calcpad antes de compilar Release.

### Instalador muy grande
El instalador incluye todas las dependencias (.NET 10 embebido opcional).
Sin embeber .NET: ~15-20 MB
Con .NET embebido: ~200+ MB

---

## ESTADO ACTUAL

✅ **Código:** Compilado en Release (0 errores)
✅ **Git:** 2 commits realizados
  - `26eee19` - fix: Apply critical fixes to MathEditor
  - `d6c8014` - build: Update installer to v1.0.1
✅ **Instalador:** Script actualizado a v1.0.1
✅ **Documentación:** CHANGELOG.md creado
⏳ **Pendiente:** Generar setup.exe con Inno Setup

---

## PRÓXIMOS PASOS

1. **Instalar Inno Setup** (si no lo tienes)
2. **Generar instalador** usando una de las 3 opciones
3. **Probar instalador** en una máquina limpia
4. **Publicar release** en GitHub (opcional)
5. **Distribuir** a usuarios

---

## CONTACTO

**Repositorio:** https://github.com/GiorgioBurbanelli89/calcpad_fork
**Licencia:** MIT
**Versión:** 1.0.1
**Fecha:** 2026-01-22
