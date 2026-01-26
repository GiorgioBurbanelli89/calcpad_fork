# ❓ ¿Por qué los ejemplos no empiezan con `<html>`?

## 🎯 Respuesta Corta:

**Porque estás usando `@{html}` en Calcpad, no un archivo HTML standalone.**

Calcpad genera la estructura HTML completa automáticamente. Tú solo pones el contenido.

---

## 📊 Comparación Visual:

### ❌ Lo que NO NECESITAS en Calcpad:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Título</title>
</head>
<body>
  <!-- Aquí va tu código -->
</body>
</html>
```

**Calcpad ya genera todo esto por ti.**

---

### ✅ Lo que SÍ necesitas en Calcpad:

```calcpad
"Título de tu análisis

'Parámetros'
x = 10

@{html}
<div id="canvas"></div>
<script>
  // Tu código aquí
</script>
@{end html}
```

**Solo el contenido que va dentro de `<body>`.**

---

## 🔍 ¿Qué hace Calcpad con `@{html}`?

Cuando escribes:

```calcpad
@{html}
<div>Hola</div>
@{end html}
```

Calcpad lo convierte en:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Created with Calcpad</title>
  <style>
    /* Estilos de Calcpad */
  </style>
</head>
<body>
  <h1>Título de tu análisis</h1>
  <p>Parámetros:</p>
  <p>x = 10</p>

  <!-- Aquí se inserta tu bloque @{html} -->
  <div>Hola</div>

</body>
</html>
```

---

## 🆚 Dos Formas de Usar HTML:

### 📄 **1. Archivo HTML Standalone** (para navegador directo)

**Archivo:** `ejemplo.html`

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Mi Ejemplo</title>
</head>
<body>
  <div id="canvas"></div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script>
    const scene = new THREE.Scene();
    // ... resto del código
  </script>
</body>
</html>
```

**Uso:** Doble click en el archivo → Se abre en el navegador

**Ventaja:** Funciona solo, no necesita Calcpad

**Desventaja:** No puedes usar variables de Calcpad (`@{calcpad:x}`)

---

### 📐 **2. HTML en Calcpad** (para integración)

**Archivo:** `ejemplo.cpd`

```calcpad
"Mi Análisis

'Parámetros'
ancho = 5
alto = 3

@{html}
<div id="canvas"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
  const scene = new THREE.Scene();

  // Usar variables de Calcpad
  const w = @{calcpad:ancho};
  const h = @{calcpad:alto};

  const geometry = new THREE.BoxGeometry(w, h, 1);
  // ... resto del código
</script>
@{end html}
```

**Uso:** Abrir en Calcpad → Calcular (F5)

**Ventaja:** Integra cálculos con visualización

**Desventaja:** Necesita Calcpad para funcionar

---

## 🧪 Prueba Práctica:

### Opción A: Usar en Calcpad (recomendado)

1. Abre Calcpad WPF
2. Abre `Examples\three\basico\01-minimo.cpd`
3. Presiona F5
4. ✅ Funciona

### Opción B: Usar HTML standalone

1. Abre `Examples\three\basico\01-minimo-standalone.html`
2. Doble click (se abre en el navegador)
3. ✅ Funciona

---

## 🎓 Estructura HTML Completa (Referencia):

### Documento HTML mínimo:

```html
<!DOCTYPE html>           ← Declara HTML5
<html lang="es">          ← Idioma
<head>                    ← Metadatos (no visible)
  <meta charset="UTF-8">  ← Codificación de caracteres
  <title>Título</title>   ← Título de la pestaña
  <style>                 ← Estilos CSS (opcional)
    /* CSS aquí */
  </style>
</head>
<body>                    ← Contenido visible
  <h1>Hola Mundo</h1>

  <script>                ← JavaScript (opcional)
    // JS aquí
  </script>
</body>
</html>
```

### Partes principales:

| Etiqueta | Qué es | Visible |
|----------|--------|---------|
| `<!DOCTYPE html>` | Declara que es HTML5 | No |
| `<html>` | Raíz del documento | No |
| `<head>` | Metadatos (título, charset, CSS) | No |
| `<title>` | Título de la pestaña del navegador | Sí (en pestaña) |
| `<meta charset>` | Codificación (UTF-8 para caracteres especiales) | No |
| `<style>` | Estilos CSS | No (afecta visualmente) |
| `<body>` | Contenido visible de la página | Sí |
| `<script>` | Código JavaScript | No (ejecuta código) |

---

## 💡 Regla Simple:

### ¿Estás usando Calcpad?
→ **NO necesitas** `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`

Solo usa:
```calcpad
@{html}
  <!-- Tu contenido aquí -->
@{end html}
```

### ¿Quieres un archivo HTML independiente?
→ **SÍ necesitas** la estructura completa

Usa la plantilla de `01-minimo-standalone.html`

---

## 📝 Resumen en 3 puntos:

1. **En Calcpad:** Solo pones el contenido dentro de `@{html}...@{end html}`

2. **HTML Standalone:** Necesitas toda la estructura (`<!DOCTYPE>`, `<html>`, etc.)

3. **Los ejemplos actuales:** Están diseñados para Calcpad, por eso no tienen la estructura completa

---

## ✅ Archivos para Comparar:

| Archivo | Tipo | Para qué |
|---------|------|----------|
| `01-minimo.cpd` | Calcpad | Usar en Calcpad WPF |
| `01-minimo-standalone.html` | HTML | Abrir directo en navegador |

Ambos muestran lo mismo, pero con estructuras diferentes.

---

**¿Tienes más dudas?** Presiona F12 en ambos archivos y compara el HTML generado.
