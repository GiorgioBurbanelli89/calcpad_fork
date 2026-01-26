# HTML desde Cero - Para Ingenieros

## ¿Qué es HTML?

**HTML** = HyperText Markup Language (Lenguaje de Marcado de Hipertexto)

Es como un **plano de construcción** para páginas web. Define la **estructura** de lo que ves en el navegador.

### Analogía de Ingeniería:
- **HTML** = Plano estructural (columnas, vigas, muros)
- **CSS** = Acabados (pintura, texturas, colores)
- **JavaScript** = Sistemas activos (ascensores, puertas automáticas)

---

## Estructura Básica de HTML

### 1. ETIQUETAS (Tags)

Todo en HTML se escribe con **etiquetas** que van entre `< >`:

```html
<etiqueta>contenido</etiqueta>
```

- `<etiqueta>` = Etiqueta de **apertura**
- `</etiqueta>` = Etiqueta de **cierre** (con `/`)
- `contenido` = Lo que va dentro

**Ejemplo:**
```html
<p>Este es un párrafo</p>
```

### 2. ETIQUETAS COMUNES

| Etiqueta | Qué hace | Ejemplo |
|----------|----------|---------|
| `<h1>` hasta `<h6>` | Títulos (1=más grande, 6=más pequeño) | `<h1>Título Principal</h1>` |
| `<p>` | Párrafo de texto | `<p>Este es un texto</p>` |
| `<div>` | Contenedor (caja) | `<div>Aquí va contenido</div>` |
| `<span>` | Contenedor en línea | `<span>texto</span>` |
| `<br>` | Salto de línea | `Línea 1<br>Línea 2` |
| `<strong>` | Texto en **negrita** | `<strong>Importante</strong>` |
| `<em>` | Texto en *cursiva* | `<em>Énfasis</em>` |

**Ejemplo completo:**
```html
<div>
  <h1>Análisis de Viga</h1>
  <p>La viga tiene una <strong>longitud</strong> de 6 metros.</p>
  <p>El momento máximo es <em>importante</em> para el diseño.</p>
</div>
```

---

## 3. ATRIBUTOS

Las etiquetas pueden tener **propiedades** llamadas atributos:

```html
<etiqueta atributo="valor">contenido</etiqueta>
```

### Atributos Comunes:

#### `id` - Identificador único
```html
<div id="resultados">Aquí van los resultados</div>
```
Piensa en `id` como el **número de un edificio**. Debe ser único.

#### `class` - Clase (puede repetirse)
```html
<p class="importante">Este texto es importante</p>
<p class="importante">Este también</p>
```
Piensa en `class` como el **tipo de material** (varios elementos pueden ser del mismo tipo).

#### `style` - Estilos en línea
```html
<p style="color:red;">Texto rojo</p>
<p style="font-size:20px;">Texto grande</p>
```

---

## 4. CSS - Dando Estilo

**CSS** = Cascading Style Sheets (Hojas de Estilo en Cascada)

Define **cómo se ve** el HTML (colores, tamaños, posiciones).

### Sintaxis Básica:
```css
selector {
  propiedad: valor;
  otra-propiedad: otro-valor;
}
```

### Ejemplo:
```html
<style>
  /* Esto es un comentario en CSS */
  .importante {
    color: red;           /* Color del texto */
    font-size: 20px;      /* Tamaño de fuente */
    font-weight: bold;    /* Negrita */
    background: yellow;   /* Fondo amarillo */
    padding: 10px;        /* Espacio interno */
    margin: 5px;          /* Espacio externo */
    border: 2px solid blue; /* Borde */
  }
</style>

<p class="importante">Este texto tiene estilo</p>
```

### Propiedades CSS Comunes:

| Propiedad | Qué hace | Ejemplo |
|-----------|----------|---------|
| `color` | Color del texto | `color: red;` o `color: #ff0000;` |
| `background` | Color de fondo | `background: blue;` |
| `font-size` | Tamaño de texto | `font-size: 16px;` |
| `width` | Ancho | `width: 200px;` |
| `height` | Alto | `height: 100px;` |
| `padding` | Espacio interno | `padding: 10px;` |
| `margin` | Espacio externo | `margin: 20px;` |
| `border` | Borde | `border: 1px solid black;` |
| `display` | Tipo de visualización | `display: block;` o `display: none;` |

---

## 5. JavaScript - Haciendo que Funcione

**JavaScript** hace que las páginas sean **interactivas** y **dinámicas**.

### Variables:
```javascript
// Esto es un comentario en JavaScript
const longitud = 6;      // Constante (no cambia)
let ancho = 3;           // Variable (puede cambiar)
var altura = 2;          // Variable (vieja forma)
```

