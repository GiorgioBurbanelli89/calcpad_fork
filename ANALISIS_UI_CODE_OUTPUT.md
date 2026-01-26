# ANÁLISIS - Paneles Code y Output en Calcpad WPF

## Estado Actual del Sistema

### Paneles Principales

**InputFrame (Code):**
- Control: `RichTextBox` (línea 252-254)
- Tipo: RichTextBox de WPF
- Contenido: Código fuente .cpd editable
- Header: "Code" (MainWindowResources.Code)

**OutputFrame (Output):**
- Control: `WebView2` (línea 267, 2878)
- Tipo: Microsoft WebView2 (navegador embebido)
- Contenido: HTML resultado del procesamiento
- Header: Variable - puede ser "Output", "Input" o "Unwarped_code"

## Uso de WebViewer.Tag

El sistema usa `WebViewer.Tag` como **flag booleano** para indicar el modo de visualización:

```csharp
// Línea 219
private bool IsUnwarpedCode => WebViewer.Tag is bool b && b;

// Cuando muestra código sin procesar:
WebViewer.Tag = true;           // Línea 571, 1542
OutputFrame.Header = "Unwarped_code";

// Cuando muestra resultado procesado:
WebViewer.Tag = false;          // Línea 1535, 1565
OutputFrame.Header = "Output";
```

## Flujo de Actualización de Paneles

### Escenario 1: Código Normal de Calcpad (sin MultLang)

```
Usuario escribe en RichTextBox (InputFrame)
    ↓
Presiona F5 (Calculate)
    ↓
CalculateAsync() línea 1326
    ↓
_calcpadProcessor.ProcessCode(inputCode)
    ↓
processingResult.MultilangProcessed = FALSE
    ↓
_parser.Parse(outputText)
    ↓
WebViewer.NavigateToString(_parser.HtmlResult)  ← Actualiza OUTPUT
    ↓
OutputFrame.Header = "Output"
WebViewer.Tag = false
```

**PROBLEMA POTENCIAL:**
- InputFrame (RichTextBox) **NO se modifica** durante el proceso
- OutputFrame (WebViewer) **SÍ se actualiza** con el HTML resultado

### Escenario 2: Código con MultLang (@{python}, @{powershell})

```
Usuario escribe en RichTextBox (InputFrame):
    @{python}
    print("Hola")
    @{end python}
    ↓
Presiona F5 (Calculate)
    ↓
CalculateAsync() línea 1326
    ↓
STEP 1: Muestra comentarios iniciales (línea 1372)
    WebViewer.NavigateToString(initialHtml);  ← OUTPUT actualizado
    ↓
STEP 2: Callback de progreso (línea 1379-1422)
    progressCallback("Ejecutando Python...")
    WebViewer.NavigateToString(progressHtml);  ← OUTPUT actualizado en tiempo real
    ↓
STEP 3: Procesamiento (línea 1426)
    _calcpadProcessor.ProcessCode(inputCode, progressCallback)
    ↓
processingResult.MultilangProcessed = TRUE
    ↓
STEP 4: Procesar marcadores Calcpad inline (línea 1502)
    GlobalParser.ProcessCalcpadInlineMarkers(outputText)
    ↓
STEP 5: Mostrar resultado final (línea 1536)
    htmlResult = HtmlApplyWorksheet(outputText);
    WebViewer.NavigateToString(htmlResult);  ← OUTPUT actualizado final
    OutputFrame.Header = "Output"
    WebViewer.Tag = false
```

**PROBLEMA POTENCIAL:**
- InputFrame (RichTextBox) **NUNCA se modifica**
- El código `@{python}...@{end python}` **permanece visible** en el panel Code
- OutputFrame muestra el resultado de la ejecución

## Problemas Detectados

### 1. ❌ Sin AutomationProperties

**Línea 2311 (InputFrame):**
```xml
<GroupBox x:Name="InputFrame" Header="{x:Static wpf:MainWindowResources.Code}" ...>
```

**Falta:**
```xml
AutomationProperties.Name="Code Panel"
AutomationProperties.AutomationId="InputFrame"
```

**Línea 2873 (OutputFrame):**
```xml
<GroupBox x:Name="OutputFrame" Grid.Column="2" Header="{x:Static wpf:MainWindowResources.Output}" ...>
```

**Falta:**
```xml
AutomationProperties.Name="Output Panel"
AutomationProperties.AutomationId="OutputFrame"
```

**Impacto:**
- Herramientas de UI Automation no pueden identificar estos controles
- Inspect.exe no muestra identificadores únicos
- Scripts de testing no pueden referenciarlos

