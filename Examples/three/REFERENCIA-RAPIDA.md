# 🔖 Referencia Rápida - Three.js en Calcpad

Código listo para copiar y pegar en tus proyectos.

---

## 📦 Plantilla Básica

```calcpad
"Título de tu análisis

'Parámetros de entrada'
ancho = 10
alto = 5
profundidad = 3

@{html}
<div id="canvas-container" style="width: 100%; height: 500px;"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<script>
  // Setup
  const container = document.getElementById('canvas-container');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  const camera = new THREE.PerspectiveCamera(
    75,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
  );
  camera.position.set(10, 10, 10);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  // Iluminación básica
  scene.add(new THREE.DirectionalLight(0xffffff, 1));
  scene.add(new THREE.AmbientLight(0x404040));

  // Grid
  scene.add(new THREE.GridHelper(20, 20));

  // Tu código aquí
  // ...

  // Renderizar
  renderer.render(scene, camera);
</script>
@{end html}
```

---

## 🎬 Plantilla con Animación

```javascript
let animando = true;
let tiempo = 0;

function animate() {
  requestAnimationFrame(animate);

  if (animando) {
    tiempo += 0.01;

    // Tu código de animación aquí
    // Ejemplo: miObjeto.rotation.y = tiempo;
  }

  renderer.render(scene, camera);
}

animate();
```

---

## 🖱️ Agregar OrbitControls

```html
<!-- Agregar DESPUÉS del script de Three.js -->
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
  // Después de crear camera y renderer
  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;

  // En el loop de animación
  function animate() {
    requestAnimationFrame(animate);
    controls.update();  // ← Importante
    renderer.render(scene, camera);
  }
</script>
```

---

## 📦 Geometrías Comunes

### Cubo
```javascript
const geometry = new THREE.BoxGeometry(ancho, alto, profundidad);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
const cubo = new THREE.Mesh(geometry, material);
scene.add(cubo);
```

### Esfera
```javascript
const geometry = new THREE.SphereGeometry(radio, 32, 32);
const material = new THREE.MeshStandardMaterial({ color: 0x0000ff });
const esfera = new THREE.Mesh(geometry, material);
scene.add(esfera);
```

### Cilindro
```javascript
const geometry = new THREE.CylinderGeometry(radioTop, radioBottom, altura, 32);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const cilindro = new THREE.Mesh(geometry, material);
scene.add(cilindro);
```

### Cono
```javascript
const geometry = new THREE.ConeGeometry(radio, altura, 32);
const material = new THREE.MeshStandardMaterial({ color: 0xffff00 });
const cono = new THREE.Mesh(geometry, material);
scene.add(cono);
```

### Toroide
```javascript
const geometry = new THREE.TorusGeometry(radio, tubo, 16, 100);
const material = new THREE.MeshStandardMaterial({ color: 0xff00ff });
const torus = new THREE.Mesh(geometry, material);
scene.add(torus);
```

### Línea
```javascript
const points = [];
points.push(new THREE.Vector3(0, 0, 0));
points.push(new THREE.Vector3(10, 0, 0));
points.push(new THREE.Vector3(10, 5, 0));

const geometry = new THREE.BufferGeometry().setFromPoints(points);
const material = new THREE.LineBasicMaterial({ color: 0x0000ff });
const line = new THREE.Line(geometry, material);
scene.add(line);
```

---

## 🎨 Materiales Comunes

### Material Básico (sin iluminación)
```javascript
const material = new THREE.MeshBasicMaterial({
  color: 0x00ff00,
  wireframe: false
});
```

### Material Standard (con iluminación)
```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0x00ff00,
  metalness: 0.3,
  roughness: 0.7
});
```

### Material Transparente
```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0x00ff00,
  transparent: true,
  opacity: 0.5
});
```

### Material con Wireframe
```javascript
const material = new THREE.MeshBasicMaterial({
  color: 0x00ff00,
  wireframe: true
});
```

---

## 💡 Iluminación

### Luz Ambiente
```javascript
const ambientLight = new THREE.AmbientLight(0x404040); // Luz tenue
scene.add(ambientLight);
```

### Luz Direccional
```javascript
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 5);
scene.add(directionalLight);
```

### Luz Puntual
```javascript
const pointLight = new THREE.PointLight(0xff0000, 1, 50);
pointLight.position.set(5, 5, 5);
scene.add(pointLight);
```

### Luz Spot
```javascript
const spotLight = new THREE.SpotLight(0xffffff, 1);
spotLight.position.set(10, 10, 10);
spotLight.angle = Math.PI / 6;
scene.add(spotLight);
```

---

## 🏷️ Etiquetas de Texto

