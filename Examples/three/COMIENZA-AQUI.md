# 🎯 COMIENZA AQUÍ - Guía Rápida

## ¿Qué encontrarás en esta carpeta?

Esta carpeta contiene **13 tutoriales progresivos** para aprender visualización 3D en Calcpad, desde lo más básico hasta análisis de elementos finitos (FEA) completos.

---

## 📋 Índice de Contenidos

### 📚 **Nivel 0: Fundamentos (Si no conoces HTML/JavaScript)**

Si nunca has programado en HTML, CSS o JavaScript, **empieza aquí**:

1. **HTML-desde-cero.md** - Guía completa de HTML/CSS/JavaScript para ingenieros
   - Qué son las etiquetas HTML
   - Cómo funciona CSS
   - Conceptos básicos de JavaScript
   - Cómo interactuar con el DOM
   - Debugging con console.log

2. **Animaciones-01-basico.cpd** - Conceptos fundamentales de animación
   - ¿Qué es un frame y FPS?
   - `requestAnimationFrame()` - El loop de animación
   - Movimiento simple (cuadrado que se mueve)
   - Oscilación con `Math.sin()`
   - Múltiples objetos animados
   - Control con botones (play/pause)

3. **Animaciones-02-easing.cpd** - Funciones de suavizado
   - Linear (movimiento constante)
   - Ease In (acelerando)
   - Ease Out (frenando)
   - Ease In-Out (curva S)
   - Bounce (rebote)
   - Elastic (elástico)
   - Gráfica comparativa de todas las curvas

4. **Animaciones-03-threejs-aplicado.cpd** - Puente entre Canvas y Three.js
   - Cómo aplicar easing a objetos 3D
   - Múltiples esferas oscilando
   - Combinación con OrbitControls
   - Morphing entre geometrías
   - Tabla comparativa Canvas vs Three.js

---

### 🟢 **Nivel 1: Fundamentos de Three.js**

5. **01-cubo-basico.cpd** - Tu primer objeto 3D
   - Los 3 elementos básicos: Scene, Camera, Renderer
   - Crear un cubo verde que rota
   - Loop de animación básico

6. **02-cubo-parametrico.cpd** - Conexión con Calcpad
   - Usar variables de Calcpad: `@{calcpad:variable}`
   - Grid y ejes de referencia
   - Etiquetas de dimensiones

---

### 🟡 **Nivel 2: Geometrías y Controles**

7. **03-geometrias-multiples.cpd** - Más objetos 3D
   - Esfera, cilindro, cono, toroide
   - OrbitControls (navegación 3D con mouse)
   - Sombras e iluminación

8. **04-viga-simple.cpd** - Primera estructura de ingeniería
   - Viga simplemente apoyada
   - Representación de apoyos
   - Etiquetas de texto con Sprites

9. **05-viga-con-cargas.cpd** - Visualización de fuerzas
   - Cargas puntuales (flechas rojas)
   - Cargas distribuidas (múltiples flechas)
   - Reacciones (flechas verdes)
   - Momentos (arcos curvos)

---

### 🟠 **Nivel 3: Elementos Finitos**

10. **06-malla-fea-simple.cpd** - Tu primera malla FEA
    - Concepto de nodos y elementos
    - BufferGeometry para FEA
    - Conectividad de elementos
    - Visualización de bordes

11. **07-malla-fea-colores.cpd** - Mapas de color
    - Escala rainbow para desplazamientos
    - Interpolación automática de colores
    - Barra de escala (colorbar)

---

### 🔴 **Nivel 4: Avanzado e Interactivo**

12. **08-animacion-carga.cpd** - Carga progresiva
    - Aplicación gradual de carga
    - Deformación en tiempo real
    - Controles play/pause/velocidad

13. **09-deformacion-animada.cpd** - Vibración modal
    - Simulación de primer modo de vibración
    - Oscilación armónica con seno
    - Frecuencia natural

14. **10-modelo-completo-fea.cpd** - 🏆 Ejemplo definitivo
    - Panel de control completo
    - Múltiples vistas de resultados
    - Modo desplazamientos/reacciones/momentos
    - Factor de escala ajustable
    - Toggles de grid/ejes/apoyos/wireframe
    - Profesional y completo

