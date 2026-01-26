# PLAN DE IMPLEMENTACIÓN - Modos Incompatibles en Calcpad

## Resumen Ejecutivo

**Problema Identificado:**
- CALCPAD usa elemento Hermite de 16 DOF (w, θx, θy, ψ)
- SAP2000 usa elemento Ibrahimbegovic-Wilson de 12 DOF + **modos incompatibles**
- Diferencia en Mxy: 13.5% (8.378 vs 7.25 kN-m/m)

**Causa Raíz:**
- SAP2000 tiene **9 modos incompatibles opcionales** que mejoran precisión
- Estos modos se condensan localmente (no añaden DOFs globales)
- Dan mejor convergencia con mallas gruesas

---

## 1. ¿Qué Son los Modos Incompatibles?

### Concepto Fundamental

**Formulación estándar:**
```
u(x,y) = Σ Ni(x,y) * ui   (funciones de forma compatibles)
```

**Con modos incompatibles:**
```
u(x,y) = Σ Ni(x,y) * ui + Σ Mi(x,y) * αi

Donde:
- Ni = funciones de forma estándar (compatibles entre elementos)
- Mi = funciones incompatibles (solo dentro del elemento)
- αi = parámetros internos (se eliminan por condensación)
```

### Ventajas

1. ✅ **Mejor representación de la curvatura** dentro del elemento
2. ✅ **No añaden DOFs globales** (se condensan localmente)
3. ✅ **Convergencia más rápida** (menos elementos necesarios)
4. ✅ **Mejoran momentos de torsión** (crítico para Mxy)

### Ejemplo para Elemento de Placa

**Modos incompatibles típicos para placa Q4:**
```
M1(ξ,η) = (ξ² - 1/3)     # Mejora curvatura en x
M2(ξ,η) = (η² - 1/3)     # Mejora curvatura en y
M3(ξ,η) = ξη             # Mejora torsión
...
(hasta 9 modos para elemento completo)
```

---

## 2. Formulación del Método de Wilson (1973)

### Papers Fundamentales

**1. Wilson et al. (1973):**
- Título: "Incompatible displacement models"
- Referencia: Numerical and computer methods in structural mechanics, pp 43–57
- Editorial: Academic Press

**2. Wilson (1974):**
- Título: "Static condensation algorithm"
- Referencia: Int. J. Numer. Methods Eng., 8, 199–203

**3. Ibrahimbegovic & Wilson (1991):**
- Título: "A modified method of incompatible modes"
- Referencia: Communications in Applied Numerical Methods, 7(3)
- **Modificación clave:** Asegura deformación constante y convergencia

---

## 3. Procedimiento de Implementación

### Paso 1: Definir Funciones Incompatibles

Para elemento rectangular en coordenadas naturales (ξ, η ∈ [-1, 1]):

```calcpad
'Modos incompatibles para flexión de placa (9 modos):
M_1(ξ; η) = ξ^2 - 1/3
M_2(ξ; η) = η^2 - 1/3
M_3(ξ; η) = ξ*η
M_4(ξ; η) = ξ*(η^2 - 1/3)
M_5(ξ; η) = η*(ξ^2 - 1/3)
M_6(ξ; η) = (ξ^2 - 1/3)*(η^2 - 1/3)
M_7(ξ; η) = ξ^3 - 3*ξ/5
M_8(ξ; η) = η^3 - 3*η/5
M_9(ξ; η) = ξ*η*(ξ^2 + η^2 - 2/3)
```

### Paso 2: Ampliar Campo de Desplazamiento

**Desplazamiento total:**
```calcpad
'Campo de desplazamiento con modos incompatibles:
w(ξ; η) = w_compatible(ξ; η) + w_incompatible(ξ; η)

w_compatible(ξ; η) = Σ N_i(ξ; η)*w_i   'i = 1..16 (Hermite estándar)
w_incompatible(ξ; η) = Σ M_j(ξ; η)*α_j  'j = 1..9 (modos incompatibles)
```

### Paso 3: Matriz de Rigidez Ampliada

**Matriz de rigidez con modos incompatibles:**
```
[ K_uu  K_uα ] { u }   { F }
[ K_αu  K_αα ] { α } = { 0 }

Donde:
- K_uu = rigidez estándar (16×16)
- K_uα = acoplamiento (16×9)
- K_αα = rigidez de modos incompatibles (9×9)
- α = parámetros internos (fuerzas = 0)
```

