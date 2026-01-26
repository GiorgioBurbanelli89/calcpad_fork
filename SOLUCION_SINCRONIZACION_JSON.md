# SOLUCIÓN - Sincronización de MultLangConfig.json

## Problema Actual

**Hay 20 copias diferentes de MultLangConfig.json** en el proyecto:
- Cada ejecutable (CLI, WPF, Test, etc.) tiene su propia copia
- No hay sincronización automática
- Cambios en uno no se reflejan en otros

## Diseño Original (CORRECTO)

La idea era tener UN SOLO archivo compartido:
```
C:\ProgramData\Calcpad\MultLangConfig.json  ← ÚNICO ARCHIVO
```

Todas las apps (CLI, WPF, API) deberían leer de ahí.

## ¿Por qué no funciona?

`FindConfigFile()` tiene prioridades en este orden:

1. **Junto a Calcpad.Common.dll** ← PROBLEMA: cada exe tiene su copia
2. Directorio de trabajo actual
3. CommonApplicationData (C:\ProgramData\Calcpad) ← DEBERÍA SER PRIORIDAD #1

### Resultado:
- CLI encuentra: `Calcpad.Cli\bin\Debug\net10.0\MultLangConfig.json`
- WPF encuentra: `Calcpad.Wpf\bin\Debug\net10.0-windows\MultLangConfig.json`
- **Nunca llegan a la ubicación compartida**

## Solución Propuesta

### Opción 1: Invertir Prioridades (RECOMENDADA)

Cambiar `FindConfigFile()` para buscar PRIMERO en ubicación compartida:

```csharp
private static string FindConfigFile()
{
    var possiblePaths = new List<string>();

    // PRIORITY 1: Shared location (C:\ProgramData\Calcpad)
    var commonAppData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
    var sharedPath = Path.Combine(commonAppData, "Calcpad", "MultLangConfig.json");
    possiblePaths.Add(sharedPath);

    // PRIORITY 2: Next to Calcpad.Common.dll (fallback for development)
    var assemblyDir = Path.GetDirectoryName(typeof(MultLangManager).Assembly.Location);
    if (!string.IsNullOrEmpty(assemblyDir))
    {
        possiblePaths.Add(Path.Combine(assemblyDir, "MultLangConfig.json"));
        possiblePaths.Add(Path.Combine(assemblyDir, "MultLangCode", "MultLangConfig.json"));
    }

    // PRIORITY 3: Current working directory (lowest priority)
    possiblePaths.Add(Path.Combine(Environment.CurrentDirectory, "MultLangConfig.json"));
    possiblePaths.Add(Path.Combine(Environment.CurrentDirectory, "MultLangCode", "MultLangConfig.json"));

    // Return first existing file
    foreach (var path in possiblePaths)
    {
        if (File.Exists(path))
        {
            LogDebug($"Found config at: {path}");
            return path;
        }
    }

    // If none found, CREATE in shared location
    LogDebug($"No config found. Will create at: {sharedPath}");
    EnsureDirectoryExists(sharedPath);
    return sharedPath;
}

private static void EnsureDirectoryExists(string filePath)
{
    var dir = Path.GetDirectoryName(filePath);
    if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
        Directory.CreateDirectory(dir);
}
```

### Opción 2: Variable de Entorno

Permitir que el usuario defina la ubicación:

```csharp
private static string FindConfigFile()
{
    // Check environment variable first
    var envPath = Environment.GetEnvironmentVariable("CALCPAD_MULTILANG_CONFIG");
    if (!string.IsNullOrEmpty(envPath) && File.Exists(envPath))
        return envPath;

    // Then use shared location...
    // (resto del código)
}
```

### Opción 3: Archivo de Configuración Maestro

Crear `calcpad.ini` que apunte a la ubicación del JSON:

```ini
[MultiLang]
ConfigPath=C:\ProgramData\Calcpad\MultLangConfig.json
```

## Implementación Paso a Paso

### 1. Modificar `MultLangManager.cs`

