# Three.js en Calcpad - Guía desde Cero

## ¿Qué es Three.js?

**Three.js** es una biblioteca JavaScript que permite crear gráficos 3D en el navegador usando WebGL. Es perfecta para:
- Visualizar modelos 3D
- Análisis estructural (FEA)
- Animaciones interactivas
- Geometrías paramétricas

## Conceptos Fundamentales

### 1. Los 3 Elementos Básicos (Siempre necesarios)

```javascript
// 1. ESCENA - El contenedor de todo
const scene = new THREE.Scene();

// 2. CÁMARA - Define qué y cómo vemos
const camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000);

// 3. RENDERER - Dibuja la escena en el canvas
const renderer = new THREE.WebGLRenderer();
```

### 2. Geometría + Material = Mesh

```javascript
// Geometría: La forma del objeto
const geometry = new THREE.BoxGeometry(1, 1, 1);

// Material: El aspecto (color, textura, etc.)
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });

// Mesh: La combinación de ambos
const cube = new THREE.Mesh(geometry, material);

// Agregar a la escena
scene.add(cube);
```

### 3. Loop de Animación

```javascript
function animate() {
  requestAnimationFrame(animate);  // Llamar de nuevo en el siguiente frame

  cube.rotation.x += 0.01;  // Modificar objetos
  cube.rotation.y += 0.01;

  renderer.render(scene, camera);  // Renderizar
}
animate();  // Iniciar el loop
```

## Jerarquía de Aprendizaje

### Nivel 1: Básico (Ejemplos 01-02)
- ✅ Crear escena, cámara y renderer
- ✅ Agregar un objeto simple
- ✅ Animar rotación
- ✅ Usar variables de Calcpad con `@{calcpad:variable}`

### Nivel 2: Intermedio (Ejemplos 03-05)
- ✅ Múltiples objetos 3D
- ✅ OrbitControls (navegación con mouse)
- ✅ Iluminación (luces direccionales, ambientales)
- ✅ Sombras
- ✅ Materiales avanzados (MeshStandardMaterial)

### Nivel 3: Estructuras (Ejemplos 06-07)
- ✅ Vigas y elementos estructurales
- ✅ Visualización de cargas (flechas)
- ✅ Etiquetas de texto (Sprites)
- ✅ Geometrías custom

### Nivel 4: Mallas FEA (Ejemplos 08-10)
- ✅ Mallas de elementos finitos
- ✅ Colores por valores (tensiones, desplazamientos)
- ✅ Animación de deformaciones
- ✅ Escalas de colores
- ✅ Contornos y mapas de calor

## Geometrías Comunes en Three.js

| Geometría | Uso | Parámetros |
|-----------|-----|------------|
| `BoxGeometry` | Vigas, columnas, cubos | (ancho, alto, prof) |
| `SphereGeometry` | Esferas, nodos | (radio, segmentos) |
| `CylinderGeometry` | Pilares, barras | (radioTop, radioBot, altura) |
| `PlaneGeometry` | Losas, muros | (ancho, alto) |
| `BufferGeometry` | Mallas custom FEA | (vertices, caras) |

## Materiales Comunes

| Material | Características | Uso |
|----------|----------------|-----|
| `MeshBasicMaterial` | Sin iluminación | Wireframes, debugging |
| `MeshLambertMaterial` | Iluminación simple | Rápido |
| `MeshPhongMaterial` | Iluminación con brillo | General |
| `MeshStandardMaterial` | Físicamente realista | Mejor calidad |
| `LineBasicMaterial` | Para líneas | Wireframes, ejes |

## Tipos de Luces

```javascript
// Luz ambiental - Ilumina todo por igual
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);

// Luz direccional - Como el sol
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(5, 10, 5);

// Luz puntual - Como una bombilla
const pointLight = new THREE.PointLight(0xffffff, 1, 100);

// Luz focal - Como un reflector
const spotLight = new THREE.SpotLight(0xffffff);
```

## Sistema de Coordenadas

```
      Y (arriba)
      |
      |
      |_______X (derecha)
     /
    /
   Z (hacia ti)
```

- **Posición**: `object.position.set(x, y, z)`
- **Rotación**: `object.rotation.x/y/z` (en radianes)
- **Escala**: `object.scale.set(x, y, z)`

