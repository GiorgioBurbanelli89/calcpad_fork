# FORMULACIÓN EXACTA DE SAP2000 - Elemento de Placa

## ✅ HALLAZGO CLAVE

**SAP2000 NO usa elemento Batoz/DKQ**

**SAP2000 usa: Formulación de Ibrahimbegovic & Wilson**

---

## 1. Referencia Bibliográfica Exacta

### Paper Original:
**A. Ibrahimbegovic and E. L. Wilson (1991)**
- **Título:** "A Unified Formulation for Triangular and Quadrilateral Flat Shell Finite Elements with Six Nodal Degrees of Freedom"
- **Publicación:** Communications in Applied Numerical Methods, Vol. 7(1), páginas 1-9
- **Año:** 1991

### Referencia Adicional para Verificación:
- Timoshenko and Woinowsky-Krieger (1959)
- "Theory of Plates and Shells", 2nd Edition, McGraw-Hill

---

## 2. Características del Elemento Ibrahimbegovic-Wilson

### Geometría:
- **Elemento cuadrilateral Q4** (4 nodos)
- **DOFs por nodo:** 3 (w, θx, θy)
- **Total DOFs del elemento:** 12

### Formulación para Placa Gruesa (Thick Plate):
```
- Interpolación CÚBICA MEJORADA para la deflexión (w)
- Interpolación CUADRÁTICA MEJORADA para las rotaciones (θx, θy)
- Rotaciones jerárquicas en cada punto medio del borde
- Condensación estática elimina las rotaciones de punto medio
- Resultado final: 12 DOF
```

### ⭐ COMPONENTE CLAVE: Modos Incompatibles de Wilson

**SAP2000 implementa:**
- **9 modos incompatibles opcionales** para elementos sólidos/placa
- Desarrollado por Wilson, Taylor, Doherty y Ghaboussi (1973)
- Mejorado por Ibrahimbegovic & Wilson (1991)

**Qué son los "modos incompatibles":**
```
- Funciones de desplazamiento adicionales que NO son compatibles entre elementos
- Mejoran la precisión sin añadir DOFs en los nodos
- Se eliminan por condensación estática a nivel de elemento
- Resultado: Mejor convergencia con menos elementos
```

**Paper fundamental:**
- Wilson et al. (1973): "Incompatible displacement models"
- En: Numerical and Computer Models in Structural Mechanics, Academic Press

### Opciones de Teoría:
1. **Thin Plate (Kirchhoff):** Sin deformación por cortante transversal
2. **Thick Plate (Mindlin/Reissner):** Con deformación por cortante

Para la placa 6×4 con t=0.1m:
```
t/L = 0.1/6 = 1/60 < 1/20  →  Teoría de Kirchhoff es válida
```

---

## 3. Diferencias con CALCPAD

| Característica | CALCPAD (Hermite) | SAP2000 (Ibrahimbegovic-Wilson) |
|----------------|-------------------|----------------------------------|
| **DOFs/nodo** | 4 (w, θx, θy, ψ) | 3 (w, θx, θy) |
| **Total DOFs** | 16 | 12 |
| **Twist (ψ)** | Explícito | Implícito (eliminado por condensación) |
| **Interpolación w** | Hermite cúbico | Cúbico mejorado |
| **Interpolación θ** | Hermite cúbico | Cuadrático mejorado |
| **Rotaciones medias** | No | Sí (pero condensadas) |

---

## 4. Por Qué Esta Diferencia Causa los Resultados Observados

### A) Momentos Mx y My (< 1% diferencia)
- Ambas formulaciones convergen bien en el centro de la placa
- La interpolación cúbica captura correctamente la curvatura principal

### B) Momento Mxy (13.5% diferencia)
- **Hermite (CALCPAD):** Usa twist (ψ) explícito
  - Puede sobreestimar momentos de torsión en ~10-15%
  - No tiene modos incompatibles

- **Ibrahimbegovic-Wilson (SAP2000):** Usa condensación estática + modos incompatibles
  - Elimina DOFs redundantes
  - **Modos incompatibles mejoran la precisión**
  - Torsión calculada de manera más eficiente
  - Mejor comportamiento en esquinas

**La clave está en los MODOS INCOMPATIBLES:**
- Son funciones de forma adicionales dentro del elemento
- Mejoran la representación de la curvatura
- Se condensan localmente (no afectan sistema global)
- Dan resultados más precisos con mallas gruesas

---