```csharp
private static string FindConfigFile()
{
    var possiblePaths = new List<string>();

    // PRIORITY 1: CommonApplicationData (SHARED)
    var commonAppData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
    var sharedConfigPath = Path.Combine(commonAppData, "Calcpad", "MultLangConfig.json");
    possiblePaths.Add(sharedConfigPath);

    // PRIORITY 2: User AppData (for per-user customization)
    var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
    possiblePaths.Add(Path.Combine(localAppData, "Calcpad", "MultLangConfig.json"));

    // PRIORITY 3: Next to assembly (development only)
    var assemblyDir = Path.GetDirectoryName(typeof(MultLangManager).Assembly.Location);
    if (!string.IsNullOrEmpty(assemblyDir))
    {
        possiblePaths.Add(Path.Combine(assemblyDir, "MultLangConfig.json"));
        possiblePaths.Add(Path.Combine(assemblyDir, "MultLangCode", "MultLangConfig.json"));
    }

    // PRIORITY 4: Current directory (lowest)
    possiblePaths.Add(Path.Combine(Environment.CurrentDirectory, "MultLangConfig.json"));

    // Find first existing file
    foreach (var path in possiblePaths)
    {
        if (File.Exists(path))
        {
            LogDebug($"Using config from: {path}");
            return path;
        }
    }

    // None found - create in shared location
    LogDebug($"Creating new config at: {sharedConfigPath}");
    var dir = Path.GetDirectoryName(sharedConfigPath);
    if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
        Directory.CreateDirectory(dir);

    return sharedConfigPath;
}

private static void LogDebug(string message)
{
    try
    {
        var logPath = Path.Combine(Path.GetTempPath(), "calcpad_multilang_debug.txt");
        File.AppendAllText(logPath, $"[{DateTime.Now:HH:mm:ss}] {message}\n");
    }
    catch { }
}
```

### 2. Crear el archivo compartido inicial

Ejecutar una sola vez:

```powershell
# Crear carpeta compartida
New-Item -ItemType Directory -Force -Path "C:\ProgramData\Calcpad"

# Copiar archivo de configuración maestro
Copy-Item "Calcpad.Common\MultLangCode\MultLangConfig.json" "C:\ProgramData\Calcpad\MultLangConfig.json"
```

### 3. Eliminar copias locales (opcional)

```powershell
# Eliminar copias en bin folders (se regenerarán si es necesario)
Get-ChildItem -Recurse -Filter "MultLangConfig.json" |
    Where-Object { $_.FullName -match "\\bin\\" } |
    Remove-Item -Verbose
```

## Ventajas de la Solución

1. ✅ **Un solo archivo** para CLI, WPF, API
2. ✅ **Cambios instantáneos** en todas las apps
3. ✅ **Fácil mantenimiento** - editar un solo archivo
4. ✅ **Soporte multi-usuario** - C:\ProgramData es accesible para todos
5. ✅ **Fallback para desarrollo** - si no existe, busca en carpeta local

## Ubicaciones Propuestas

### Producción (Compartido):
```
C:\ProgramData\Calcpad\MultLangConfig.json  ← PRIORIDAD 1
```

### Usuario (Personalización):
```
C:\Users\{user}\AppData\Local\Calcpad\MultLangConfig.json  ← PRIORIDAD 2
```

### Desarrollo (Fallback):
```
{ProjectRoot}\bin\Debug\net10.0\MultLangConfig.json  ← PRIORIDAD 3
```

## Script de Migración

```powershell
# migrate-multilang-config.ps1

$sharedPath = "C:\ProgramData\Calcpad\MultLangConfig.json"
$sourcePath = "C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Common\MultLangCode\MultLangConfig.json"

# Create directory
New-Item -ItemType Directory -Force -Path (Split-Path $sharedPath) | Out-Null

# Copy master config
if (Test-Path $sourcePath) {
    Copy-Item $sourcePath $sharedPath -Force
    Write-Host "✅ Created shared config at: $sharedPath"
} else {
    Write-Host "❌ Source file not found: $sourcePath"
}

# Verify
if (Test-Path $sharedPath) {
    $config = Get-Content $sharedPath | ConvertFrom-Json
    Write-Host "✅ Config loaded. Languages count: $($config.languages.Count)"
    Write-Host "Languages: $($config.languages.Keys -join ', ')"
} else {
    Write-Host "❌ Failed to create shared config"
}
```

## Próximos Pasos

1. ✅ Modificar `FindConfigFile()` con nuevas prioridades
2. ✅ Crear carpeta `C:\ProgramData\Calcpad`
3. ✅ Copiar archivo maestro
4. ✅ Recompilar Calcpad.Common
5. ✅ Probar CLI
6. ✅ Probar WPF
7. ✅ Verificar sincronización

¿Quieres que proceda con la implementación?
