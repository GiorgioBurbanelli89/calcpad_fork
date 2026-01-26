# Integración de Maxima con Calcpad

## ¿Qué es Maxima?

**Maxima** es un sistema de álgebra computacional (CAS) de código abierto basado en Macsyma (MIT, 1960s). Es completamente gratuito y muy potente para:

- Resolver ecuaciones diferenciales ordinarias (ODEs) y parciales (PDEs)
- Álgebra simbólica avanzada
- Cálculo integral y diferencial
- Transformadas de Laplace y Fourier
- Series de Taylor
- Manipulación de matrices simbólicas

## Ventajas de Maxima

✅ **Opensource y gratuito**
✅ **Más potente que AngouriMath** para ODEs
✅ **Soporta ODEs no lineales, sistemas de ODEs, PDEs**
✅ **Transformadas de Laplace, Fourier, etc.**
✅ **Documentación extensa** (40+ años de desarrollo)

## Comparación: AngouriMath vs Maxima

| Característica | AngouriMath | Maxima |
|---------------|-------------|---------|
| Estado | Deprecado (2026) | Activo |
| ODEs lineales constantes | ✅ (manual) | ✅ (nativo) |
| ODEs no lineales | ❌ | ✅ |
| Sistemas de ODEs | ❌ | ✅ |
| PDEs | ❌ | ✅ |
| Transformadas Laplace | ❌ | ✅ |
| Series de Taylor | ⚠️ | ✅ |
| Manipulación simbólica | ✅ | ✅ |
| Integración .NET | Directa | Proceso externo |

## Instalación de Maxima

### Windows
```bash
# Descargar de: https://maxima.sourceforge.io/
# O con Chocolatey:
choco install maxima
```

### Linux
```bash
sudo apt-get install maxima
# O
sudo yum install maxima
```

### Verificar instalación
```bash
maxima --version
```

## Integrar Maxima en Calcpad

Hay 3 formas de integrar Maxima:

### Opción 1: Ejecutar Maxima como proceso externo (CLI)

```csharp
// Calcpad.Common/ExpressionParsers/MaximaParser.cs
using System.Diagnostics;

public class MaximaParser : BaseExpressionParser
{
    public override string Name => "Maxima CAS Parser";
    public override string Directive => "@{maxima}";
    public override string EndDirective => "@{end maxima}";

    public override string Translate(string expression)
    {
        // Ejecutar Maxima en batch mode
        var startInfo = new ProcessStartInfo
        {
            FileName = "maxima",
            Arguments = "--very-quiet --batch-string=\"" + expression + "\"",
            RedirectStandardOutput = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        using var process = Process.Start(startInfo);
        string output = process.StandardOutput.ReadToEnd();
        process.WaitForExit();

        return output.Trim();
    }
}
```

**Ejemplo de uso:**
```calcpad
@{maxima}
' Resolver ODE no lineal
sol = ode2('diff(y,x) = y^2, y, x);
' Resultado: y = -1/(x+C)
@{end maxima}
```

### Opción 2: Usar biblioteca MaximaSharp (si existe)

Buscar en NuGet paquetes que integren Maxima con .NET.

### Opción 3: Usar sockets o pipes para comunicación bidireccional

```csharp
// Mantener proceso Maxima corriendo y comunicarse vía pipes
var process = new Process
{
    StartInfo = new ProcessStartInfo
    {
        FileName = "maxima",
        Arguments = "--very-quiet",
        RedirectStandardInput = true,
        RedirectStandardOutput = true,
        UseShellExecute = false,
        CreateNoWindow = true
    }
};
process.Start();

// Enviar comandos
process.StandardInput.WriteLine("solve([x^2+y^2=25, x-y=5], [x,y]);");
process.StandardInput.Flush();

// Leer respuesta
string output = process.StandardOutput.ReadLine();
```

## Sintaxis de Maxima para ODEs

### ODEs de primer orden
```maxima
/* ODE separable */
ode2('diff(y,x) = 2*x, y, x);
/* Resultado: y = x^2 + C */

/* ODE lineal */
ode2('diff(y,x) + 2*y = exp(x), y, x);
```

### ODEs de segundo orden
```maxima
/* Homogénea */
ode2('diff(y,x,2) - 3*'diff(y,x) + 2*y = 0, y, x);
/* Resultado: y = C1*exp(2*x) + C2*exp(x) */

/* No homogénea */
ode2('diff(y,x,2) + 4*y = sin(x), y, x);
```

### Condiciones iniciales
```maxima
/* Resolver con condiciones */
sol: ode2('diff(y,x,2) + 4*y = 0, y, x);
ic2(sol, x=0, y=1, 'diff(y,x)=0);
/* Resultado: y = cos(2*x) */
```

### Sistemas de ODEs
```maxima
/* Sistema acoplado */
atvalue('diff(x,t), t=0, 1);
atvalue('diff(y,t), t=0, 0);
desolve(['diff(x,t,2) + 3*x + 4*y = 0,
         'diff(y,t,2) + 2*x + 3*y = 0], [x,y]);
```

### Transformadas de Laplace
```maxima
/* Resolver ODE con Laplace */
eq: 'diff(y,t,2) + 5*'diff(y,t) + 6*y = exp(-t);
laplace(eq, t, s);
solve(%, laplace(y,t,s));
```

