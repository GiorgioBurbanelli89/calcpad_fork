# Flujo de Trabajo Correcto: MathEditor vs AvalonEdit

**Fecha**: 2026-01-21
**Estado**: ✅ DISEÑO CORRECTO IMPLEMENTADO

---

## 🎯 Arquitectura de Calcpad

```
┌─────────────────────────────────────────────────────────────┐
│                    CALCPAD WPF                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────┐      ┌────────────────────┐        │
│  │   MATHEDITOR       │      │   AVALONEDIT       │        │
│  │   (modo Visual)    │      │   (modo Code)      │        │
│  ├────────────────────┤      ├────────────────────┤        │
│  │ • Canvas           │      │ • Editor de texto  │        │
│  │ • Renderizado      │      │ • Edición libre    │        │
│  │ • Solo lectura     │      │ • Snippets         │        │
│  │ • Visualización    │      │ • Code folding     │        │
│  │ • Ecuaciones       │      │ • Syntax highlight │        │
│  │ • Bloques externos │      │ • Modificable      │        │
│  └────────────────────┘      └────────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ DISEÑO CORRECTO

### MathEditor (modo Visual)
- **Propósito**: VISUALIZACIÓN RENDERIZADA
- **Tipo**: Canvas con elementos dibujados
- **Ecuaciones**: Se muestran formateadas (fracciones, matrices, etc.)
- **Bloques externos**: Se muestran como `| HTML [+]` con colores
- **Edición**: ❌ NO ES UN EDITOR
- **Interacción**: Click para expandir/colapsar, doble-click para ir a Code

### AvalonEdit (modo Code)
- **Propósito**: EDICIÓN DE CÓDIGO
- **Tipo**: Editor de texto completo
- **Código fuente**: Texto plano editable
- **Bloques externos**: Código HTML/CSS/C/Fortran editable
- **Edición**: ✅ TOTALMENTE EDITABLE
- **Herramientas**: Snippets, folding, syntax highlighting

---

## 🔄 Flujo de Trabajo

### Para Visualizar Ecuaciones:
```
1. Botón "Visual" → MathEditor
2. Ver ecuaciones renderizadas
3. Ver bloques externos como | HTML [+]
4. Click simple → Expandir/colapsar para revisar código
```

### Para Editar Código:
```
1. Botón "Code" → AvalonEdit
   O
   En MathEditor: Doble-click en | HTML [+] → Cambia a Code

2. Editar código libremente:
   • Escribir HTML/CSS/TypeScript
   • Usar snippets (html → Tab)
   • Usar folding (▼ para colapsar)

3. Botón "Visual" → Ver resultado renderizado
```

---

## 🎨 Ejemplo Práctico

### Caso: Editar bloque HTML

**INCORRECTO** ❌:
```
1. Modo Visual
2. Click en | HTML [+]
3. Intentar editar el código → NO FUNCIONA (es solo lectura)
```

**CORRECTO** ✅:
```
1. Modo Visual
2. Doble-click en | HTML [+]
3. Automáticamente cambia a modo Code
4. Editar el código HTML
5. Volver a Visual para ver resultado
```

O alternativamente:
```
1. Botón "Code" directamente
2. Editar código HTML
3. Botón "Visual" para ver resultado
```

---

## 💡 Por Qué Este Diseño

### Separación de Responsabilidades

**MathEditor**:
- Se especializa en RENDERIZAR ecuaciones matemáticas
- Canvas permite dibujar fracciones, matrices, integrales, etc.
- No está diseñado para ser un editor de texto
- Es como un "PDF viewer" de ecuaciones

**AvalonEdit**:
- Se especializa en EDITAR código
- Editor de texto robusto con todas las herramientas
- Snippets, autocomplete, syntax highlighting
- Es como "VS Code"

### ¿Por qué no editar en MathEditor?

1. **Complejidad**: MathEditor es un Canvas, no un TextBox
2. **Mantenimiento**: Duplicaría funcionalidad que ya existe en AvalonEdit
3. **Consistencia**: Todo el código se edita en el mismo lugar (AvalonEdit)
4. **Herramientas**: AvalonEdit tiene snippets, folding, etc. ya implementados

---

## 🔑 Conceptos Clave

### MathEditor NO es un editor de texto
```
MathEditor ≠ TextBox
MathEditor = Canvas de visualización

Equivalente a:
• PDF Viewer (solo lectura)
• Markdown Preview (renderizado)
• Ecuaciones LaTeX renderizadas
```

### AvalonEdit ES el editor
```
AvalonEdit = Editor de texto completo

Equivalente a:
• VS Code
• Notepad++
• Sublime Text
```

---

## 📋 Indicadores Visuales Implementados

### En MathEditor:
1. **Tooltip en bloques externos**: "Doble-click para editar en modo Code"
   - Pasa el mouse sobre `| HTML [+]`
   - Aparece tooltip explicando qué hacer

2. **Colores distintos por lenguaje**:
   - HTML → Naranja
   - CSS → Azul
   - C → Gris
   - Fortran → Morado
   - Indica que son bloques especiales

3. **Iconos [+] y [-]**:
   - `[+]` → Colapsado, click para expandir
   - `[-]` → Expandido, muestra código (solo lectura)

---

## ✨ Resumen Final

| Pregunta | Respuesta |
|----------|-----------|
| ¿Dónde VER ecuaciones? | MathEditor (modo Visual) |
| ¿Dónde VER bloques externos? | MathEditor → `\| HTML [+]` |
| ¿Dónde EDITAR código? | AvalonEdit (modo Code) |
| ¿Cómo cambiar a editar? | Doble-click en bloque O botón "Code" |
| ¿Por qué no editar en MathEditor? | No es un editor, es un Canvas de visualización |

---

## 🎯 Instrucciones de Uso

### Ver y Revisar Código (sin editar):
1. ✅ Modo Visual
2. ✅ Click en `| HTML [+]`
3. ✅ Ver código expandido (solo lectura)

### Editar Código:
1. ✅ Doble-click en `| HTML [+]` (cambia a modo Code)
   O
   ✅ Botón "Code" directamente
2. ✅ Editar código libremente
3. ✅ Usar snippets (html → Tab)
4. ✅ Guardar cambios automáticos
5. ✅ Volver a Visual para ver resultado

---

**Este es el diseño CORRECTO y mantiene la arquitectura limpia de Calcpad.**