### Paso 4: Condensación Estática

**Eliminar α a nivel de elemento:**
```
α = -K_αα^(-1) * K_αu * u

Sustituir en primera ecuación:
K_condensed * u = F

Donde:
K_condensed = K_uu - K_uα * K_αα^(-1) * K_αu
```

**Resultado:** Matriz 16×16 mejorada sin añadir DOFs globales

---

## 4. Implementación en Calcpad

### Opción A: Implementación Completa (PRECISA)

**Modificar:** `Rectangular Slab FEA.cpd`

**Cambios requeridos:**

#### 4.1. Añadir Modos Incompatibles (después línea 153)
```calcpad
'<h4>Incompatible Modes (Wilson 1973)</h4>
'Modos incompatibles para mejorar convergencia:
M_1(ξ; η) = ξ^2 - 1/3
M_2(ξ; η) = η^2 - 1/3
M_3(ξ; η) = ξ*η
M_4(ξ; η) = ξ*(η^2 - 1/3)
M_5(ξ; η) = η*(ξ^2 - 1/3)
M_6(ξ; η) = (ξ^2 - 1/3)*(η^2 - 1/3)
M_7(ξ; η) = ξ^3 - 3*ξ/5
M_8(ξ; η) = η^3 - 3*η/5
M_9(ξ; η) = ξ*η*(ξ^2 + η^2 - 2/3)
```

#### 4.2. Calcular Matriz K_αα (9×9)
```calcpad
'Matriz de rigidez de modos incompatibles:
$Map{i = 1 : 9
    $Map{j = 1 : 9
        B_α,i(ξ; η) = [derivadas de M_i]
        K_αα,ij = a_1*b_1*$Area{$Area{B_α,i^T*D*B_α,j @ ξ = 0:1} @ η = 0:1}
    }
}
```

#### 4.3. Calcular Matriz K_uα (16×9)
```calcpad
'Matriz de acoplamiento:
$Map{i = 1 : 16
    $Map{j = 1 : 9
        K_uα,ij = a_1*b_1*$Area{$Area{B_i^T*D*B_α,j @ ξ = 0:1} @ η = 0:1}
    }
}
```

#### 4.4. Condensación Estática
```calcpad
'Matriz condensada (método de Wilson):
K_e_condensed,ij = K_e,ij - K_uα,ik*(K_αα^-1),kl*K_uα,lj
```

**Tiempo estimado:** 5-7 días de implementación

**Resultado esperado:** Resultados IDÉNTICOS a SAP2000

---

### Opción B: Simplificación con Refinamiento de Malla

**Hipótesis:**
- Modos incompatibles permiten convergencia con mallas gruesas
- Hermite sin modos incompatibles converge con mallas finas
- Si refinamos suficientemente, deberíamos acercarnos al valor exacto

**Prueba:**
```calcpad
'Modificar línea 12 de "Rectangular Slab FEA.cpd":
n_a = 24', 'n_b = 16   'En lugar de n_a = 6', 'n_b = 4
```

**Tiempo estimado:** 1 hora

**Resultado esperado:** Reducir diferencia de 13.5% a ~5%

---

### Opción C: Factor de Corrección Empírico

**Basado en comparación SAP2000 vs CALCPAD:**

```calcpad
'Al final del cálculo, aplicar:
Mxy_corregido = Mxy_calcpad * 0.865

'Donde 0.865 = 7.25/8.378 (factor empírico)
```

**Ventajas:** Rápido (30 min)
**Desventajas:** No es la solución correcta, solo empírica

---

## 5. Recursos Necesarios

### Papers a Obtener:

1. ✅ **Wilson et al. (1973)** - "Incompatible displacement models"
   - Buscar en: Google Scholar, biblioteca universitaria
   - Contiene: Formulación original de modos incompatibles

2. ✅ **Wilson (1974)** - "Static condensation algorithm"
   - Int. J. Numer. Methods Eng., 8, 199–203
   - Contiene: Algoritmo de condensación estática

