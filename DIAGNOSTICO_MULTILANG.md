# DIAGNÓSTICO - Bloques MultLang no se ejecutan en CLI

## Problema Identificado

Los bloques `@{python}...@{end python}` NO se detectan como código externo en GlobalParser, pero SÍ se ejecutan correctamente por MultLangProcessor.

## Flujo de Ejecución

### 1. Program.cs línea 349
```csharp
var code = CalcpadReader.Read(fileName);
```
- Lee el archivo .cpd
- **CalcpadReader.cs líneas 57-70**: Detecta bloques que empiezan con `#` (para compatibilidad)
- **PROBLEMA**: Los archivos usan `@{python}` pero CalcpadReader busca líneas con `#python`

### 2. Program.cs línea 353
```csharp
var result = processor.ProcessCode(code, addLineNumbers: true);
```
- CalcpadProcessor.ProcessCode() → GlobalParser.Process()

### 3. GlobalParser.cs línea 36
```csharp
hasExternalCode = MultLangManager.HasLanguageCode(code);
```
- **AQUÍ ESTÁ EL BUG #1**: Busca directivas en el código
- MultLangConfig.json tenía `"directive": "#python"` (INCORRECTO)
- Debería ser `"directive": "@{python}"`
- **YA CORREGIDO**: Copiamos el archivo correcto

### 4. GlobalParser.cs líneas 41-56
```csharp
bool hasMixedCode = HasCalcpadCode(code);
if (hasMixedCode)
{
    hasExternalCode = false; // Signal to use ExpressionParser
    // Reemplaza bloques externos con HTML comments
}
```
- **PROBLEMA #2**: Como hay código Calcpad MEZCLADO con código externo:
  - DetectahasCalcpadCode=True
  - Setea `hasExternalCode=false`
  - Los bloques externos se procesan por MultLangProcessor
  - Pero se reemplazan con resultados
  - ExpressionParser se usa para código Calcpad

### 5. MultLangProcessor ejecuta los bloques
```
[11:54:40] MultLangProcessor: Processing language 'python', 1 blocks
[11:54:47] MultLangProcessor: Processing language 'powershell', 1 blocks
```
- **SÍ SE EJECUTAN CORRECTAMENTE**
- Los resultados se insertan como comentarios Calcpad ('Python: 5 + 10 = 15')

### 6. Resultado final
```
[11:54:48] GlobalParser: HasExternalCode=False
[11:54:48] PATH: Calcpad - ExpressionParser will be USED
```

## Conclusión

**EL CÓDIGO SÍ SE EJECUTA** pero:
- `HasExternalCode=False` porque es modo MIXTO
- En modo mixto, se procesan bloques externos PRIMERO
- Luego se usa ExpressionParser para código Calcpad

## Verificación del Bug Original

### Bug #1: MultLangConfig.json con directivas incorrectas ✅ CORREGIDO
**Estado:** Línea 5 tenía `"directive": "#python"`, ahora tiene `"directive": "@{python}"`
**Solución:** Copiado `Calcpad.Common\MultLangCode\MultLangConfig.json` a `Calcpad.Cli\bin\Debug\net10.0\`

### Bug #2: CalcpadReader busca `#python` en lugar de `@{python}` ⚠️ REVISAR
**Ubicación:** CalcpadReader.cs líneas 57-70
```csharp
if (trimmedLine.StartsWith("#") && !trimmedLine.StartsWith("#hide") &&
    !trimmedLine.StartsWith("#show") && !trimmedLine.StartsWith("#pre") &&
    !trimmedLine.StartsWith("#post") && !trimmedLine.StartsWith("#val") &&
    !trimmedLine.StartsWith("#equ") && !trimmedLine.StartsWith("#noc"))
{
    if (trimmedLine.Contains("end"))
        insideLanguageBlock = false;
    else
        insideLanguageBlock = true;
}
```
**Problema:** Esta lógica parece estar diseñada para la sintaxis antigua `#python` ... `#end python`
**Impacto:** NO afecta la ejecución porque MultLangProcessor usa las directivas correctas

## Logs de Evidencia

```
[11:54:40] CalcpadProcessor initialized with 18 languages
[11:54:40] GlobalParser.Process: HasCalcpadCode=True
[11:54:40] PATH 1A: MIXED MODE - Setting hasExternalCode=false
[11:54:40] MultLangProcessor.Process() START
[11:54:40] MultLangProcessor: Found 2 language types
[11:54:40] MultLangProcessor: Processing language 'python', 1 blocks
[11:54:47] MultLangProcessor: Processing language 'powershell', 1 blocks
[11:54:48] MultLangProcessor returnHtml=FALSE output length: 322
[11:54:48] MultLangProcessor returnHtml=FALSE first 500 chars:
"Prueba de MultLangCode con Calcpad
'Calculo en Calcpad:
a = 5
b = 10
c = a + b

'Python: 5 + 10 = 15          <-- EJECUTADO CORRECTAMENTE
'Raiz cuadrada de 15: 3.8730  <-- EJECUTADO CORRECTAMENTE

'Mas calculos en Calcpad:
d = c * 2
e = sqr(d)

'PowerShell: 5 + 10 = 15      <-- EJECUTADO CORRECTAMENTE
'Fecha actual: 2026-01-18     <-- EJECUTADO CORRECTAMENTE
```

## ¿Los bloques se ejecutan o no?

**SÍ SE EJECUTAN CORRECTAMENTE** ✅

El log muestra:
- Python calculó 5 + 10 = 15
- Python calculó raíz de 15 = 3.8730
- PowerShell calculó 5 + 10 = 15
- PowerShell obtuvo fecha actual: 2026-01-18

## Entonces ¿cuál es el problema real?

Necesito verificar:
1. ¿El código se ejecuta pero no muestra la salida?
2. ¿El HTML final no incluye los resultados?
3. ¿Hay un error después de la ejecución?

**ACCIÓN:** Necesito ver el archivo de salida HTML para confirmar si los resultados aparecen.