### Tipos de Datos:
```javascript
const numero = 42;                    // Número
const texto = "Hola";                 // Texto (string)
const verdadero = true;               // Booleano (true/false)
const lista = [1, 2, 3];             // Array (lista)
const objeto = { x: 10, y: 20 };     // Objeto
```

### Operaciones:
```javascript
const suma = 5 + 3;        // 8
const resta = 10 - 4;      // 6
const multiplicacion = 6 * 7; // 42
const division = 20 / 4;   // 5
const potencia = 2 ** 3;   // 8 (2^3)
```

### Funciones:
```javascript
// Definir una función
function calcularArea(base, altura) {
  const area = base * altura;
  return area;
}

// Usar la función
const resultado = calcularArea(5, 3); // 15
```

### Funciones Flecha (modernas):
```javascript
const calcularArea = (base, altura) => {
  return base * altura;
};

// Forma corta (una sola línea)
const calcularArea = (base, altura) => base * altura;
```

---

## 6. Interactuar con el HTML desde JavaScript

### Obtener elementos:
```javascript
// Por ID
const elemento = document.getElementById('miDiv');

// Por clase
const elementos = document.getElementsByClassName('importante');

// Selector CSS (el más usado)
const elemento = document.querySelector('#miDiv');
const elementos = document.querySelectorAll('.importante');
```

### Modificar contenido:
```javascript
// Cambiar texto
elemento.textContent = 'Nuevo texto';
elemento.innerHTML = '<strong>Texto con HTML</strong>';

// Cambiar estilos
elemento.style.color = 'red';
elemento.style.fontSize = '20px';

// Agregar/quitar clases
elemento.classList.add('activo');
elemento.classList.remove('inactivo');
```

### Eventos (Interactividad):
```javascript
// Cuando se hace click
elemento.addEventListener('click', function() {
  alert('¡Me hiciste click!');
});

// Cuando cambia un input
input.addEventListener('input', function(evento) {
  console.log('Nuevo valor:', evento.target.value);
});
```

---

## 7. Estructura del Bloque @{html} en Calcpad

Cuando usas `@{html}` en Calcpad, puedes escribir HTML, CSS y JavaScript:

```calcpad
@{html}
<!-- Aquí va tu código HTML/CSS/JavaScript -->
<style>
  /* CSS aquí */
  .contenedor {
    background: lightblue;
    padding: 20px;
  }
</style>

<div class="contenedor">
  <h2>Título</h2>
  <p id="resultado">Resultado: 0</p>
  <button id="miBoton">Calcular</button>
</div>

<script>
  // JavaScript aquí
  document.getElementById('miBoton').addEventListener('click', () => {
    const valor = 5 + 3;
    document.getElementById('resultado').textContent = 'Resultado: ' + valor;
  });
</script>
@{end html}
```

---

## 8. Ejemplo Completo Paso a Paso

```html
<!-- 1. ESTRUCTURA HTML -->
<div id="calculadora">
  <h2>Calculadora de Área</h2>

  <label>Base:</label>
  <input type="number" id="base" value="5">

  <label>Altura:</label>
  <input type="number" id="altura" value="3">

  <button id="calcular">Calcular</button>

  <p id="resultado">Área: 0 m²</p>
</div>

<!-- 2. ESTILOS CSS -->
<style>
  #calculadora {
    background: #f0f0f0;
    padding: 20px;
    border-radius: 10px;
    width: 300px;
    margin: 20px auto;
  }

  input {
    width: 100%;
    padding: 8px;
    margin: 5px 0 15px 0;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  button {
    background: #4caf50;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    width: 100%;
  }

  button:hover {
    background: #45a049;
  }

  #resultado {
    margin-top: 20px;
    font-size: 20px;
    font-weight: bold;
    color: #333;
  }
</style>

<!-- 3. LÓGICA JAVASCRIPT -->
<script>
  // Obtener referencias a los elementos
  const inputBase = document.getElementById('base');
  const inputAltura = document.getElementById('altura');
  const boton = document.getElementById('calcular');
  const resultado = document.getElementById('resultado');

  // Función para calcular
  function calcular() {
    // Obtener valores (convertir texto a número)
    const base = parseFloat(inputBase.value);
    const altura = parseFloat(inputAltura.value);

    // Calcular área
    const area = base * altura;

    // Mostrar resultado
    resultado.textContent = 'Área: ' + area + ' m²';
  }

  // Cuando se hace click en el botón
  boton.addEventListener('click', calcular);

  // Calcular automáticamente cuando cambian los inputs
  inputBase.addEventListener('input', calcular);
  inputAltura.addEventListener('input', calcular);

  // Calcular al cargar
  calcular();
</script>
```

