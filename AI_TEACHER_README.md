# 🤖 AI Teacher - Profesor de IA Integrado en Calcpad Debugger

El Calcpad Debugger ahora incluye un **profesor de IA** integrado que te ayuda a entender WPF, C#, XAML y el código fuente de Calcpad mientras depuras.

## Características Principales

### 1. Profesor Experto en Múltiples Temas
El AI Teacher está especializado en:
- **WPF/XAML**: Bindings, DataTemplates, Styles, Controls, Layouts, MVVM
- **C# Avanzado**: LINQ, async/await, delegates, events, generics, reflection
- **Arquitectura de Calcpad**: Parser, procesador, ejecución de lenguajes externos
- **Debugging**: Análisis de código línea por línea

### 2. Contexto Inteligente
Puedes agregar contexto del código actual:
- **+ Código .cpd**: Envía el archivo .cpd completo que estás depurando
- **+ Código C# actual**: Envía el código fuente C# que estás viendo
- **+ Texto seleccionado**: Envía solo una porción de código seleccionada

### 3. Conversación Continua
- Mantiene el historial de la conversación
- Claude recuerda lo que preguntaste antes
- Puedes hacer preguntas de seguimiento

---

## Configuración Inicial

### Paso 1: Obtener API Key de Anthropic

1. Ve a [https://console.anthropic.com/](https://console.anthropic.com/)
2. Crea una cuenta o inicia sesión
3. Ve a "API Keys" en el panel
4. Crea una nueva API key
5. Copia la clave (empieza con `sk-ant-api03-...`)

### Paso 2: Configurar la API Key

Hay dos métodos:

#### Método 1: Archivo .env (Recomendado)

1. Ve a la carpeta del depurador:
   ```
   CalcpadDebugger\bin\Release\net10.0-windows\
   ```

2. Copia el archivo `.env.example` como `.env`:
   ```bash
   cp .env.example .env
   ```

3. Edita `.env` y reemplaza `tu-api-key-aqui` con tu clave real:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
   ```

#### Método 2: Variable de Entorno del Sistema

**Windows (PowerShell)**:
```powershell
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-api03-xxxxx', 'User')
```

**Windows (CMD)**:
```cmd
setx ANTHROPIC_API_KEY "sk-ant-api03-xxxxx"
```

**Linux/Mac**:
```bash
export ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
# Agregar a ~/.bashrc o ~/.zshrc para hacerlo permanente
```

### Paso 3: Iniciar el Depurador

```bash
CalcpadDebugger.exe archivo.cpd
```

Si la API key está configurada correctamente, verás:
```
✓ AI Teacher inicializado correctamente
```

---

## Cómo Usar el AI Teacher

### 1. Abrir el Panel de AI Teacher

1. Inicia el depurador
2. Ve a la pestaña **🤖 AI Teacher (Claude)** en la parte inferior

### 2. Hacer Preguntas Simples

Simplemente escribe tu pregunta y presiona **Ctrl+Enter** o haz clic en **🚀 Preguntar**.

**Ejemplos de preguntas**:
```
¿Qué es un DataTemplate en WPF?

¿Cómo funciona async/await en C#?

Explícame qué hace CalcpadProcessor

¿Cuál es la diferencia entre ObservableCollection y List?
```

### 3. Preguntar sobre Código Específico

#### Opción A: Agregar todo el archivo .cpd
1. Haz clic en **+ Código .cpd**
2. Escribe tu pregunta, por ejemplo:
   ```
   ¿Qué hace este código? Explícalo línea por línea
   ```
3. Presiona **Ctrl+Enter**

#### Opción B: Agregar código C# que estás viendo
1. Selecciona un archivo C# en el ComboBox (ej: `LanguageExecutor.cs`)
2. Haz clic en **+ Código C# actual**
3. Escribe tu pregunta:
   ```
   ¿Qué patrón de diseño se usa aquí?

   ¿Cómo podría mejorar este código?
   ```

#### Opción C: Seleccionar una porción de código
1. Selecciona algunas líneas de código en el editor .cpd o C#
2. Haz clic en **+ Texto seleccionado**
3. Pregunta:
   ```
   ¿Qué hace exactamente este bloque?

   ¿Hay algún bug potencial aquí?
   ```

### 4. Preguntas de Seguimiento

El AI Teacher recuerda la conversación, puedes hacer preguntas de seguimiento:

**Tú**: ¿Qué es MVVM en WPF?

**Claude**: [Explicación detallada de MVVM]

**Tú**: ¿Puedes mostrarme un ejemplo simple?

**Claude**: [Ejemplo de código MVVM]

**Tú**: ¿Cómo se hace el binding de un botón en ese ejemplo?

**Claude**: [Explicación específica sobre binding de botones]

### 5. Limpiar el Chat

Si quieres empezar una conversación nueva:
1. Haz clic en **🗑 Limpiar Chat**
2. Confirma

Esto borra el historial de conversación.

---

## Ejemplos de Uso

### Ejemplo 1: Entender un Concepto de WPF

**Pregunta**:
```
¿Qué es un DataTemplate y para qué se usa en WPF?
```

**Respuesta de Claude**:
```
Un DataTemplate en WPF es una plantilla que define cómo se visualizan
los datos. Es como un "molde" que le dice a WPF cómo mostrar objetos.

[Explicación detallada con ejemplos...]
```

### Ejemplo 2: Analizar Código Calcpad

**Pasos**:
1. Carga `ejemplo-multiples-lenguajes.cpd` en el depurador
2. Haz clic en **+ Código .cpd**
3. Pregunta:
   ```
   Explícame este archivo .cpd línea por línea.
   ¿Cómo funciona la ejecución de múltiples lenguajes?
   ```

**Resultado**:
Claude analizará el código y explicará:
- Qué hace cada directiva `@{python}`, `@{cpp}`, etc.
- Cómo Calcpad ejecuta cada bloque
- Qué significa "independiente" para cada bloque

### Ejemplo 3: Debugging Paso a Paso

**Escenario**: Estás depurando y llegaste a `LanguageExecutor.cs:68`

**Pasos**:
1. Selecciona las líneas 63-79 en el editor C#
2. Haz clic en **+ Texto seleccionado**
3. Pregunta:
   ```
   Estoy depurando y la ejecución se detuvo aquí.
   ¿Qué está haciendo este código?
   ¿Qué debería verificar antes de continuar?
   ```

**Resultado**:
Claude te explicará qué hace esa sección y qué condiciones verificar.

### Ejemplo 4: Aprender un Patrón de Diseño

**Pregunta**:
```
Veo que CalcpadProcessor usa ExecutionTracker.
¿Qué patrón de diseño es esto?
¿Por qué es mejor que simplemente llamar métodos directamente?
```

**Respuesta esperada**:
- Explicación del patrón Observer
- Ventajas: bajo acoplamiento, extensibilidad
- Ejemplo de cómo se usa en Calcpad

---

## Tips para Mejores Respuestas

### ✅ Buenas Prácticas

1. **Sé específico**:
   - ❌ "¿Qué es esto?"
   - ✅ "¿Qué hace el método ExecuteSingleLine() en MainWindow.cs?"

2. **Proporciona contexto cuando sea útil**:
   - Usa los botones de contexto para código relevante
   - Menciona qué estás intentando hacer

3. **Haz preguntas de seguimiento**:
   - Si algo no quedó claro, pregunta de nuevo
   - Pide ejemplos si necesitas

4. **Pregunta por alternativas**:
   - "¿Hay una mejor forma de hacer esto?"
   - "¿Qué pros y contras tiene este enfoque?"

### ❌ Evitar

1. **Preguntas demasiado genéricas**:
   - "Enséñame WPF" (muy amplio)
   - Mejor: "¿Cómo funciona el binding en WPF?"

2. **Enviar código sin contexto**:
   - Si envías código, explica qué quieres saber

3. **Esperar que compile/ejecute código**:
   - El AI Teacher es un tutor, no un compilador
   - Te explicará el código, pero no lo ejecutará

---

## Solución de Problemas

### ❌ El botón "🚀 Preguntar" está deshabilitado

**Posibles causas**:
1. No se configuró la API key
2. La API key es inválida

**Solución**:
1. Verifica que el archivo `.env` existe y tiene la clave correcta
2. Reinicia el depurador
3. Revisa el log en la pestaña "Output / Log" para más detalles

### ❌ Error: "Authentication error"

**Causa**: API key inválida o expirada

**Solución**:
1. Ve a https://console.anthropic.com/
2. Verifica que tu API key es correcta
3. Copia la clave nuevamente al archivo `.env`
4. Reinicia el depurador

### ❌ Error: "Rate limit exceeded"

**Causa**: Has excedido el límite de requests de la API

**Solución**:
1. Espera unos minutos
2. Revisa tu plan en Anthropic Console
3. Considera actualizar tu plan si usas mucho el AI Teacher

### ❌ Error: "Timeout"

**Causa**: La respuesta tardó demasiado (puede ser una pregunta muy compleja)

**Solución**:
1. Intenta hacer la pregunta de forma más simple
2. Divide preguntas complejas en varias más sencillas
3. Verifica tu conexión a internet

---

## Preguntas Frecuentes (FAQ)

### ¿Cuánto cuesta usar el AI Teacher?

El AI Teacher usa la API de Claude, que tiene costos:
- **Modelo usado**: Claude 3.5 Sonnet
- **Costo aproximado**: ~$3 USD por 1 millón de tokens
- **Conversación típica**: 5-10 preguntas = ~$0.01-0.05 USD

**Tip**: Anthropic da créditos gratuitos al crear una cuenta nueva.

### ¿El AI Teacher tiene acceso a internet?

No. El AI Teacher solo conoce:
- Conceptos generales de C#, WPF, XAML
- El código que le envíes explícitamente
- El contexto del sistema (prompt sobre Calcpad)

No puede buscar en internet ni acceder a archivos fuera del depurador.

### ¿Puedo usar otro modelo de Claude?

Sí, puedes editar `AITeacherService.cs` y cambiar:
```csharp
private const string MODEL = "claude-3-5-sonnet-20241022";
```

Opciones:
- `claude-3-5-sonnet-20241022` (actual, recomendado)
- `claude-3-opus-20240229` (más potente, más caro)
- `claude-3-haiku-20240307` (más rápido, más barato)

### ¿El historial de chat se guarda?

No. El historial solo existe durante la sesión actual.
- Si cierras el depurador, se pierde
- Usa "Limpiar Chat" para empezar una conversación nueva

### ¿Puedo compartir mi API key?

**¡NO!** Tu API key es personal y secreta.
- No la compartas con nadie
- No la subas a repositorios git
- Cada desarrollador debe tener su propia clave

---

## Roadmap Futuro

### Features Planeadas:

1. **Exportar Conversaciones**
   - Guardar chat como .md o .txt
   - Útil para documentación o referencia

2. **Snippets de Código**
   - Pedir código de ejemplo
   - Insertar directamente en el editor

3. **Modo "Explicación Automática"**
   - El AI Teacher explica automáticamente cada línea al depurar
   - Modo "profesor en vivo"

4. **Análisis de Performance**
   - Sugerencias de optimización
   - Análisis de complejidad algorítmica

5. **Integración con Documentación**
   - Enlaces automáticos a docs de Microsoft
   - Referencias a código de ejemplo

---

## Contribuir

Si encuentras bugs o tienes ideas para mejorar el AI Teacher:

1. Reporta issues con ejemplos de preguntas problemáticas
2. Sugiere mejoras al sistema de prompts
3. Comparte casos de uso interesantes

---

## Créditos

- **IA**: Claude 3.5 Sonnet de Anthropic
- **Integración**: Desarrollado para Calcpad Debugger
- **API**: Anthropic Messages API v1

**Disfruta aprendiendo con tu profesor de IA personal** 🤖📚
