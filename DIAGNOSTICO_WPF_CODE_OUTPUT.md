# DIAGNÓSTICO - WPF Code y Output con MultLang

## Estructura de la UI

### InputFrame (Panel Code)
```xml
<GroupBox x:Name="InputFrame" Header="Code" ...>
    <RichTextBox x:Name="RichTextBox" .../>
</GroupBox>
```

### OutputFrame (Panel Output)
```xml
<GroupBox x:Name="OutputFrame" Header="Output" ...>
    <WebView2 x:Name="WebViewer" .../>
</GroupBox>
```

## Flujo de Procesamiento MultLang en WPF

### Cuando presionas F5 (Calculate):

**1. CalculateAsync() línea 1326:**
```csharp
// Lee código del editor
string inputCode = InputText;

// STEP 1: Muestra comentarios Calcpad inmediatamente en WebViewer
var calcpadComments = extractar_comentarios(inputCode);
WebViewer.NavigateToString(initialHtml); // ← Actualiza OUTPUT

// STEP 2: Callback de progreso durante ejecución externa
Action<string> progressCallback = (message) =>
{
    Dispatcher.Invoke(() => {
        WebViewer.NavigateToString(progressHtml); // ← Actualiza OUTPUT
    });
};

// STEP 3: Procesar código
var result = _calcpadProcessor.ProcessCode(inputCode, progressCallback);

// STEP 4: Si MultilangProcessed=true
if (result.MultilangProcessed)
{
    // Código externo fue ejecutado
    // Output ya está en HTML completo
    WebViewer.NavigateToString(htmlResult); // ← Actualiza OUTPUT FINAL
}
else
{
    // Código Calcpad normal
    _parser.Parse(outputText);
    WebViewer.NavigateToString(_parser.HtmlResult); // ← Actualiza OUTPUT
}
```

## Posibles Problemas

### 1. ❌ Falta AutomationProperties en XAML

**Problema:** Los frames NO tienen `AutomationProperties.Name` configurado

**Actual:**
```xml
<GroupBox x:Name="InputFrame" Header="Code" ...>
```

**Debería ser:**
```xml
<GroupBox x:Name="InputFrame"
          Header="Code"
          AutomationProperties.Name="CodePanel"
          AutomationProperties.AutomationId="InputFrame" ...>
```

**Y para Output:**
```xml
<GroupBox x:Name="OutputFrame"
          Header="Output"
          AutomationProperties.Name="OutputPanel"
          AutomationProperties.AutomationId="OutputFrame" ...>
    <WebView2 x:Name="WebViewer"
              AutomationProperties.Name="OutputWebView"
              AutomationProperties.AutomationId="WebViewer" .../>
```

### 2. ⚠️ RichTextBox vs WebView2 sincronización

**Problema potencial:** Cuando ejecutas código MultLang:
- El **CODE** panel muestra el texto original (con `@{python}...@{end python}`)
- El **OUTPUT** panel muestra el resultado procesado

**Pero:** Si el usuario edita código MIENTRAS se está ejecutando, puede haber desincronización.

### 3. ⚠️ WebView2 puede no estar listo

**Problema:** `WebViewer.NavigateToString()` puede fallar si WebView2 no está inicializado.

**Verificar en MainWindow.xaml.cs línea 267:**
```csharp
_wv2Warper = new WebView2Wrapper(WebViewer, $"{docPath}\\blank.html");
```

¿WebView2 está completamente inicializado antes de llamar a `NavigateToString()`?

## Prueba de Diagnóstico

### Paso 1: Verificar que WebViewer se actualiza

1. Abre Calcpad WPF
2. Carga `test_multilang.cpd`
3. Presiona F5
4. **Observa:**
   - ¿Se muestra "⏳ Processing..." en el panel OUTPUT?
   - ¿Aparecen los resultados de Python/PowerShell?
   - ¿O el panel OUTPUT queda en blanco/congelado?

### Paso 2: Ver log de debug

```powershell
cat C:\Users\j-b-j\AppData\Local\Temp\calcpad-debug.txt | tail -50
```

Buscar:
```
[HH:mm:ss] MainWindow: Calling ProcessCalcpadInlineMarkers...
[HH:mm:ss] MainWindow: Output text length = XXXX
```

### Paso 3: Verificar AutomationProperties

**Con Inspect.exe (Windows SDK):**
```powershell
# Buscar Inspect.exe en:
# C:\Program Files (x86)\Windows Kits\10\bin\<version>\x64\inspect.exe

# Ejecutar:
.\inspect.exe

# Luego:
# 1. Abrir Calcpad WPF
# 2. En Inspect.exe, hacer hover sobre el panel "Code"
# 3. Verificar si aparece "AutomationId" en las propiedades
```

