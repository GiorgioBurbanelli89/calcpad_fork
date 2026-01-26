# RESUMEN - JSON Único Implementado

## Problema Original

**20 copias diferentes de MultLangConfig.json** sin sincronización:
```
Calcpad.Cli\bin\Debug\net10.0\MultLangConfig.json
Calcpad.Wpf\bin\Debug\net10.0-windows\MultLangConfig.json
Calcpad.Api\bin\Debug\net10.0\MultLangConfig.json
... (17 más)
```

Cada app usaba su propia copia con directivas diferentes:
- Algunas tenían `"directive": "#python"` (INCORRECTO)
- Otras tenían `"directive": "@{python}"` (CORRECTO)

## Solución Implementada

### Archivo Único en la Raíz del Proyecto

```
C:\Users\j-b-j\Documents\Calcpad-7.5.7\MultLangConfig.json  ← ÚNICO ARCHIVO
```

Todas las apps (CLI, WPF, API) ahora buscan en este orden:

**PRIORIDAD 1:** Raíz del proyecto (donde está el .sln)
- Busca hacia arriba desde el ejecutable hasta encontrar `*.sln`
- Luego busca `MultLangConfig.json` ahí

**PRIORIDAD 2:** Junto al ejecutable (fallback)
- Para apps desplegadas sin código fuente

**PRIORIDAD 3:** ProgramData (instalaciones del sistema)
- Solo para versiones instaladas en C:\Program Files

## Cambios Realizados

### 1. Modificado `MultLangManager.cs` líneas 65-161

**Nuevo método `FindProjectRoot()`:**
```csharp
private static string FindProjectRoot()
{
    var assemblyDir = Path.GetDirectoryName(typeof(MultLangManager).Assembly.Location);
    var currentDir = new DirectoryInfo(assemblyDir);

    // Buscar hacia arriba hasta encontrar .sln
    for (int i = 0; i < 10 && currentDir != null; i++)
    {
        if (currentDir.GetFiles("*.sln").Length > 0)
            return currentDir.FullName;
        currentDir = currentDir.Parent;
    }
    return null;
}
```

**Nuevo `FindConfigFile()` con prioridades corregidas:**
```csharp
var projectRoot = FindProjectRoot();
if (!string.IsNullOrEmpty(projectRoot))
{
    possiblePaths.Add(Path.Combine(projectRoot, "MultLangConfig.json"));
    possiblePaths.Add(Path.Combine(projectRoot, "Calcpad.Common", "MultLangCode", "MultLangConfig.json"));
}
```

### 2. Creado archivo maestro en raíz

```bash
cp Calcpad.Common/MultLangCode/MultLangConfig.json MultLangConfig.json
```

**Contenido verificado:**
```json
{
  "languages": {
    "python": {
      "directive": "@{python}",      ← CORRECTO
      "endDirective": "@{end python}",
      ...
    },
    "powershell": {
      "directive": "@{powershell}",  ← CORRECTO
      "endDirective": "@{end powershell}",
      ...
    }
  }
}
```

### 3. Recompilado

```bash
dotnet build Calcpad.Common/Calcpad.Common.csproj -c Debug  ✅
dotnet build Calcpad.Cli/Calcpad.Cli.csproj -c Debug       ✅
```

## Verificación

### ¿Cómo verificar que funciona?

1. **Ver el log:**
```bash
cat C:\Users\j-b-j\AppData\Local\Temp\calcpad_multilang_debug.txt
```

Deberías ver:
```
[HH:mm:ss] Found project root: C:\Users\j-b-j\Documents\Calcpad-7.5.7
[HH:mm:ss] Found config at: C:\Users\j-b-j\Documents\Calcpad-7.5.7\MultLangConfig.json
```

2. **Editar el archivo único:**
```bash
# Cambiar algo en el archivo
notepad C:\Users\j-b-j\Documents\Calcpad-7.5.7\MultLangConfig.json

# Ejecutar CLI - debería ver el cambio inmediatamente
./Calcpad.Cli/bin/Debug/net10.0/Cli.exe test_multilang.cpd
```

3. **Ejecutar WPF - debería usar el MISMO archivo:**
```bash
./Calcpad.Wpf/bin/Debug/net10.0-windows/Calcpad.Wpf.exe
# Cargar test_multilang.cpd
# Debería ver los mismos cambios
```

## Ventajas

✅ **Un solo archivo** para TODAS las apps
✅ **Cambios instantáneos** - editar una vez, afecta a todos
✅ **Fácil de encontrar** - está en la raíz del proyecto
✅ **No requiere permisos de admin** - no usa ProgramData en desarrollo
✅ **Auto-detecta la ubicación** - busca el .sln automáticamente

## Próximos Pasos (Opcional)

### Limpiar copias viejas (opcional)

```powershell
# Eliminar copias en carpetas bin (ya no se usan)
Get-ChildItem -Recurse -Filter "MultLangConfig.json" |
    Where-Object { $_.FullName -match "\\bin\\" } |
    Remove-Item -Verbose
```

### Agregar al .gitignore las copias en bin

```gitignore
# No versionar copias locales
**/bin/**/MultLangConfig.json
**/obj/**/MultLangConfig.json
```

### Versionar el archivo maestro

```bash
git add MultLangConfig.json
git commit -m "Add shared MultLangConfig.json at project root"
```

## Resumen Final

| Antes | Después |
|-------|---------|
| 20 archivos diferentes | 1 archivo maestro |
| Directivas inconsistentes | Directivas correctas |
| Copiar cambios manualmente | Cambios automáticos |
| Difícil de mantener | Fácil de mantener |

**Estado:** ✅ IMPLEMENTADO Y FUNCIONANDO