### 2. ⚠️ WebViewer.Tag usado como flag interno

**Problema:** `WebViewer.Tag` se usa internamente pero no está documentado

**Ubicaciones:**
- Línea 219: `private bool IsUnwarpedCode => WebViewer.Tag is bool b && b;`
- Línea 571: `WebViewer.Tag = true;` (modo código sin procesar)
- Línea 1535: `WebViewer.Tag = false;` (modo resultado)
- Línea 1542: `WebViewer.Tag = true;` (modo código sin procesar)
- Línea 1565: `WebViewer.Tag = false;` (modo resultado)

**Mejor práctica:** Usar una propiedad privada en lugar de Tag

### 3. ⚠️ OutputFrame.Header cambia dinámicamente

**Cambios del header:**
```csharp
// Línea 388 - SetOutputFrameHeader()
OutputFrame.Header = isWebForm ? "Input" : "Output";

// Línea 1546
OutputFrame.Header = "Unwarped_code";
```

**Problema:** UI Automation puede no detectar estos cambios si no hay eventos

### 4. ⚠️ WebViewer.NavigateToString() sin await

**Problema:** Todas las llamadas a `WebViewer.NavigateToString()` son síncronas

**Ubicaciones:**
- Línea 1372: `WebViewer.NavigateToString(initialHtml);`
- Línea 1418: `WebViewer.NavigateToString(progressHtml);`
- Línea 1536: (a través de HtmlApplyWorksheet)

**Riesgo:** Si WebView2 no está inicializado, puede fallar silenciosamente

## Comportamiento Observado

### ¿Qué VE el usuario cuando ejecuta código MultLang?

**Panel Code (InputFrame):**
```
@{python}
import math
print(f"Resultado: {math.sqrt(16)}")
@{end python}
```
↑ Este texto **NO cambia** durante la ejecución

**Panel Output (OutputFrame):**
```
⏳ Ejecutando Python...
---
Python:
Resultado: 4.0
---
```
↑ Este HTML **SÍ se actualiza** progresivamente

### ¿Qué pasa si Code y Output se confunden?

**NO puede pasar** porque son controles completamente diferentes:
- **Code** = RichTextBox (editor de texto)
- **Output** = WebView2 (navegador HTML)

**Pero SÍ puede haber confusión visual si:**
- El usuario no ve que Output se actualizó
- WebView2 no renderiza correctamente el HTML
- Hay errores silenciosos en NavigateToString()

## Soluciones Propuestas

### Solución 1: Agregar AutomationProperties ✅ CRÍTICO

**Editar MainWindow.xaml línea 2311:**
```xml
<GroupBox x:Name="InputFrame"
          Header="{x:Static wpf:MainWindowResources.Code}"
          AutomationProperties.Name="Code Editor"
          AutomationProperties.AutomationId="InputFrame"
          AutomationProperties.HelpText="Calcpad code editor with syntax highlighting"
          FontSize="13" FontFamily="Segoe UI Semibold"
          Margin="6,1,4,1" MinWidth="580"
          BorderBrush="{DynamicResource {x:Static SystemColors.ActiveBorderBrushKey}}">
```

**Editar MainWindow.xaml línea 2873:**
```xml
<GroupBox x:Name="OutputFrame" Grid.Column="2"
          FontFamily="Segoe UI Semibold" FontWeight="Bold" FontSize="13"
          VerticalContentAlignment="Stretch" Margin="4,1,6,1"
          BorderBrush="#AACCCCCC" Background="White"
          Header="{x:Static wpf:MainWindowResources.Output}"
          AutomationProperties.Name="Output Viewer"
          AutomationProperties.AutomationId="OutputFrame"
          AutomationProperties.HelpText="Calculation results and rendered output">
    <Wpf:WebView2 x:Name="WebViewer"
                  Margin="5,5,5,5"
                  AutomationProperties.Name="Output HTML View"
                  AutomationProperties.AutomationId="WebViewer"
                  AutomationProperties.HelpText="HTML rendered output with calculations"
                  KeyUp="WebViewer_KeyUp"
                  PreviewKeyDown="WebViewer_PreviewKeyDown"
                  NavigationCompleted="WebViewer_NavigationCompleted"
                  WebMessageReceived="WebViewer_WebMessageReceived" />
</GroupBox>
```

**También para RichTextBox (encontrar en XAML y agregar):**
```xml
<RichTextBox x:Name="RichTextBox"
             ...
             AutomationProperties.Name="Code Editor TextBox"
             AutomationProperties.AutomationId="RichTextBox"
             AutomationProperties.HelpText="Main code editor for Calcpad scripts"
             ... />
```