## Posibles Causas del Problema

### Causa 1: WebView2 no actualiza correctamente

**Síntoma:** El panel OUTPUT no muestra nada o muestra contenido viejo

**Solución:**
```csharp
// Asegurar que WebView2 está listo antes de navegar
private async Task UpdateOutputAsync(string html)
{
    await WebViewer.EnsureCoreWebView2Async();
    WebViewer.NavigateToString(html);
}
```

### Causa 2: Dispatcher.Invoke() no se ejecuta

**Síntoma:** Los mensajes de progreso no aparecen

**Debug:**
```csharp
Action<string> progressCallback = (message) =>
{
    System.Diagnostics.Debug.WriteLine($"Progress: {message}");
    Dispatcher.Invoke(() => {
        System.Diagnostics.Debug.WriteLine($"UI Thread: {message}");
        WebViewer.NavigateToString(progressHtml);
    });
};
```

### Causa 3: GlobalParser no está devolviendo HTML correcto

**Debug:** Ver línea 1455 en CalculateAsync:
```csharp
if (processingResult.MultilangProcessed)
{
    // Agregar debug aquí
    System.IO.File.WriteAllText(
        @"C:\Temp\output_debug.html",
        outputText
    );
    // ...
}
```

## Recomendación de Fix

### Fix 1: Agregar AutomationProperties al XAML

**Editar MainWindow.xaml línea 2311:**
```xml
<GroupBox x:Name="InputFrame"
          Header="{x:Static wpf:MainWindowResources.Code}"
          AutomationProperties.Name="Code Panel"
          AutomationProperties.AutomationId="InputFrame"
          FontSize="13" FontFamily="Segoe UI Semibold"
          Margin="6,1,4,1" MinWidth="580"
          BorderBrush="{DynamicResource {x:Static SystemColors.ActiveBorderBrushKey}}">
```

**Y línea 2873:**
```xml
<GroupBox x:Name="OutputFrame" Grid.Column="2"
          FontFamily="Segoe UI Semibold" FontWeight="Bold" FontSize="13"
          VerticalContentAlignment="Stretch" Margin="4,1,6,1"
          BorderBrush="#AACCCCCC" Background="White"
          Header="{x:Static wpf:MainWindowResources.Output}"
          AutomationProperties.Name="Output Panel"
          AutomationProperties.AutomationId="OutputFrame">
    <Wpf:WebView2 x:Name="WebViewer"
                  Margin="5,5,5,5"
                  AutomationProperties.Name="Output Web View"
                  AutomationProperties.AutomationId="WebViewer"
                  KeyUp="WebViewer_KeyUp"
                  PreviewKeyDown="WebViewer_PreviewKeyDown"
                  NavigationCompleted="WebViewer_NavigationCompleted"
                  WebMessageReceived="WebViewer_WebMessageReceived" />
</GroupBox>
```

### Fix 2: Asegurar WebView2 está listo

**Editar CalculateAsync() para usar async/await:**
```csharp
// Cambiar todas las llamadas a WebViewer.NavigateToString()
// Por:
await UpdateOutputSafeAsync(htmlContent);

// Y agregar método helper:
private async Task UpdateOutputSafeAsync(string html)
{
    try
    {
        await WebViewer.EnsureCoreWebView2Async();
        WebViewer.NavigateToString(html);
    }
    catch (Exception ex)
    {
        System.Diagnostics.Debug.WriteLine($"Error updating output: {ex.Message}");
    }
}
```

### Fix 3: Debug logging

**Agregar al principio de CalculateAsync():**
```csharp
private async void CalculateAsync(bool toWebForm = false)
{
    try
    {
        var debugPath = Path.Combine(Path.GetTempPath(), "calcpad-wpf-debug.txt");
        File.AppendAllText(debugPath, $"\n[{DateTime.Now:HH:mm:ss}] === CalculateAsync START ===\n");
        File.AppendAllText(debugPath, $"[{DateTime.Now:HH:mm:ss}] InputText length: {InputText.Length}\n");
        File.AppendAllText(debugPath, $"[{DateTime.Now:HH:mm:ss}] WebViewer ready: {WebViewer.CoreWebView2 != null}\n");
    }
    catch { }

    // ... resto del código
}
```

## Próximo Paso

¿Qué problema específico estás viendo?

1. **Panel OUTPUT no se actualiza** cuando ejecutas código MultLang
2. **Panel CODE desaparece** o se borra
3. **Herramientas de testing/automation** no pueden acceder a los paneles
4. **Otro problema** con la UI

Dime qué observas y puedo dar un fix más específico.