## Integración con Calcpad

### Sintaxis básica:

```calcpad
"Parámetros:
longitud = 5m
ancho = 2m

@{html}
<script src="https://cdn.jsdelivr.net/npm/three@0.145/build/three.min.js"></script>
<script>
  // Interpolar valores de Calcpad
  const L = @{calcpad:longitud};  // → 5
  const W = @{calcpad:ancho};     // → 2

  // Tu código Three.js aquí
</script>
@{end html}
```

### Variables disponibles:
- ✅ Números: `@{calcpad:variable}`
- ✅ Expresiones: `@{calcpad:a + b}`
- ✅ Funciones: `@{calcpad:sqrt(x)}`

## Recursos Útiles

### Documentación oficial:
- 📚 [Three.js Docs](https://threejs.org/docs/)
- 📖 [Three.js Examples](https://threejs.org/examples/)
- 🎓 [Three.js Journey](https://threejs-journey.com/) (curso recomendado)

### CDN Links (para usar en Calcpad):
```html
<!-- Three.js core -->
<script src="https://cdn.jsdelivr.net/npm/three@0.145/build/three.min.js"></script>

<!-- OrbitControls -->
<script src="https://cdn.jsdelivr.net/npm/three@0.145/examples/js/controls/OrbitControls.js"></script>

<!-- Stats (FPS monitor) -->
<script src="https://cdn.jsdelivr.net/npm/three@0.145/examples/js/libs/stats.min.js"></script>
```

## Archivos de Ejemplo

### Progresión de Aprendizaje:

1. **01-cubo-basico.cpd** - Tu primer cubo 3D
2. **02-cubo-parametrico.cpd** - Usar variables de Calcpad
3. **03-geometrias-multiples.cpd** - Varios objetos y controles
4. **04-viga-simple.cpd** - Primera estructura de ingeniería
5. **05-viga-con-cargas.cpd** - Visualizar cargas y reacciones
6. **06-malla-fea-simple.cpd** - Malla de elementos finitos
7. **07-malla-fea-colores.cpd** - Mapas de colores por valores
8. **08-animacion-carga.cpd** - Animar aplicación de cargas
9. **09-deformacion-animada.cpd** - Animar deformaciones
10. **10-modelo-completo-fea.cpd** - Modelo FEA completo

## Tips y Trucos

### 1. Debugging
```javascript
// Ver la consola del navegador (F12)
console.log('Variable:', miVariable);

// Agregar ejes de ayuda
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper);

// Agregar grid
const gridHelper = new THREE.GridHelper(10, 10);
scene.add(gridHelper);
```

### 2. Performance
```javascript
// Deshabilitar antialiasing si es lento
const renderer = new THREE.WebGLRenderer({ antialias: false });

// Reducir resolución de sombras
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
```

### 3. Cámara
```javascript
// Mover la cámara
camera.position.set(x, y, z);

// Mirar hacia un punto
camera.lookAt(0, 0, 0);

// Con OrbitControls, definir el target
controls.target.set(x, y, z);
controls.update();
```

### 4. Colores
```javascript
// Hexadecimal
const color = 0xff0000;  // Rojo

// RGB
const color = new THREE.Color(1, 0, 0);  // Rojo

// Nombre
const color = new THREE.Color('red');

// Desde Calcpad
const color = @{calcpad:color_value};  // Debe ser número hex
```

## Errores Comunes y Soluciones

### ❌ "THREE is not defined"
**Causa**: Script de Three.js no cargó
**Solución**: Verificar URL del CDN y conexión a internet

### ❌ "OrbitControls is not a constructor"
**Causa**: Archivo de OrbitControls no cargó
**Solución**: Agregar el script antes de usarlo

### ❌ Pantalla negra
**Causa**: Cámara mal posicionada o sin iluminación
**Solución**: Mover cámara lejos y agregar luces

### ❌ Objeto no visible
**Causa**: No agregado a la escena o fuera de vista
**Solución**: `scene.add(objeto)` y verificar posición

## Siguiente Paso

🚀 **Empieza con `01-cubo-basico.cpd`** y sigue en orden. Cada archivo está comentado para que entiendas cada línea de código.

¡Disfruta creando visualizaciones 3D en Calcpad! 🎨