## Implementación Completa Recomendada

```csharp
// Calcpad.Common/ExpressionParsers/MaximaParser.cs
using System;
using System.Diagnostics;
using System.Text.RegularExpressions;

namespace Calcpad.Common.ExpressionParsers
{
    public class MaximaParser : BaseExpressionParser
    {
        public override string Name => "Maxima CAS Parser";
        public override string Directive => "@{maxima}";
        public override string EndDirective => "@{end maxima}";
        public override ParserMode Mode => ParserMode.Execute;

        private readonly bool _isMaximaAvailable;

        public MaximaParser()
        {
            _isMaximaAvailable = CheckMaximaInstalled();
        }

        private bool CheckMaximaInstalled()
        {
            try
            {
                var startInfo = new ProcessStartInfo
                {
                    FileName = "maxima",
                    Arguments = "--version",
                    RedirectStandardOutput = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };

                using var process = Process.Start(startInfo);
                process.WaitForExit(3000);
                return process.ExitCode == 0;
            }
            catch
            {
                return false;
            }
        }

        public override string Translate(string expression)
        {
            if (!_isMaximaAvailable)
                return "' Error: Maxima not installed. Download from https://maxima.sourceforge.io/";

            var lines = expression.Split(new[] { '\n', '\r' },
                StringSplitOptions.RemoveEmptyEntries);
            var results = new List<string>();

            foreach (var line in lines)
            {
                var trimmed = line.Trim();
                if (string.IsNullOrWhiteSpace(trimmed) || trimmed.StartsWith("'"))
                {
                    results.Add(line);
                    continue;
                }

                // Procesar con Maxima
                try
                {
                    var result = ExecuteMaxima(trimmed);
                    results.Add($"' {trimmed}");
                    results.Add($"' {result}");
                }
                catch (Exception ex)
                {
                    results.Add($"' {trimmed}");
                    results.Add($"' Error: {ex.Message}");
                }
            }

            return string.Join("\n", results);
        }

        private string ExecuteMaxima(string command)
        {
            // Asegurarse de que el comando termina con ;
            if (!command.TrimEnd().EndsWith(";"))
                command += ";";

            var startInfo = new ProcessStartInfo
            {
                FileName = "maxima",
                Arguments = $"--very-quiet --batch-string=\"{command}\"",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using var process = Process.Start(startInfo);
            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();
            process.WaitForExit(10000);

            if (!string.IsNullOrEmpty(error))
                throw new Exception(error);

            // Limpiar output de Maxima (remover prompts y espacios)
            output = Regex.Replace(output, @"^\(%i\d+\)", "",
                RegexOptions.Multiline);
            output = Regex.Replace(output, @"^\(%o\d+\)", "",
                RegexOptions.Multiline);
            output = output.Trim();

            return output;
        }

        public override object Evaluate(string expression,
            IDictionary<string, double> variables)
        {
            return ExecuteMaxima(expression);
        }

        public override bool Validate(string expression, out string error)
        {
            error = null;
            if (!_isMaximaAvailable)
            {
                error = "Maxima not installed";
                return false;
            }
            return true;
        }
    }
}
```

## Ejemplo de uso en Calcpad

```calcpad
"Ecuaciones Diferenciales con Maxima"

@{maxima}
' ODE no lineal
ode2('diff(y,x) = y^2 + x, y, x);

' ODE de segundo orden no homogénea
ode2('diff(y,x,2) + 4*y = sin(x), y, x);

' Sistema de ODEs
desolve(['diff(x,t) = -2*x + y,
         'diff(y,t) = x - 2*y], [x,y]);

' Transformada de Laplace
laplace(t^2*exp(-3*t), t, s);

' Serie de Taylor
taylor(sin(x), x, 0, 5);
@{end maxima}
```

## Próximos Pasos

1. **Implementar MaximaParser.cs** siguiendo el código anterior
2. **Registrar en MultLangConfig.json**:
```json
"maxima": {
    "directive": "@{maxima}",
    "endDirective": "@{end maxima}",
    "description": "Maxima CAS - ODEs, PDEs, Laplace, etc."
}
```
3. **Agregar a MultLangProcessor.ExpressionParsers.cs**
4. **Crear ejemplos en Examples/Test-Maxima-ODEs.cpd**
5. **Actualizar documentación**

## Recursos

- **Sitio oficial**: https://maxima.sourceforge.io/
- **Documentación**: https://maxima.sourceforge.io/docs/manual/maxima.html
- **Tutorial ODEs**: https://maxima.sourceforge.io/docs/tutorial/en/minimal-maxima.pdf
- **Referencia rápida**: http://maxima.sourceforge.net/docs/intromax/intromax.html

## Conclusión

**AngouriMath** es suficiente para ODEs lineales básicas con coeficientes constantes (implementado ✅).

**Maxima** es recomendado para:
- ODEs no lineales
- Sistemas de ODEs
- PDEs (ecuaciones en derivadas parciales)
- Transformadas de Laplace/Fourier
- Manipulación simbólica avanzada

La integración de Maxima es relativamente simple usando `Process.Start()` en modo batch.
