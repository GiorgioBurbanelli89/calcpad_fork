# Guía de Prueba Paso a Paso - Mejoras de Calcpad

**Fecha**: 2026-01-21
**Archivo abierto**: test_folding.cpd

---

## ✅ Checklist de Pruebas

### 1️⃣ Probar Code Folding en AvalonEdit

**Pasos**:
1. ✓ Calcpad está abierto con test_folding.cpd
2. **IMPORTANTE**: Presiona el botón **"Code"** en la barra superior (si no estás ya en modo Code)
3. Mira el **margen izquierdo** del editor
4. Deberías ver triángulos **▼** (apuntando hacia abajo) al lado de cada bloque

**Bloques a verificar**:
- [ ] Bloque `@{html}` - línea 11
- [ ] Bloque `@{css}` - línea 24
- [ ] Bloque `@{ts}` - línea 36
- [ ] Bloque `@{c}` - línea 46
- [ ] Bloque `@{fortran}` - línea 56
- [ ] Bloque `#if...#end if` - línea 64
- [ ] Bloque `#def...#end def` - línea 70
- [ ] Bloque `$svg...$end` - línea 79

**Acciones**:
- [ ] Hacer click en **▼** para colapsar un bloque
- [ ] El triángulo cambia a **▶** (apuntando a la derecha)
- [ ] El código del bloque desaparece (queda solo la línea de inicio)
- [ ] Hacer click en **▶** para expandir nuevamente
- [ ] El código reaparece

**✅ RESULTADO ESPERADO**: Los triángulos funcionan correctamente y colapsan/expanden los bloques.

---

### 2️⃣ Probar Snippets HTML/CSS/TS en AvalonEdit

**Pasos**:
1. Asegúrate de estar en modo **"Code"** (AvalonEdit)
2. Posiciona el cursor **dentro** del bloque `@{html}` (línea 13, después de `<html>`)
3. Escribe: `div`
4. Espera 1 segundo (aparecerá popup de autocomplete)

**Verificar popup**:
- [ ] Aparece popup con opciones de snippets
- [ ] Se ve "div" en la lista
- [ ] Se ve preview del código: `<div></div>`
- [ ] Presiona **Tab** o **Enter** para insertar

**Resultado esperado**:
```html
<div></div>
```
El cursor queda entre las etiquetas: `<div>|</div>`

**Otros snippets a probar**:
- [ ] En `@{html}`: escribir `html` → debe insertar HTML5 boilerplate completo
- [ ] En `@{css}`: escribir `flex` → debe insertar reglas flexbox
- [ ] En `@{ts}`: escribir `function` → debe insertar declaración de función

**✅ RESULTADO ESPERADO**: Los snippets se insertan correctamente con preview.

---

### 3️⃣ Probar MathEditor con Bloques Externos

**Pasos**:
1. Presiona el botón **"Visual"** en la barra superior (cambiar a MathEditor)
2. Espera a que se renderice el contenido

**Verificar bloques externos**:
- [ ] El bloque `@{html}` NO se muestra como `@{html}...@{end html}`
- [ ] El bloque HTML se muestra como: **`| HTML [+]`** con barra de color **naranja**
- [ ] El bloque CSS se muestra como: **`| CSS [+]`** con barra de color **azul**
- [ ] El bloque TS se muestra como: **`| TS [+]`** con barra de color **azul**
- [ ] El bloque C se muestra como: **`| C [+]`** con barra de color **gris**
- [ ] El bloque Fortran se muestra como: **`| FORTRAN [+]`** con barra de color **morado**