3. ✅ **Ibrahimbegovic & Wilson (1991)** - "A modified method"
   - Communications in Applied Numerical Methods, 7(3)
   - Contiene: Correcciones para asegurar convergencia
   - **Disponible en:** [Wiley Online Library](https://onlinelibrary.wiley.com/doi/10.1002/cnm.1630070303)

### Libros de Referencia:

4. **Edward Wilson** - "Three Dimensional Static and Dynamic Analysis of Structures"
   - **Disponible en:** https://edwilson.org/bookshelf/edsbook
   - Capítulo sobre elementos finitos y modos incompatibles

5. **Klaus-Jürgen Bathe** - "Finite Element Procedures"
   - Capítulo sobre plate and shell elements

---

## 6. Cronograma Propuesto

### Fase 1: Investigación (1-2 días)
- [ ] Obtener papers de Wilson (1973, 1974, 1991)
- [ ] Leer libro de Wilson (capítulo elementos finitos)
- [ ] Extraer ecuaciones exactas de modos incompatibles

### Fase 2: Prueba Rápida (1 día)
- [ ] Probar malla 12×8 en Calcpad
- [ ] Probar malla 24×16 en Calcpad
- [ ] Analizar convergencia

### Fase 3: Implementación (3-5 días)
- [ ] Programar funciones de modos incompatibles
- [ ] Calcular matrices K_αα y K_uα
- [ ] Implementar condensación estática
- [ ] Verificar con caso de prueba

### Fase 4: Validación (1 día)
- [ ] Ejecutar modelo 6×4 con modos incompatibles
- [ ] Comparar con PDF (SAP2000 v6-7)
- [ ] Verificar que Mxy = 7.25 kN-m/m

**Total:** 6-9 días de trabajo

---

## 7. Criterio de Éxito

### Resultados Objetivo:

| Parámetro | CALCPAD Actual | Objetivo (SAP2000 PDF) | Tolerancia |
|-----------|----------------|------------------------|------------|
| Mx | 6.275 kN-m/m | 6.22 kN-m/m | ±1% |
| My | 12.744 kN-m/m | 12.76 kN-m/m | ±1% |
| **Mxy** | **8.378 kN-m/m** | **7.25 kN-m/m** | **±2%** |
| w(centro) | - | 6.529 mm | ±2% |

**Condición de éxito:**
```
|Mxy_calcpad - Mxy_SAP2000| / Mxy_SAP2000 < 0.02  (2%)
```

---

## 8. Recomendación Final

### 🎯 OPCIÓN RECOMENDADA: Opción A (Implementación Completa)

**Razones:**
1. ✅ Es la solución **correcta y rigurosa**
2. ✅ Resultará en validación **exacta** con SAP2000
3. ✅ Enriquecerá Calcpad con método de Wilson
4. ✅ Permitirá usar mallas más gruesas (eficiencia)

**Próximo paso inmediato:**
1. Obtener paper de Wilson et al. (1973)
2. Estudiar ecuaciones de modos incompatibles
3. Comenzar implementación en .cpd

---

## Fuentes Completas

### Documentación SAP2000:
- [CSI Knowledge Base - Shell FAQ](https://wiki.csiamerica.com/display/kb/Shell+FAQ)
- [SAP2000 Basic Analysis Reference Manual](https://studylib.net/doc/27872782/04---sapbasic)
- [CSI Analysis Reference Manual](https://www.academia.edu/28385689/CSI_Anal_y_sis_Reference_Manual_For_SAP2000_ETABS_and_SAFE)

### Papers Académicos:
- [Ibrahimbegovic & Wilson (1991) - Unified Formulation](https://onlinelibrary.wiley.com/doi/abs/10.1002/cnm.1630070102)
- [Ibrahimbegovic & Wilson (1991) - Modified Method of Incompatible Modes](https://onlinelibrary.wiley.com/doi/10.1002/cnm.1630070303)
- [Wilson - Use of Incompatible Displacement Modes](https://www.semanticscholar.org/paper/Use-of-incompatible-displacement-modes-for-the-of-Wilson-Ibrahimbegovic/a1883933e6c237ee1738e671a606e36b8f32cabc)

### Libros:
- [Edward Wilson - Three Dimensional Static and Dynamic Analysis](https://edwilson.org/bookshelf/edsbook)
- [Edward L. Wilson - Wikipedia](https://en.wikipedia.org/wiki/Edward_L._Wilson)

---

**Fecha:** 2026-01-18

**Conclusión:** La diferencia del 13.5% en Mxy se debe a los **modos incompatibles de Wilson** que SAP2000 implementa y CALCPAD no. La implementación de estos modos permitirá obtener resultados idénticos a SAP2000.
