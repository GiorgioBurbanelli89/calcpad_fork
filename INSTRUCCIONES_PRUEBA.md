# 🎉 Instrucciones de Prueba - GlobalParser y AutoCompletado

## ✅ Implementación Completada

Se ha implementado exitosamente:

1. **GlobalParser** - Arquitectura que separa código externo de Calcpad
2. **Nueva sintaxis** - `@{language}` para código externo
3. **AutoCompletado** - Sugerencias inteligentes al escribir `@`

---

## 🧪 Cómo Probar

### 1. Probar AutoCompletado de Lenguajes

1. **Abrir Calcpad.exe** (ya está ejecutándose)
2. **Crear nuevo archivo**
3. **Escribir `@`** - Debe aparecer una lista con todos los lenguajes disponibles:
   - `@{avalonia}`
   - `@{bash}`
   - `@{c}`
   - `@{cmd}`
   - `@{cpp}`
   - `@{csharp}`
   - `@{fortran}`
   - `@{gtk}`
   - `@{html}`
   - `@{julia}`
   - `@{markdown}`
   - `@{octave}`
   - `@{powershell}`
   - `@{python}`
   - `@{qt}`
   - `@{r}`
   - `@{wpf}`
   - `@{xaml}`

4. **Seleccionar un lenguaje** con las flechas y presionar **Tab** o **Enter**
5. El autocompletado también funciona al escribir:
   - `@{py` → Filtra y muestra `@{python}`
   - `@{c` → Muestra `@{c}`, `@{cmd}`, `@{cpp}`, `@{csharp}`
   - `@{end ` → Muestra todos los `@{end language}`

### 2. Probar Código Python

1. **Abrir archivo**: `test_python_new_syntax.cpd`
2. **Presionar F5** o click en **Calculate**
3. **Resultado esperado**:
   - Ejecuta el código Python sin errores
   - Muestra la salida en la ventana Output
   - NO aparecen errores de ExpressionParser
   - La sintaxis `@{python}` es reconocida

### 3. Probar Código Avalonia/C#

1. **Abrir archivo**: `test_avalonia_new_syntax.cpd`
2. **Presionar F5** o click en **Calculate**
3. **Resultado esperado**:
   - Ejecuta el código C# sin errores
   - Muestra "¡Hola desde Avalonia!" y cálculos
   - ExpressionParser NO intenta parsear el código C#

### 4. Probar Código Calcpad Normal

1. **Abrir archivo**: `test_pure_calcpad.cpd`
2. **Presionar F5** o click en **Calculate**
3. **Resultado esperado**:
   - Calcpad matemático funciona normalmente
   - Variables, funciones trigonométricas calculadas
   - GlobalParser detecta que NO hay código externo
   - ExpressionParser procesa el código correctamente

### 5. Probar Mezcla (Código Externo + Calcpad)

Crear un archivo nuevo con:

```calcpad
"Primero código Python

@{python}
resultado = 3.14159 * 2
print(f"Resultado Python: {resultado}")
print(f"CALCPAD:pi_doble={resultado}")
@{end python}

"Ahora código Calcpad usa la variable exportada
'Variable importada desde Python:
pi_doble = ?

'Cálculos Calcpad:
radio = 5
area = π·radio^2
area = ?
```

**Resultado esperado**:
- Python ejecuta primero
- Variable `pi_doble` exportada a Calcpad
- Calcpad usa la variable en cálculos posteriores

---

## 🎯 Características Clave Implementadas

### GlobalParser.cs
- **Ubicación**: `Calcpad.Common\GlobalParser.cs`
- **Función**: Decide ANTES de procesar si usar MultLang O Calcpad
- **Lógica**:
  ```
  ¿Contiene @{language}?
    → SÍ: MultLangProcessor (ExpressionParser SALTADO)
    → NO: ExpressionParser (MultLangProcessor SALTADO)
  ```

### CalcpadProcessor.cs
- Integra GlobalParser
- Usa flag `MultilangProcessed` para indicar qué ruta se usó
- Macros se saltan cuando hay código externo

### MainWindow.xaml.cs (líneas 1350-1403)
- Verifica `processingResult.MultilangProcessed`
- Si es `true` → **NO** llama a `_parser.Parse()`
- Si es `false` → Procesa normalmente con ExpressionParser

### AutoCompleteManager.cs
- Trigger `@` agregado (línea 839)
- Trigger `{` cuando ya está visible (línea 841)
- Lenguajes cargados dinámicamente desde MultLangConfig.json (líneas 41-70)
- Color verde para directivas de código externo
- Tooltips con información del lenguaje

### MultLangConfig.json y MultLangManager.cs
- 18 lenguajes configurados con sintaxis `@{language}`
- Configuración compartida entre CLI y WPF

---

## 🔍 Verificación de Arquitectura

### Antes (PROBLEMA):
```
Código → MultLangProcessor → HTML → MacroParser → ExpressionParser
                                                          ↑
                                                    PARSEA HTML Y GENERA ERRORES
```

### Ahora (SOLUCIÓN):
```
Código → GlobalParser (DECISIÓN)
         ↓
         ¿Tiene @{language}?
         ↓
    SÍ → MultLangProcessor → HTML → FIN
         ↓
    NO → MacroParser → ExpressionParser → HTML → FIN
```

---

## 📊 Resumen de Archivos Modificados

1. **MultLangConfig.json** - Sintaxis actualizada a `@{language}`
2. **MultLangManager.cs** - Directivas en CreateDefaultConfig()
3. **GlobalParser.cs** (NUEVO) - Parser de decisión
4. **CalcpadProcessor.cs** - Integra GlobalParser
5. **MainWindow.xaml.cs** - Respeta flag MultilangProcessed
6. **AutoCompleteManager.cs** - Soporte para `@` y lenguajes externos

---

## 🚀 Próximos Pasos (Opcionales)

1. **Syntax Highlighting**: Actualizar resaltador para `@{language}`
2. **Snippets**: Agregar plantillas completas (ej: `@{python}` inserta bloque completo)
3. **Validación**: Verificar que lenguaje existe antes de ejecutar
4. **Documentación**: Actualizar manual de usuario
5. **Más Parsers**: Agregar otros parsers personalizados usando GlobalParser como base

---

## 💡 Ventajas de la Nueva Arquitectura

1. **Modular**: Fácil agregar nuevos parsers
2. **Limpio**: Separación clara entre código externo y Calcpad
3. **Eficiente**: NO procesa innecesariamente
4. **Extensible**: GlobalParser puede expandirse para otros tipos
5. **Sin conflictos**: `@{` no se usa en Calcpad ni en lenguajes externos

---

## ❓ Solución de Problemas

### El autocompletado no muestra lenguajes
- Verificar que MultLangConfig.json existe en la carpeta de Calcpad.exe
- El archivo debe tener la nueva sintaxis `@{language}`

### Código externo no ejecuta
- Verificar que el lenguaje está instalado (`python --version`, `dotnet --version`, etc.)
- Ver archivo de debug: `%TEMP%\calcpad-debug.txt`
- Ver archivo de log: `%TEMP%\calcpad_multilang_debug.txt`

### ExpressionParser aún parsea código externo
- Verificar que se usa la sintaxis `@{language}` (NO `#language`)
- Verificar que el archivo fue guardado y recargado
- Revisar `calcpad-debug.txt` - debe decir "HasExternalCode=true"

---

¡Disfruta usando Calcpad con código externo! 🎉