---

## 9. Elementos HTML para Inputs

### Input de Texto:
```html
<input type="text" id="nombre" placeholder="Tu nombre">
```

### Input Numérico:
```html
<input type="number" id="edad" min="0" max="100" value="25">
```

### Checkbox:
```html
<input type="checkbox" id="acepto">
<label for="acepto">Acepto los términos</label>
```

### Radio Buttons:
```html
<input type="radio" name="opcion" value="A" id="opcionA">
<label for="opcionA">Opción A</label>

<input type="radio" name="opcion" value="B" id="opcionB">
<label for="opcionB">Opción B</label>
```

### Select (Dropdown):
```html
<select id="material">
  <option value="acero">Acero</option>
  <option value="concreto">Concreto</option>
  <option value="madera">Madera</option>
</select>
```

### Slider (Rango):
```html
<input type="range" id="carga" min="0" max="100" value="50">
<span id="valorCarga">50</span>

<script>
  const slider = document.getElementById('carga');
  const valor = document.getElementById('valorCarga');

  slider.addEventListener('input', () => {
    valor.textContent = slider.value;
  });
</script>
```

### Botones:
```html
<button onclick="miFuncion()">Click aquí</button>
```

---

## 10. Debugging (Encontrar Errores)

### Console.log - Tu mejor amigo:
```javascript
const x = 5;
console.log('El valor de x es:', x);

const objeto = { nombre: 'Juan', edad: 30 };
console.log('Objeto completo:', objeto);
```

### Ver la consola:
1. Presiona **F12** en el navegador
2. Ve a la pestaña **"Console"**
3. Verás todos los `console.log()` y errores

### Errores comunes:
```javascript
// ❌ ERROR: Olvidar comillas
const texto = Hola;  // Error!

// ✅ CORRECTO:
const texto = "Hola";

// ❌ ERROR: Olvidar punto y coma (no siempre necesario, pero recomendado)
const x = 5
const y = 3

// ✅ CORRECTO:
const x = 5;
const y = 3;

// ❌ ERROR: Variable no definida
console.log(variableQueNoExiste);  // Error!

// ✅ CORRECTO: Definir primero
const miVariable = 10;
console.log(miVariable);
```

---

## 11. Plantilla Base para Calcpad

```calcpad
"Título de tu análisis
'Parámetros:'
parametro1 = 5
parametro2 = 3

@{html}
<style>
  /* Estilos aquí */
  .contenedor {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
  }
</style>

<div class="contenedor">
  <!-- HTML aquí -->
  <h3>Resultado del Análisis</h3>
  <p id="output">Calculando...</p>
</div>

<script>
  // JavaScript aquí

  // 1. Obtener valores de Calcpad
  const param1 = @{calcpad:parametro1};
  const param2 = @{calcpad:parametro2};

  // 2. Hacer cálculos
  const resultado = param1 * param2;

  // 3. Mostrar resultado
  document.getElementById('output').textContent = 'Resultado: ' + resultado;
</script>
@{end html}
```

---

## 12. Tips de Productividad

### Comentarios:
```html
<!-- Comentario en HTML -->

<style>
  /* Comentario en CSS */
</style>

<script>
  // Comentario de una línea en JavaScript

  /*
    Comentario de
    múltiples líneas
  */
</script>
```

### Inspeccionar elementos:
1. Click derecho en cualquier parte de la página
2. "Inspeccionar elemento"
3. Verás el HTML y CSS en tiempo real

### Shortcuts útiles:
- `Ctrl + /` - Comentar/descomentar línea
- `F12` - Abrir DevTools
- `Ctrl + Shift + C` - Inspeccionar elemento

---

## 13. Recursos para Aprender Más

### Documentación:
- **MDN Web Docs**: https://developer.mozilla.org/es/
  - La mejor documentación de HTML/CSS/JS
  - En español

### Tutoriales interactivos:
- **freeCodeCamp**: https://www.freecodecamp.org/
- **W3Schools**: https://www.w3schools.com/

### Para practicar:
- **CodePen**: https://codepen.io/
  - Escribe HTML/CSS/JS y ve el resultado en tiempo real

---

## 14. Próximos Pasos

Ahora que sabes lo básico, puedes:
1. ✅ Entender el código de los ejemplos de Three.js
2. ✅ Modificar los ejemplos existentes
3. ✅ Crear tus propias visualizaciones
4. ✅ Agregar interactividad a tus análisis

**¡Manos a la obra!** 🚀