**Colores esperados**:
| Bloque | Color de barra |
|--------|----------------|
| HTML | Naranja (#E34C26) |
| CSS | Azul (#264DE4) |
| TS | Azul (#007ACC) |
| C | Gris (#555555) |
| Fortran | Morado (#734F96) |

**Acciones**:
- [ ] Hacer click en **`| HTML [+]`**
- [ ] El bloque se expande y muestra: **`| HTML [-]`** con el código HTML visible abajo
- [ ] El código se muestra en fuente Consolas, color negro
- [ ] Hacer click nuevamente para colapsar
- [ ] Vuelve a **`| HTML [+]`**

**✅ RESULTADO ESPERADO**: Los bloques externos se muestran como elementos colapsables con colores correctos.

---

### 4️⃣ Probar Preview con AvalonEdit

**Pasos**:
1. Asegúrate de estar en modo **"Visual"** (MathEditor)
2. Mira la **barra superior** (justo debajo de los botones)
3. Deberías ver: **"Calcpad:"** seguido de un editor pequeño

**Verificar preview**:
- [ ] El preview muestra código con **syntax highlighting** (colores)
- [ ] El preview está en fuente **Consolas** (monoespaciada)
- [ ] El preview muestra un cursor visual con **`|`** (pipe)
- [ ] Al moverte con las flechas en el editor principal, el preview se actualiza

**Probar navegación**:
- [ ] Presiona **Flecha Abajo** para bajar líneas
- [ ] El preview cambia para mostrar la nueva línea actual
- [ ] Los comentarios (`'`) aparecen en **verde**
- [ ] Los strings (`"`) aparecen en **rojo/naranja**
- [ ] Los números aparecen en color diferente al texto

**✅ RESULTADO ESPERADO**: El preview muestra la línea actual con colores de syntax highlighting.

---

### 5️⃣ Probar Toggle entre Code y Visual

**Pasos**:
1. Presiona botón **"Code"** → Modo AvalonEdit
   - [ ] Se ve el código fuente completo en texto plano
   - [ ] Hay triángulos ▼ en el margen izquierdo
   - [ ] El preview superior desaparece (no es necesario en modo Code)

2. Presiona botón **"Visual"** → Modo MathEditor
   - [ ] Los bloques externos se renderizan como **`| LANGUAGE [+]`**
   - [ ] El preview superior reaparece con syntax highlighting
   - [ ] Los números de línea están visibles

**✅ RESULTADO ESPERADO**: Ambos modos funcionan correctamente.

---

## 🐛 Problemas Conocidos y Soluciones

### ❌ Problema: No veo triángulos ▼ en AvalonEdit
**Solución**:
1. Verifica que estés en modo **"Code"** (no "Visual")
2. El archivo debe tener bloques de código (`@{html}`, `#if`, etc.)
3. Los triángulos aparecen SOLO en el margen izquierdo

### ❌ Problema: Los bloques en MathEditor siguen mostrándose como `@{html}`
**Solución**:
1. Cierra Calcpad completamente
2. Vuelve a abrir el archivo
3. Asegúrate de estar en modo **"Visual"**

### ❌ Problema: Los snippets no aparecen
**Solución**:
1. Asegúrate de estar en modo **"Code"** (AvalonEdit)
2. El cursor debe estar **DENTRO** de un bloque externo (`@{html}`, `@{css}`, `@{ts}`)
3. Espera 1 segundo después de escribir para que aparezca el popup

### ❌ Problema: El preview superior no tiene colores
**Solución**:
1. Verifica que existe el archivo `Calcpad.xshd` en la carpeta de Calcpad.exe
2. Si no existe, el preview funcionará pero sin colores (solo texto plano)

---

## 📊 Tabla de Verificación Final

| Funcionalidad | Estado | Notas |
|--------------|--------|-------|
| Code Folding (▼) en AvalonEdit | ⬜ | Triángulos visibles y funcionales |
| Snippets HTML/CSS/TS | ⬜ | Popup con preview correcto |
| MathEditor: `\| HTML [+]` | ⬜ | Bloques externos colapsables |
| Colores por lenguaje | ⬜ | HTML=naranja, CSS=azul, etc. |
| Click para toggle | ⬜ | Colapsar/expandir funciona |
| Preview con AvalonEdit | ⬜ | Syntax highlighting visible |
| Toggle Code/Visual | ⬜ | Ambos modos funcionan |

---

## ✅ Cuando Todo Funcione

**Marca esta casilla cuando hayas verificado todo**:
- [ ] ✅ Todas las funcionalidades probadas y funcionando

**Entonces ejecuta**:
```bash
cd "C:\Users\j-b-j\Documents\Calcpad-7.5.7"
.\git-commit-mejoras.ps1
```

Esto creará el commit de git con todos los cambios.

---

## 📝 Reportar Problemas

Si encuentras algún problema, anótalo aquí:

**Problema 1**:
- Descripción: _____________________
- Pasos para reproducir: _____________________
- Screenshot: _____________________

**Problema 2**:
- Descripción: _____________________
- Pasos para reproducir: _____________________
- Screenshot: _____________________

---

**¡Buena suerte con las pruebas!** 🚀
