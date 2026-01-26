# 📋 PLAN FASE 2: Implementación WPF UI

## 🎯 Objetivo
Crear una interfaz gráfica WPF para el depurador genérico, reutilizando el core ya validado de la Fase 1.

## ✅ Prerequisitos (Ya completados)
- ✅ GenericDebugger.Core funcional (94% tests passing)
- ✅ CSharpScriptEngine validado (100% tests passing)
- ✅ Arquitectura core probada con CLI

## 📦 Componentes a Implementar

### 1. Proyecto Base
```
GenericDebugger.WPF/
├── GenericDebugger.WPF.csproj
├── App.xaml / App.xaml.cs
├── MainWindow.xaml / MainWindow.xaml.cs
└── Resources/
```

### 2. ViewModels (MVVM Pattern)
```
ViewModels/
├── MainViewModel.cs           - ViewModel principal
├── DebugSessionViewModel.cs   - Sesión de depuración
├── VariablesViewModel.cs      - Lista de variables
├── BreakpointsViewModel.cs    - Lista de breakpoints
└── CallStackViewModel.cs      - Call stack (futuro)
```

### 3. Controls Personalizados
```
Controls/
├── CodeEditorControl.xaml     - Editor con AvalonEdit
├── VariableGridControl.xaml   - Grid de variables
├── BreakpointMargin.cs        - Click en margen para breakpoints
└── ToolbarControl.xaml        - Barra de herramientas
```

### 4. Views/Windows
```
Views/
├── MainDebugWindow.xaml       - Ventana principal
└── AboutWindow.xaml           - Ventana About (opcional)
```

### 5. Services
```
Services/
├── FileDialogService.cs       - Abrir archivos
├── EngineFactory.cs           - Crear motores de depuración
└── SettingsService.cs         - Configuración (futuro)
```

## 🎨 Diseño de UI Propuesto

```
┌─────────────────────────────────────────────────────────┐
│ Generic Debugger                          [_][□][X]     │
├─────────────────────────────────────────────────────────┤
│ File  Debug  Tools  Help                                │
├─────────────────────────────────────────────────────────┤
│ [📂 Open] [▶ Run] [⏸ Pause] [⏹ Stop] [➡ Next] [⬇ Step]│
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CODE EDITOR                    │  VARIABLES             │
│  ┌────────────────────┐        │  ┌──────────────────┐ │
│  │ 1  ● int x = 10;   │        │  │ Name  Value Type │ │
│  │ 2    int y = 20;   │        │  ├──────────────────┤ │
│  │ 3 ▶  int z = x + y;│        │  │ x     10    Int32│ │
│  │ 4    Console...    │        │  │ y     20    Int32│ │
│  │                    │        │  │ z     30    Int32│ │
│  └────────────────────┘        │  └──────────────────┘ │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ OUTPUT                                                   │
│ ┌─────────────────────────────────────────────────────┐│
│ │ La suma es: 30                                      ││
│ │ El doble es: 60                                     ││
│ └─────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────┤
│ Ready | Line 3 of 6 | Motor: C# (Roslyn)               │
└─────────────────────────────────────────────────────────┘

Leyenda:
  ● = Breakpoint
  ▶ = Línea actual
```

## 🛠️ Implementación por Pasos

### Paso 1: Proyecto Base (1-2 horas)
- [x] Crear GenericDebugger.WPF.csproj
- [ ] App.xaml con recursos globales
- [ ] MainWindow.xaml básico
- [ ] Configurar referencias a Core y Engines

### Paso 2: MainViewModel (1-2 horas)
- [ ] Implementar INotifyPropertyChanged
- [ ] Comandos: Open, Run, Step, Next, Continue
- [ ] Integración con IDebugEngine
- [ ] Propiedades observables

### Paso 3: CodeEditorControl (2-3 horas)
- [ ] Integrar AvalonEdit
- [ ] Syntax highlighting para C#
- [ ] Numeración de líneas
- [ ] Highlight de línea actual
- [ ] BreakpointMargin (click para agregar/quitar)

### Paso 4: VariableGridControl (1 hora)
- [ ] DataGrid con columnas: Name, Value, Type
- [ ] Binding a VariablesViewModel
- [ ] Highlight de variables cambiadas
- [ ] Auto-refresh cuando cambian

### Paso 5: Toolbar y Comandos (1 hora)
- [ ] Botones: Open, Run, Pause, Stop, Next, Step
- [ ] Shortcuts: F5, F10, F11
- [ ] Enable/Disable según estado

### Paso 6: Output Panel (30 min)
- [ ] TextBox para mostrar Console.WriteLine
- [ ] Auto-scroll
- [ ] Clear button

### Paso 7: Status Bar (30 min)
- [ ] Línea actual / Total
- [ ] Motor activo
- [ ] Estado (Running/Paused/Stopped)

### Paso 8: Integración Final (2-3 horas)
- [ ] Conectar todos los componentes
- [ ] Event handlers
- [ ] Sincronización UI-Engine
- [ ] Testing manual

### Paso 9: Polish (1-2 horas)
- [ ] Iconos
- [ ] Colores y estilos
- [ ] Mensajes de error
- [ ] Tooltips

## 📦 Paquetes NuGet Necesarios

```xml
<ItemGroup>
  <!-- UI Framework -->
  <PackageReference Include="AvalonEdit" Version="6.3.0.90" />

  <!-- MVVM Helpers -->
  <PackageReference Include="CommunityToolkit.Mvvm" Version="8.2.2" />

  <!-- Icons (opcional) -->
  <PackageReference Include="MaterialDesignThemes" Version="5.0.0" />
</ItemGroup>
```

## 🎯 Opciones de Implementación

### Opción A: Implementación Completa (8-12 horas)
✅ Todos los pasos 1-9
✅ UI pulida y profesional
✅ Todas las características

### Opción B: MVP Funcional (4-6 horas)
✅ Pasos 1-6 (lo esencial)
⚠️ Sin polish ni iconos fancy
✅ Funcionalmente completo

### Opción C: Incrementos (tu eliges)
✅ Implemento paso por paso
✅ Pruebas después de cada paso
✅ Tú decides si continuar

## 🔍 Testing de WPF

```
GenericDebugger.WPF.Tests/
├── ViewModels/
│   └── MainViewModelTests.cs
├── Integration/
│   └── UIIntegrationTests.cs
└── Manual/
    └── TestScenarios.md
```

## 📋 Criterios de Éxito

✅ Carga archivos .cs
✅ Muestra código con syntax highlighting
✅ Click en margen agrega breakpoints
✅ Botón Run ejecuta código
✅ Variables se actualizan en tiempo real
✅ Línea actual se resalta
✅ Output se muestra en panel
✅ Breakpoints funcionan
✅ Shortcuts F5/F10/F11 funcionan

## 🚀 Próximos Pasos

**¿Qué opción prefieres?**

A) Implementación completa (todos los features)
B) MVP funcional (solo lo esencial)
C) Paso a paso (yo te muestro cada paso)

**También puedo:**
- Mostrar mockups de la UI antes de implementar
- Crear prototipos rápidos para que apruebes el diseño
- Implementar features específicos que te interesen más

---

**Tiempo estimado:**
- Opción A: 8-12 horas
- Opción B: 4-6 horas
- Opción C: A tu ritmo

**Complejidad:**
- Opción A: Alta (pero UI profesional)
- Opción B: Media (funcional pero básico)
- Opción C: Flexible