### Método 1: Sprite (recomendado)
```javascript
function crearEtiqueta(texto, posX, posY, posZ) {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');
  canvas.width = 256;
  canvas.height = 64;

  context.fillStyle = 'white';
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = 'black';
  context.font = 'bold 20px Arial';
  context.textAlign = 'center';
  context.fillText(texto, 128, 40);

  const texture = new THREE.CanvasTexture(canvas);
  const material = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(material);
  sprite.position.set(posX, posY, posZ);
  sprite.scale.set(2, 0.5, 1);

  return sprite;
}

// Uso
const etiqueta = crearEtiqueta('L = 10 m', 5, 2, 0);
scene.add(etiqueta);
```

---

## ➡️ Flechas (Cargas, Fuerzas)

### Flecha Simple
```javascript
const origen = new THREE.Vector3(0, 0, 0);
const direccion = new THREE.Vector3(0, 1, 0).normalize();
const longitud = 5;
const color = 0xff0000;

const arrow = new THREE.ArrowHelper(direccion, origen, longitud, color);
scene.add(arrow);
```

### Flecha con Parámetros de Calcpad
```javascript
const cargaX = @{calcpad:carga_x};
const cargaY = @{calcpad:carga_y};

const origen = new THREE.Vector3(0, 0, 0);
const direccion = new THREE.Vector3(cargaX, cargaY, 0).normalize();
const longitud = Math.sqrt(cargaX * cargaX + cargaY * cargaY);

const arrow = new THREE.ArrowHelper(direccion, origen, longitud, 0xff0000);
scene.add(arrow);
```

---

## 🔄 Easing Functions (copiar y pegar)

```javascript
const easing = {
  linear: t => t,
  easeInQuad: t => t * t,
  easeOutQuad: t => t * (2 - t),
  easeInOutQuad: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
  easeInCubic: t => t * t * t,
  easeOutCubic: t => (--t) * t * t + 1,
  easeInOutCubic: t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
  easeOutBounce: t => {
    const n1 = 7.5625, d1 = 2.75;
    if (t < 1 / d1) {
      return n1 * t * t;
    } else if (t < 2 / d1) {
      return n1 * (t -= 1.5 / d1) * t + 0.75;
    } else if (t < 2.5 / d1) {
      return n1 * (t -= 2.25 / d1) * t + 0.9375;
    } else {
      return n1 * (t -= 2.625 / d1) * t + 0.984375;
    }
  },
  easeOutElastic: t => {
    const c4 = (2 * Math.PI) / 3;
    return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  }
};

// Uso
let t = 0;  // 0 a 1
const easedT = easing.easeOutBounce(t);
objeto.position.x = inicio + (fin - inicio) * easedT;
```

---

## 🎨 Mapa de Colores Rainbow

```javascript
function valorAColorRainbow(valor, min, max) {
  const t = (valor - min) / (max - min); // Normalizar 0-1
  const hue = (1 - t) * 240 / 360;  // 240° (azul) a 0° (rojo)
  const color = new THREE.Color();
  color.setHSL(hue, 1, 0.5);
  return color;
}

// Uso
const valor = 0.75;
const color = valorAColorRainbow(valor, 0, 1);
material.color = color;
```

---

## 🔲 Malla FEA Simple

```javascript
// Nodos (x, y, z)
const nodos = [
  [0, 0, 0],
  [1, 0, 0],
  [1, 1, 0],
  [0, 1, 0]
];

// Elementos (índices de nodos)
const elementos = [
  [0, 1, 2],
  [0, 2, 3]
];

// Crear BufferGeometry
const vertices = [];
const indices = [];

nodos.forEach(nodo => {
  vertices.push(nodo[0], nodo[1], nodo[2]);
});

elementos.forEach(elem => {
  indices.push(elem[0], elem[1], elem[2]);
});

const geometry = new THREE.BufferGeometry();
geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
geometry.setIndex(indices);
geometry.computeVertexNormals();

const material = new THREE.MeshStandardMaterial({
  color: 0x00ff00,
  side: THREE.DoubleSide
});

const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
```

---

## 🎮 Controles Interactivos

### Botones
```html
<button id="miBoton">Click aquí</button>

<script>
  document.getElementById('miBoton').addEventListener('click', () => {
    console.log('Botón presionado');
    // Tu código aquí
  });
</script>
```

### Slider
```html
<input type="range" id="miSlider" min="0" max="100" value="50">
<span id="valorSlider">50</span>

<script>
  document.getElementById('miSlider').addEventListener('input', (e) => {
    const valor = e.target.value;
    document.getElementById('valorSlider').textContent = valor;
    // Usar el valor
    objeto.scale.setScalar(valor / 50);
  });
</script>
```

