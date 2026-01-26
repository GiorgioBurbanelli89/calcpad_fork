# 🎯 Three.js DESDE CERO - Ejemplos Ultra Básicos

## ¿Qué es Three.js?

Three.js es una biblioteca que permite crear objetos 3D en el navegador.

Imagina que tienes:
- 📦 Objetos 3D (cubos, esferas, etc.)
- 📷 Una cámara (tu punto de vista)
- 🎬 Una escena (donde pones los objetos)
- 🖼️ Un renderizador (dibuja todo en pantalla)

## 🎓 Ruta de Aprendizaje

**Empieza en ORDEN:**

1. **01-minimo.cpd** (5 líneas) - Lo más básico: un cubo negro
2. **02-con-color.cpd** (6 líneas) - Agregar color al cubo
3. **03-con-luz.cpd** (8 líneas) - Agregar luz para ver mejor
4. **04-rotando.cpd** (10 líneas) - Hacer que el cubo rote
5. **05-varios-objetos.cpd** (15 líneas) - Agregar más objetos
6. **06-mover-camara.cpd** (12 líneas) - Mover la cámara con el mouse
7. **07-cambiar-tamaño.cpd** (8 líneas) - Controlar el tamaño del cubo
8. **08-varias-formas.cpd** (20 líneas) - Esfera, cilindro, cono

---

## 💡 Los 4 Pasos Básicos

TODOS los ejemplos de Three.js siguen estos 4 pasos:

```javascript
// 1. CREAR LA ESCENA (donde van los objetos)
const scene = new THREE.Scene();

// 2. CREAR LA CÁMARA (tu punto de vista)
const camera = new THREE.PerspectiveCamera(...);

// 3. CREAR EL RENDERIZADOR (dibuja en pantalla)
const renderer = new THREE.WebGLRenderer();

// 4. AGREGAR OBJETOS
// ... aquí agregas cubos, esferas, etc.

// 5. RENDERIZAR (dibujar)
renderer.render(scene, camera);
```

---

## 📖 Conceptos Clave

### Scene (Escena)
Es como una habitación vacía donde pones objetos.

```javascript
const scene = new THREE.Scene();
```

### Camera (Cámara)
Es tu "ojo" que mira la escena.

```javascript
const camera = new THREE.PerspectiveCamera(75, 600/400, 0.1, 1000);
//                                          ↑    ↑       ↑    ↑
//                                        FOV  aspecto cerca lejos
```

- **FOV** (Field of View): Ángulo de visión (75° es estándar)
- **Aspecto**: Ancho/Alto (600/400 = 1.5)
- **Cerca/Lejos**: Rango de visión (objetos muy cerca o lejos no se ven)

### Renderer (Renderizador)
Dibuja todo en un `<canvas>`.

```javascript
const renderer = new THREE.WebGLRenderer();
renderer.setSize(600, 400);  // Tamaño en píxeles
```

### Mesh (Malla/Objeto)
Un objeto 3D = Geometría + Material

```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1);  // Forma (cubo)
const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });  // Color (rojo)
const cube = new THREE.Mesh(geometry, material);  // Juntar forma + color
```

---

## 🎨 Colores en Three.js

Tres formas de escribir colores:

```javascript
// Hexadecimal (0x + código de color)
color: 0xff0000  // Rojo
color: 0x00ff00  // Verde
color: 0x0000ff  // Azul
color: 0xffff00  // Amarillo
color: 0xff00ff  // Magenta

// String
color: 'red'
color: 'blue'
color: '#ff0000'

// CSS
color: 'rgb(255, 0, 0)'
```

---

## 📦 Formas Básicas (Geometrías)

```javascript
// Cubo
new THREE.BoxGeometry(ancho, alto, profundidad)

// Esfera
new THREE.SphereGeometry(radio, segmentos, segmentos)

// Cilindro
new THREE.CylinderGeometry(radioTop, radioBottom, altura, segmentos)

// Cono
new THREE.ConeGeometry(radio, altura, segmentos)

// Plano
new THREE.PlaneGeometry(ancho, alto)
```

---

## 🎨 Materiales Básicos

```javascript
// Material Básico (NO necesita luz)
new THREE.MeshBasicMaterial({ color: 0xff0000 })

// Material Standard (SÍ necesita luz)
new THREE.MeshStandardMaterial({ color: 0xff0000 })

// Material con Wireframe (solo bordes)
new THREE.MeshBasicMaterial({ color: 0xff0000, wireframe: true })
```

---

## 💡 Posición de Objetos

Todo objeto tiene posición en 3D: `x, y, z`

```javascript
cube.position.x = 2;   // Mover a la derecha
cube.position.y = 1;   // Mover arriba
cube.position.z = -3;  // Mover atrás (alejándose)

// O todo junto:
cube.position.set(2, 1, -3);
```

**Sistema de coordenadas:**
- `X`: Derecha (+) / Izquierda (-)
- `Y`: Arriba (+) / Abajo (-)
- `Z`: Hacia ti (+) / Alejándose (-)

---

## 🔄 Rotación de Objetos

Todo objeto puede rotar en 3 ejes:

```javascript
cube.rotation.x = 0.5;  // Rotar en X (voltear adelante/atrás)
cube.rotation.y = 0.5;  // Rotar en Y (girar izquierda/derecha)
cube.rotation.z = 0.5;  // Rotar en Z (inclinar)
```

**Nota:** Los ángulos están en **radianes**, no grados.
- 360° = 2π radianes = `Math.PI * 2`
- 180° = π radianes = `Math.PI`
- 90° = π/2 radianes = `Math.PI / 2`

---

## 📏 Escala de Objetos

Hacer objetos más grandes o pequeños:

```javascript
cube.scale.x = 2;   // Doble de ancho
cube.scale.y = 0.5; // Mitad de alto
cube.scale.z = 1;   // Profundidad normal

// O todo junto (mismo valor en X, Y, Z):
cube.scale.set(2, 2, 2);  // Doble de tamaño
```

---

## 🎬 Animación Básica

Para hacer que algo se mueva:

```javascript
function animate() {
  requestAnimationFrame(animate);  // Llamar otra vez (60 FPS)

  cube.rotation.y += 0.01;  // Incrementar rotación

  renderer.render(scene, camera);  // Dibujar
}

animate();  // Iniciar
```

---

## 💡 Consejos Importantes

1. **Orden importa:**
   - Primero crear scene, camera, renderer
   - Luego crear objetos
   - Luego agregar a la escena con `scene.add()`
   - Por último renderizar

2. **Siempre agrega a la escena:**
   ```javascript
   scene.add(cube);  // ← Sin esto, el cubo no se verá
   ```

3. **La cámara debe estar alejada:**
   ```javascript
   camera.position.z = 5;  // Alejar la cámara
   ```
   Si está en `0, 0, 0` (igual que el cubo), no verás nada.

4. **Para ver console.log:**
   - Presiona **F12** en Calcpad
   - Ve a la pestaña **Console**

---

## 🚀 ¿Listo?

Abre el archivo **01-minimo.cpd** y ve línea por línea.

**IMPORTANTE:** Lee los comentarios en CADA línea de código. Explican exactamente qué hace cada parte.

---

*Creado para aprender Three.js desde CERO* 🎯
