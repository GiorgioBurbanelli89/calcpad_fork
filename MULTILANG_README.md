# MultLangCode - Sistema de Múltiples Lenguajes para Calcpad

## Descripción

MultLangCode es una extensión de Calcpad que permite ejecutar código en múltiples lenguajes de programación (Python, C++, Octave, Julia, R, PowerShell, Bash, CMD) directamente desde archivos `.cpd`. Los resultados se integran en el documento de Calcpad y las variables pueden compartirse entre Calcpad y los lenguajes externos.

**Nota:** Esta funcionalidad es exclusiva de esta versión fork y no está disponible en el repositorio original [Proektsoftbg/Calcpad](https://github.com/Proektsoftbg/Calcpad).

---

## Lenguajes Soportados

| Lenguaje    | Directiva         | Fin Directiva       | Comando      | Tipo        |
|-------------|-------------------|---------------------|--------------|-------------|
| Python      | `@{python}`         | `@{end python}`       | python       | Interpretado|
| C++         | `@{cpp}`            | `@{end cpp}`          | g++          | Compilado   |
| GNU Octave  | `@{octave}`         | `@{end octave}`       | octave-cli   | Interpretado|
| Julia       | `@{julia}`          | `@{end julia}`        | julia        | Interpretado|
| R           | `@{r}`              | `@{end r}`            | Rscript      | Interpretado|
| PowerShell  | `@{powershell}`     | `@{end powershell}`   | pwsh         | Interpretado|
| Bash        | `@{bash}`           | `@{end bash}`         | bash         | Interpretado|
| CMD         | `@{cmd}`            | `@{end cmd}`          | cmd          | Interpretado|

**Requisito:** Todos los lenguajes deben estar instalados y disponibles en el PATH del sistema.

---

## Sintaxis Básica

### Bloque de código externo

```
@{lenguaje}
... código del lenguaje ...
@{end lenguaje}
```

### Ejemplo con Python

```
"Cálculo con Python
radio = 5

@{python}
import math
area = math.pi * 5**2
print(f"Área del círculo: {area:.4f}")
@{end python}

'Continuando en Calcpad:
perimetro = 2*pi*radio
```

### Ejemplo con C++

```
"Cálculo con C++

@{cpp}
#include <iostream>
#include <cmath>
using namespace std;

int main() {
    double radio = 5.0;
    double area = M_PI * radio * radio;
    cout << "Área: " << area << endl;
    return 0;
}
@{end cpp}
```

### Ejemplo con GNU Octave

```
"Cálculo con Octave

@{octave}
x = linspace(0, 2*pi, 100);
y = sin(x);
disp(["Máximo de sin(x): ", num2str(max(y))]);
@{end octave}
```

---

## Intercambio de Variables

### Exportar variables desde lenguaje externo a Calcpad

Para exportar una variable desde cualquier lenguaje externo a Calcpad, imprima una línea con el formato:

```
CALCPAD:nombre_variable=valor
```

La variable estará disponible para cálculos posteriores en Calcpad.

#### Python
```python
resultado = 3.14159
print(f"CALCPAD:mi_variable={resultado}")
```

#### C++
```cpp
double resultado = 3.14159;
cout << "CALCPAD:mi_variable=" << resultado << endl;
```

#### Octave
```octave
resultado = 3.14159;
printf("CALCPAD:mi_variable=%.6f\n", resultado);
```

#### Julia
```julia
resultado = 3.14159
println("CALCPAD:mi_variable=$resultado")
```

#### R
```r
resultado <- 3.14159
cat(paste0("CALCPAD:mi_variable=", resultado, "\n"))
```

#### PowerShell
```powershell
$resultado = 3.14159
Write-Host "CALCPAD:mi_variable=$resultado"
```

### Ejemplo completo de intercambio

```
"Intercambio de variables
'=========================
radio = 5
altura = 10

@{python}
import math
r = 5
h = 10
volumen = math.pi * r**2 * h
print(f"Volumen calculado en Python: {volumen:.4f}")
print(f"CALCPAD:vol_python={volumen:.6f}")
@{end python}

'Verificación en Calcpad:
'El volumen desde Python es:
resultado = vol_python

'Comparación con cálculo de Calcpad:
vol_calcpad = pi*radio^2*altura
diferencia = vol_calcpad - vol_python
```

---

## Configuración

El sistema se configura mediante el archivo `MultLangConfig.json` ubicado en:
- `Calcpad.Common/MultLangCode/MultLangConfig.json`

### Estructura del archivo de configuración

```json
{
  "languages": {
    "python": {
      "command": "python",
      "extension": ".py",
      "directive": "@{python}",
      "endDirective": "@{end python}",
      "commentPrefix": "#",
      "keywords": ["def", "class", "import", ...],
      "builtins": ["print", "len", "range", ...],
      "requiresCompilation": false,
      "compileArgs": "",
      "runArgs": "\"{file}\""
    },
    "cpp": {
      "command": "g++",
      "extension": ".cpp",
      "directive": "@{cpp}",
      "endDirective": "@{end cpp}",
      "commentPrefix": "//",
      "keywords": ["int", "double", "class", ...],
      "builtins": ["cout", "cin", "endl", ...],
      "requiresCompilation": true,
      "compileArgs": "{input} -o {output}",
      "runArgs": ""
    }
    // ... otros lenguajes
  },
  "settings": {
    "timeout": 30000,
    "maxOutputLines": 1000,
    "tempDirectory": "temp_multilang",
    "shareVariables": true
  }
}
```

### Opciones de configuración

| Opción            | Descripción                                           |
|-------------------|-------------------------------------------------------|
| `timeout`         | Tiempo máximo de ejecución en milisegundos (default: 30000) |
| `maxOutputLines`  | Número máximo de líneas de salida (default: 1000)     |
| `tempDirectory`   | Directorio para archivos temporales                   |
| `shareVariables`  | Habilitar intercambio de variables (default: true)    |

### Agregar un nuevo lenguaje

Para agregar un nuevo lenguaje, edite `MultLangConfig.json`:

```json
"mi_lenguaje": {
  "command": "mi_interprete",
  "extension": ".ext",
  "directive": "@{mi_lenguaje}",
  "endDirective": "@{end mi_lenguaje}",
  "commentPrefix": "#",
  "keywords": [],
  "builtins": [],
  "requiresCompilation": false,
  "compileArgs": "",
  "runArgs": "\"{file}\""
}
```

---

## Uso desde CLI

```bash
# Ejecutar archivo con bloques de múltiples lenguajes
cli input.cpd output.html

# Modo silencioso
cli input.cpd output.html -s
```

---

## Estructura de Archivos

```
Calcpad.Common/MultLangCode/
├── MultLangConfig.json         # Configuración de lenguajes
├── MultLangManager.cs          # Gestión de configuración
├── MultLangProcessor.cs        # Procesador principal
├── LanguageExecutor.cs         # Ejecutor de código
├── LanguageDefinition.cs       # Modelo de definición
├── LanguageHtmlGenerator.cs    # Generador de salida
├── Highlighting/               # Resaltado de sintaxis
│   ├── PythonHighlighter.cs
│   ├── CppHighlighter.cs
│   ├── OctaveHighlighter.cs
│   └── ...
├── AutoComplete/               # Autocompletado
│   ├── PythonAutoComplete.cs
│   └── ...
└── Templates/                  # Templates HTML
    ├── python.html
    ├── cpp.html
    └── ...
```

---

## Notas Importantes

1. **Orden de procesamiento:** Los bloques de código externo se procesan ANTES que el MacroParser de Calcpad.

2. **Variables exportadas:** Las líneas `CALCPAD:var=valor` no aparecen en la salida visible.

3. **Lenguajes compilados:** C++ se compila automáticamente con g++ antes de ejecutarse.

4. **Errores:** Si un lenguaje no está instalado, se muestra un mensaje de error en lugar del resultado.

5. **Timeout:** Si la ejecución excede el timeout configurado, el proceso se termina automáticamente.

---

## Ejemplos

### Ejemplo 1: Cálculo científico con Python

```
"Análisis estadístico con Python

@{python}
import statistics
datos = [23, 45, 67, 89, 12, 34, 56, 78, 90, 11]
media = statistics.mean(datos)
desv = statistics.stdev(datos)
print(f"Media: {media:.2f}")
print(f"Desviación estándar: {desv:.2f}")
print(f"CALCPAD:media_py={media}")
print(f"CALCPAD:desv_py={desv}")
@{end python}

'Resultados en Calcpad:
promedio = media_py
variacion = desv_py/media_py*100
```

### Ejemplo 2: Cálculo numérico con Octave

```
"Solución de sistema lineal con Octave

@{octave}
A = [3 2 -1; 2 -2 4; -1 0.5 -1];
b = [1; -2; 0];
x = A \ b;
printf("Solución:\n");
printf("x1 = %.4f\n", x(1));
printf("x2 = %.4f\n", x(2));
printf("x3 = %.4f\n", x(3));
printf("CALCPAD:x1=%.6f\n", x(1));
printf("CALCPAD:x2=%.6f\n", x(2));
printf("CALCPAD:x3=%.6f\n", x(3));
@{end octave}

'Verificación en Calcpad:
'Las soluciones del sistema son:
sol_1 = x1
sol_2 = x2
sol_3 = x3
```

### Ejemplo 3: Procesamiento con C++

```
"Cálculo de factorial con C++

@{cpp}
#include <iostream>
using namespace std;

long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    int n = 10;
    long long result = factorial(n);
    cout << n << "! = " << result << endl;
    cout << "CALCPAD:fact_10=" << result << endl;
    return 0;
}
@{end cpp}

'El factorial de 10 es:
resultado = fact_10
```

---

## Solución de Problemas

### El lenguaje no se detecta

Verifique que el ejecutable esté en el PATH:
```bash
# Windows
where python
where g++

# Linux/Mac
which python
which g++
```

### Error de compilación en C++

Asegúrese de que el código C++ sea válido y tenga una función `main()`.

### Timeout excedido

Aumente el valor de `timeout` en `MultLangConfig.json` o optimice su código.

### Variables no se exportan

Verifique el formato exacto: `CALCPAD:nombre=valor` (sin espacios alrededor del `=`).

---

## Licencia

Este sistema es parte del proyecto Calcpad y está sujeto a la misma licencia.

---

**Versión:** 7.5.8
**Autor:** Fork de Calcpad con extensiones MultLangCode