### Checkbox
```html
<input type="checkbox" id="miCheckbox" checked>
<label for="miCheckbox">Mostrar grid</label>

<script>
  document.getElementById('miCheckbox').addEventListener('change', (e) => {
    const mostrar = e.target.checked;
    grid.visible = mostrar;
  });
</script>
```

### Select (Dropdown)
```html
<select id="miSelect">
  <option value="opcion1">Opción 1</option>
  <option value="opcion2">Opción 2</option>
  <option value="opcion3">Opción 3</option>
</select>

<script>
  document.getElementById('miSelect').addEventListener('change', (e) => {
    const opcion = e.target.value;
    console.log('Seleccionado:', opcion);
    // Tu código aquí
  });
</script>
```

---

## 🔍 Interpolación de Valores

### Interpolar Posición
```javascript
function lerp(inicio, fin, t) {
  return inicio + (fin - inicio) * t;
}

// Uso
const t = 0.5;  // 50%
const x = lerp(0, 10, t);  // 5
```

### Interpolar Color
```javascript
function lerpColor(color1, color2, t) {
  const c1 = new THREE.Color(color1);
  const c2 = new THREE.Color(color2);
  return c1.lerp(c2, t);
}

// Uso
const t = 0.3;
const color = lerpColor(0x0000ff, 0xff0000, t);
```

---

## 📊 Grid y Ejes

### Grid
```javascript
const grid = new THREE.GridHelper(20, 20);  // Tamaño, divisiones
scene.add(grid);
```

### Ejes (X=rojo, Y=verde, Z=azul)
```javascript
const axes = new THREE.AxesHelper(5);  // Longitud
scene.add(axes);
```

---

## 💾 Guardar Posiciones Iniciales

```javascript
// Guardar posiciones originales
const posicionesOriginales = [];
malla.geometry.attributes.position.array.forEach(coord => {
  posicionesOriginales.push(coord);
});

// Restaurar
function restaurarPosiciones() {
  const positions = malla.geometry.attributes.position;
  for (let i = 0; i < posicionesOriginales.length; i++) {
    positions.array[i] = posicionesOriginales[i];
  }
  positions.needsUpdate = true;
  malla.geometry.computeVertexNormals();
}
```

---

## 🖼️ Responsive (Ajustar al redimensionar ventana)

```javascript
window.addEventListener('resize', () => {
  const width = container.clientWidth;
  const height = container.clientHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();

  renderer.setSize(width, height);
});
```

---

## 🐛 Debugging

### Console.log básico
```javascript
console.log('Valor de x:', x);
console.log('Objeto completo:', miObjeto);
console.log('Posición:', miObjeto.position);
```

### Verificar si existe un objeto
```javascript
if (miObjeto) {
  console.log('El objeto existe');
} else {
  console.log('El objeto NO existe');
}
```

### Ver estructura de un objeto
```javascript
console.dir(miObjeto);  // Muestra toda la estructura
```

---

## ⚡ Optimización

### Usar BufferGeometry (más eficiente)
```javascript
// ✅ Bien
const geometry = new THREE.BufferGeometry();

// ❌ Evitar (versión vieja)
const geometry = new THREE.Geometry();  // Deprecado
```

### Reutilizar geometrías y materiales
```javascript
// ✅ Bien
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });

for (let i = 0; i < 100; i++) {
  const mesh = new THREE.Mesh(geometry, material);  // Reutiliza
  mesh.position.x = i;
  scene.add(mesh);
}
```

---

## 🎯 Código Útil de Calcpad

### Obtener variables
```javascript
const valor = @{calcpad:miVariable};
```

### Múltiples variables
```javascript
const ancho = @{calcpad:ancho};
const alto = @{calcpad:alto};
const carga = @{calcpad:carga_kN};
```

### Array desde Calcpad
```calcpad
'Definir array en Calcpad'
coords = [0; 1; 2; 3; 4]

@{html}
<script>
  // Convertir a array de JavaScript
  const coords = [@{calcpad:coords[1]}; @{calcpad:coords[2]}; @{calcpad:coords[3]}];
</script>
@{end html}
```

---

## 📋 Checklist de Errores Comunes

- [ ] ¿Agregaste el script de Three.js?
- [ ] ¿Llamaste `renderer.render()` al final?
- [ ] ¿La cámara está apuntando al objeto? (`camera.lookAt()`)
- [ ] ¿Hay iluminación? (luz ambiente + direccional)
- [ ] ¿El objeto está en `scene`? (`scene.add(objeto)`)
- [ ] ¿Abriste la consola (F12) para ver errores?
- [ ] ¿Usas `controls.update()` si tienes OrbitControls?

---

**¡Copia, pega y adapta a tu proyecto!** 🚀