---

## 🎓 Ruta de Aprendizaje Recomendada

### Si **NO conoces HTML/JavaScript**:
```
1. HTML-desde-cero.md (lee todo)
2. Animaciones-01-basico.cpd
3. Animaciones-02-easing.cpd
4. Animaciones-03-threejs-aplicado.cpd
5. 01-cubo-basico.cpd
6. Continúa del 02 al 10 en orden
```

### Si **YA conoces HTML/JavaScript**:
```
1. Animaciones-03-threejs-aplicado.cpd (opcional, para repasar conceptos)
2. 01-cubo-basico.cpd
3. Continúa del 02 al 10 en orden
```

### Si **YA conoces Three.js**:
```
1. 04-viga-simple.cpd (ver cómo integrar con Calcpad)
2. 06-malla-fea-simple.cpd (FEA basics)
3. 10-modelo-completo-fea.cpd (ejemplo completo)
```

---

## 🚀 Cómo usar estos archivos

### Opción 1: Índice Visual Interactivo
Abre `00-indice.cpd` en Calcpad para ver un índice interactivo con tarjetas clickeables.

### Opción 2: Leer en orden
Simplemente abre los archivos en orden numérico. Cada archivo tiene:
- ✅ Explicaciones detalladas
- ✅ Código completamente comentado
- ✅ Ejemplos interactivos
- ✅ Conceptos clave destacados

---

## 📖 Archivos de Referencia

- **README.md** - Guía completa de Three.js (conceptos, API, solución de errores)
- **HTML-desde-cero.md** - Tutorial completo de HTML/CSS/JS
- **00-indice.cpd** - Índice visual interactivo

---

## 💡 Consejos Importantes

### 1. **No te saltes ejemplos**
Cada ejemplo construye sobre el anterior. Si saltas, te perderás conceptos clave.

### 2. **Experimenta con el código**
No solo leas. Modifica valores, cambia colores, ajusta dimensiones.

### 3. **Usa la consola del navegador**
Presiona **F12** para ver errores y usar `console.log()`.

### 4. **Copia y adapta**
Una vez que entiendas un ejemplo, cópialo y modifícalo para tus necesidades.

### 5. **Lee los comentarios**
Cada línea compleja está comentada explicando qué hace y por qué.

---

## 🔍 ¿Qué aprenderás?

Al terminar estos tutoriales, sabrás:

- ✅ Crear objetos 3D interactivos
- ✅ Animar objetos con easing suave
- ✅ Conectar Calcpad con Three.js
- ✅ Visualizar estructuras de ingeniería
- ✅ Crear mallas de elementos finitos
- ✅ Mostrar resultados con mapas de color
- ✅ Implementar controles interactivos
- ✅ Crear dashboards profesionales

---

## 🆘 Si te atascas

1. **Lee la sección de errores comunes** en README.md
2. **Revisa la consola** (F12) para ver mensajes de error
3. **Usa console.log()** para inspeccionar variables
4. **Compara con el ejemplo anterior** para ver qué cambió
5. **Lee los comentarios** línea por línea

---

## 📚 Recursos Externos

- **Three.js Docs**: https://threejs.org/docs/
- **Three.js Examples**: https://threejs.org/examples/
- **MDN Web Docs**: https://developer.mozilla.org/es/
- **Three.js Forum**: https://discourse.threejs.org/

---

## 🎯 Objetivo Final

Al terminar, podrás crear visualizaciones 3D profesionales de tus análisis de ingeniería directamente en Calcpad, combinando:

- Cálculos de Calcpad
- Visualización 3D con Three.js
- Interactividad con controles
- Presentación profesional

---

**¡Comienza ahora!**

👉 Si no conoces HTML: Abre `HTML-desde-cero.md`
👉 Si conoces HTML: Abre `01-cubo-basico.cpd`
👉 Para ver todo: Abre `00-indice.cpd`

---

*Creado para aprender Three.js en Calcpad - De lo más simple a lo más complejo* 🎨
