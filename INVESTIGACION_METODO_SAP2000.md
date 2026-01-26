# INVESTIGACIÓN - Método de SAP2000 vs Calcpad

## Objetivo
Entender exactamente qué método usa SAP2000 para Plate-Thin (Kirchhoff) y replicarlo en Calcpad para obtener resultados idénticos.

## 1. Información del archivo .s2k

```
SHELL SECTION
  NAME=SSEC1  MAT=CONC    TYPE=Plate,Thin  TH=.1
```

**Tipo:** Plate-Thin = Elemento de placa delgada de Kirchhoff

## 2. Características del Elemento Kirchhoff

### Teoría de Kirchhoff (Placas Delgadas):
- **Hipótesis:** Las normales a la superficie media permanecen normales después de la deformación
- **Despreciado:** Deformación por cortante transversal
- **DOFs por nodo:** 3 (w, θx, θy) o 4 con twist (w, θx, θy, ψ)
- **Válido para:** t/L < 1/20

### Elemento Rectangular de Kirchhoff:

**Opciones de formulación:**

#### A) Elemento de 4 nodos con 3 DOF/nodo = 12 DOF total
- DOFs: w, θx, θy en cada nodo
- Continuidad C0 (solo desplazamiento continuo)
- **Problema:** No garantiza continuidad de derivadas

#### B) Elemento de 4 nodos con 4 DOF/nodo = 16 DOF total
- DOFs: w, θx, θy, ψ (twist) en cada nodo
- Continuidad C1 (desplazamiento y derivadas continuas)
- **Ventaja:** Mejor convergencia
- **Usado por:** Calcpad

#### C) Elemento isoparamétrico con funciones de forma especiales
- Puede usar formulación mixta
- Integración numérica (Gauss)
- **Posiblemente usado por:** SAP2000

## 3. Diferencias Potenciales

### A) Funciones de Forma

**Calcpad usa (según el .cpd):**
```
Φ_1(x) = 1 - x²(3 - 2x)        # Base Hermite
Φ_2(x) = x*L(1 - x(2 - x))     # Base Hermite
Φ_3(x) = x²(3 - 2x)            # Base Hermite
Φ_4(x) = x²*L(-1 + x)          # Base Hermite
```

Estas son **polinomios de Hermite cúbicos** (grado 3).

**SAP2000 podría usar:**
- Formulación similar pero con diferentes coeficientes
- Integración reducida o selectiva
- Correcciones para "shear locking"

### B) Integración Numérica

**Calcpad:**
```calcpad
K_e,ij = a_1*b_1*$Area{$Area{B_i^T*D*B_j @ ξ = 0:1} @ η = 0:1}
```
Usa `$Area` que es integración numérica con puntos de Gauss.

**SAP2000:**
- ¿Cuántos puntos de integración?
- ¿2×2, 3×3, o integración reducida?

### C) Cálculo de Momentos

**En nodos vs en puntos de integración:**
- **Calcpad:** Calcula en nodos y promedia
- **SAP2000:** ¿Calcula en puntos de Gauss y extrapola?

## 4. Plan de Iteración

Vamos a probar:

### Iteración 1: Verificar malla exacta
- ¿Calcpad usa exactamente 6×4 elementos?
- ¿Las coordenadas coinciden?

### Iteración 2: Probar diferentes mallas
- 12×8 elementos (más refinado)
- 3×2 elementos (más grueso)
- Ver si converge a los valores del PDF

### Iteración 3: Revisar parámetros de integración
- Ver si hay opciones de precisión en Calcpad
- Ajustar tolerancias

### Iteración 4: Verificar cálculo de momentos
- ¿Dónde exactamente se extraen los momentos?
- Centro del elemento vs nodo

## 5. Próximos Pasos

1. Ejecutar Calcpad CLI con malla 6×4 (actual)
2. Ejecutar con malla más fina (12×8)
3. Ejecutar con malla más gruesa (3×2)
4. Comparar convergencia

---

**Comenzando iteraciones...**