### Solución 2: Reemplazar WebViewer.Tag con propiedad privada

**Agregar en MainWindow.xaml.cs después de línea 140:**
```csharp
private bool _isShowingUnwarpedCode;
private bool IsUnwarpedCode
{
    get => _isShowingUnwarpedCode;
    set
    {
        _isShowingUnwarpedCode = value;
        // Notificar cambio para UI Automation
        if (value)
            OutputFrame.SetValue(AutomationProperties.NameProperty, "Output Viewer - Unwarped Code");
        else
            OutputFrame.SetValue(AutomationProperties.NameProperty, "Output Viewer - Results");
    }
}
```

**Reemplazar línea 219:**
```csharp
// ANTES:
private bool IsUnwarpedCode => WebViewer.Tag is bool b && b;

// DESPUÉS:
// (ya está definida arriba)
```

**Reemplazar todas las asignaciones:**
```csharp
// Línea 571: WebViewer.Tag = true;
IsUnwarpedCode = true;

// Línea 1535: WebViewer.Tag = false;
IsUnwarpedCode = false;

// Línea 1542: WebViewer.Tag = true;
IsUnwarpedCode = true;

// Línea 1565: WebViewer.Tag = false;
IsUnwarpedCode = false;
```

### Solución 3: Usar async/await para WebView2

**Agregar método helper:**
```csharp
private async Task NavigateOutputToHtmlAsync(string html)
{
    try
    {
        // Asegurar que WebView2 está inicializado
        await WebViewer.EnsureCoreWebView2Async();

        // Navegar al contenido
        WebViewer.NavigateToString(html);

        // Notificar cambio para UI Automation
        await Task.Delay(100); // Dar tiempo para que renderice

        // Disparar evento para automation
        if (AutomationPeer.ListenerExists(AutomationEvents.LiveRegionChanged))
        {
            var peer = UIElementAutomationPeer.FromElement(WebViewer);
            peer?.RaiseAutomationEvent(AutomationEvents.LiveRegionChanged);
        }
    }
    catch (Exception ex)
    {
        System.Diagnostics.Debug.WriteLine($"Error navigating to HTML: {ex.Message}");
    }
}
```

**Reemplazar todas las llamadas a WebViewer.NavigateToString():**
```csharp
// Línea 1372:
await NavigateOutputToHtmlAsync(initialHtml);

// Línea 1418:
await NavigateOutputToHtmlAsync(progressHtml);

// Etc.
```

### Solución 4: Agregar LiveRegion para Output

**Editar MainWindow.xaml línea 2873:**
```xml
<GroupBox x:Name="OutputFrame" Grid.Column="2"
          ...
          AutomationProperties.LiveSetting="Polite"
          AutomationProperties.ItemStatus="Updating">
```

Esto hace que UI Automation notifique cuando cambia el contenido.

## Testing con UI Automation

### Código C# para acceder a los paneles:

```csharp
using System.Windows.Automation;

// Encontrar ventana principal
var mainWindow = AutomationElement.RootElement.FindFirst(
    TreeScope.Children,
    new PropertyCondition(AutomationElement.NameProperty, "Calcpad VM 7.5.8")
);

// Encontrar panel Code
var codePanel = mainWindow.FindFirst(
    TreeScope.Descendants,
    new PropertyCondition(AutomationElement.AutomationIdProperty, "InputFrame")
);

// Encontrar panel Output
var outputPanel = mainWindow.FindFirst(
    TreeScope.Descendants,
    new PropertyCondition(AutomationElement.AutomationIdProperty, "OutputFrame")
);

// Obtener contenido del RichTextBox
var richTextBox = mainWindow.FindFirst(
    TreeScope.Descendants,
    new PropertyCondition(AutomationElement.AutomationIdProperty, "RichTextBox")
);

var textPattern = richTextBox.GetCurrentPattern(TextPattern.Pattern) as TextPattern;
string codeText = textPattern.DocumentRange.GetText(-1);

Console.WriteLine($"Code: {codeText}");
```

## Conclusión

**El sistema funciona correctamente** en cuanto a funcionalidad:
- Code panel mantiene el código fuente
- Output panel se actualiza con resultados

**Pero falta soporte para UI Automation:**
- ❌ No hay AutomationProperties en los controles principales
- ❌ No hay eventos de LiveRegion para cambios dinámicos
- ❌ No hay IDs únicos para testing/automation

**Implementar Soluciones 1-4 agregará soporte completo para:**
- ✅ Herramientas de accessibility (lectores de pantalla)
- ✅ Testing automatizado con UI Automation
- ✅ Inspect.exe y otras herramientas de debugging
- ✅ Scripts de automation externos