## 5. Ventajas del Elemento Ibrahimbegovic-Wilson

1. ✅ **Menos DOFs:** 12 vs 16 (más eficiente)
2. ✅ **Mejor en torsión:** Condensación estática mejora precisión de Mxy
3. ✅ **Unificación:** Misma formulación para triangular (T3) y cuadrilateral (Q4)
4. ✅ **Pasa patch test:** Convergencia garantizada
5. ✅ **Sin locking:** Mejor comportamiento que Hermite estándar

---

## 6. Implementación en SAP2000

### Código del archivo .s2k:
```
SHELL SECTION
  NAME=SSEC1  MAT=CONC    TYPE=Plate,Thin  TH=.1
```

`TYPE=Plate,Thin` activa:
- Formulación de Ibrahimbegovic-Wilson
- Teoría de Kirchhoff (sin cortante transversal)
- Elemento Q4 con 12 DOF

---

## 7. Plan para Igualar Resultados en CALCPAD

### OPCIÓN A: Implementar Ibrahimbegovic-Wilson en .cpd

**Pasos:**
1. Obtener el paper completo de Ibrahimbegovic & Wilson (1991)
2. Extraer las funciones de forma mejoradas
3. Implementar condensación estática de rotaciones medias
4. Reducir de 16 a 12 DOFs

**Tiempo estimado:** 3-5 días

**Resultado esperado:** Resultados IDÉNTICOS a SAP2000

---

### OPCIÓN B: Factor de Corrección Empírico (RÁPIDO)

**Solo para Mxy:**
```calcpad
Mxy_corr = Mxy_hermite × 0.865  # 7.25/8.378
```

**Tiempo:** 30 minutos

**Resultado:** Mxy coincide, pero no es la solución correcta

---

### OPCIÓN C: Refinar Malla y Analizar Convergencia

**Probar:**
- Malla 12×8 (96 elementos)
- Malla 24×16 (384 elementos)

**Hipótesis:**
- Hermite con malla fina → debería converger hacia valor más bajo
- Diferencia podría reducirse de 13.5% a ~5%

**Tiempo:** 2 horas

---

## 8. Próximo Paso Recomendado

### 🎯 BUSCAR EL PAPER DE IBRAHIMBEGOVIC-WILSON

**Necesitamos:**
1. El paper completo (Communications in Applied Numerical Methods, 1991)
2. Ecuaciones exactas de las funciones de forma mejoradas
3. Procedimiento de condensación estática
4. Matriz de rigidez del elemento

**Con esto podremos:**
- Implementar el elemento exacto en Calcpad
- Obtener resultados idénticos a SAP2000
- Validar completamente la implementación

---

## Fuentes

### Documentación SAP2000:
- [CSI Knowledge Base - Shell FAQ](https://wiki.csiamerica.com/pages/viewpage.action?pageId=4161682)
- [SAP2000 Basic Analysis Reference Manual](https://studylib.net/doc/27872782/04---sapbasic)
- [CSI Analysis Reference Manual (SAP2000, ETABS, SAFE)](https://www.academia.edu/28385689/CSI_Anal_y_sis_Reference_Manual_For_SAP2000_ETABS_and_SAFE)
- [SAP2000 Verification Examples](https://docs.csiamerica.com/manuals/csibridge/Verification/Analysis/Shells/Problem%202-001.pdf)

### Papers Académicos:
- [Ibrahimbegovic & Wilson (1991) - Unified Formulation](https://onlinelibrary.wiley.com/doi/abs/10.1002/cnm.1630070102)
- [A Modified Method of Incompatible Modes](https://www.semanticscholar.org/paper/A-modified-method-of-incompatible-modes-Ibrahimbegovic-Wilson/09c0485db4353aea763d15db5add439b92071977)
- [Edward L. Wilson - Wikipedia](https://en.wikipedia.org/wiki/Edward_L._Wilson)
- [Three Dimensional Static and Dynamic Analysis of Structures](https://edwilson.org/bookshelf/edsbook)
- [Ibrahimbegovic CV with Publications](https://shellbuckling.com/cv/ibrahimbegovic.pdf)

---

**Fecha:** 2026-01-18

**Conclusión:** El elemento de SAP2000 es la formulación de **Ibrahimbegovic & Wilson (1991)**, NO Batoz. Esta formulación usa 12 DOF con interpolación cúbica mejorada y condensación estática, explicando las diferencias observadas con CALCPAD.
