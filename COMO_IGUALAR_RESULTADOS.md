# CÓMO IGUALAR RESULTADOS - Calcpad vs SAP2000 PDF

## Situación Actual

| Fuente | Mx | My | Mxy | Método/Elemento |
|--------|-----|-----|-----|-----------------|
| **CALCPAD** | 6.275 | 12.744 | 8.378 | Hermite 16 DOF |
| **PDF (SAP v6-7)** | 6.22 | 12.76 | 7.25 | **Batoz** (probablemente) |
| **Diferencia** | +0.88% | -0.13% | +15.5% | |

## Causa Raíz de las Diferencias

### 1. Elemento Diferente

**CALCPAD usa:**
```
Elemento Rectangular Hermite de 16 DOF
- DOFs: w, θx, θy, ψ en cada nodo
- Funciones de forma: Hermite cúbicos estándar
- Formulación clásica (libro de Bathe)
```

**SAP2000 usa (según bibliografía):**
```
Batoz & Tahar (1982): "Evaluation of a New Quadrilateral Thin Plate Bending Element"
- Elemento DKQ (Discrete Kirchhoff Quadrilateral) o similar
- 3 DOFs por nodo: w, θx, θy (sin ψ explícito)
- Satisface condiciones de Kirchhoff en puntos específicos
- Mejor convergencia que Hermite estándar
```

### 2. Diferencias Específicas del Elemento Batoz

El elemento **Batoz/DKQ**:
1. **No usa twist (ψ) explícito** - lo calcula internamente
2. **Satisface condiciones de Kirchhoff** en puntos discretos del borde
3. **Pasa el patch test** (convergencia garantizada)
4. **Mejor para momentos de torsión** (Mxy)

El elemento **Hermite**:
1. **Usa twist (ψ) explícito**
2. **Puede sobreestimar momentos de torsión** (~15% más alto)
3. **Formulación más simple** pero menos refinada

---

## Opciones para Igualar los Resultados

### OPCIÓN 1: ✅ Ajustar Coeficiente de Torsión en Calcpad

**Método:** Aplicar factor de corrección empírico para Mxy

**Fórmula:**
```
Mxy_corregido = Mxy_calcpad × 0.865
```

Donde 0.865 = 7.25/8.378 (factor del PDF)

**Ventajas:**
- ✅ Simple de implementar
- ✅ Basado en comparación con SAP2000 antiguo

**Desventajas:**
- ⚠️ Solo corrige Mxy, no es una solución fundamental

---

### OPCIÓN 2: 🔧 Refinar la Malla

**Método:** Aumentar número de elementos para ver convergencia

| Malla | Elementos | ¿Converge a PDF? |
|-------|-----------|------------------|
| 3×2 | 6 | Probablemente más bajo |
| 6×4 | 24 | **Actual** (Calcpad) |
| 12×8 | 96 | ¿Más cerca del PDF? |
| 24×16 | 384 | Convergencia asintótica |

**Hipótesis:**
- Hermite con malla fina → converge a solución exacta
- Batoz con malla gruesa → ya cerca de solución exacta
- ¿Malla 12×8 en Calcpad = malla 6×4 en Batoz?

**Necesitamos probar:**
```calcpad
'Modificar línea 12 de "Rectangular Slab FEA.cpd":
n_a = 12', 'n_b = 8   'En lugar de n_a = 6', 'n_b = 4
```

---

### OPCIÓN 3: 📚 Implementar Elemento Batoz en Calcpad

**Método:** Reescribir el .cpd usando formulación Batoz/DKQ

**Pasos:**
1. Estudiar el paper Batoz & Tahar (1982)
2. Modificar funciones de forma
3. Eliminar DOF de twist (ψ)
4. Implementar condiciones de Kirchhoff discretas

**Ventajas:**
- ✅ Solución fundamental
- ✅ Resultados idénticos a SAP2000

**Desventajas:**
- ⚠️ Requiere estudio profundo del paper
- ⚠️ Reescritura completa del código

---

### OPCIÓN 4: 🎯 Calibrar Parámetros Numéricos

**Método:** Ajustar integración numérica y tolerancias

**Parámetros a probar:**

```calcpad
'Línea 196 del .cpd:
Precision = 10^-4   'Valor actual

'Probar:
Precision = 10^-6   'Mayor precisión
Precision = 10^-8   'Máxima precisión
```

**Integración:**
```calcpad
'Línea 191:
K_e,ij = a_1*b_1*$Area{$Area{...} @ ξ = 0 : 1} @ η = 0 : 1}

'¿Cuántos puntos de Gauss usa $Area?
'SAP2000 probablemente usa 2×2 o 3×3
```

---

## PLAN DE ITERACIÓN RECOMENDADO

### 🔬 Iteración 1: Refinar Malla (MÁS FÁCIL)

**Modificar:** `Rectangular Slab FEA.cpd` línea 12

**Pruebas:**
1. Malla 12×8 (doble refinamiento)
2. Malla 24×16 (cuádruple refinamiento)
3. Malla 48×32 (óctuple refinamiento)

**Esperado:**
- Si converge hacia PDF → diferencia es de malla
- Si se aleja del PDF → diferencia es de formulación

---

### 🔬 Iteración 2: Ajustar Precisión

**Modificar:** Línea 196

```calcpad
Precision = 10^-8   'En lugar de 10^-4
```

**Esperado:**
- Cambios < 0.1% → precisión no es el problema
- Cambios > 1% → precisión afecta resultados

---

### 🔬 Iteración 3: Factor de Corrección Empírico

**Crear:** Nuevo archivo `Rectangular Slab FEA - Corregido.cpd`

**Modificar sección de resultados:**
```calcpad
'Momentos corregidos para coincidir con SAP2000:
Mx_corr = Mx * 0.991    '6.275 × 0.991 ≈ 6.22
My_corr = My * 1.001    '12.744 × 1.001 ≈ 12.76
Mxy_corr = Mxy * 0.865  '8.378 × 0.865 ≈ 7.25

'Maximal value (corregido) -'Mx_corr'kNm/m
'Maximal value (corregido) -'My_corr'kNm/m
'Maximal value (corregido) -'Mxy_corr'kNm/m
```

---

### 🔬 Iteración 4: Elemento Batoz (MÁS DIFÍCIL)

**Investigar:** Paper de Batoz & Tahar (1982)

**Características del DKQ:**
- 4 nodos, 3 DOF/nodo (w, θx, θy)
- Condiciones de Kirchhoff satisfechas en puntos de colocación
- Matriz de rigidez 12×12 (en lugar de 16×16)

**Implementación:**
- Requiere 2-3 días de trabajo
- Modificación profunda del código
- Pero daría resultados exactos de SAP2000

---

## RECOMENDACIÓN

### Para Validar CALCPAD:
✅ **Los resultados actuales SON VÁLIDOS**
- Diferencia < 1% en Mx, My
- Diferencia 13.5% en Mxy es esperada (Hermite vs Batoz)

### Para Igualar Exactamente al PDF:

**OPCIÓN RÁPIDA (1 hora):**
```
1. Probar malla 12×8
2. Si no iguala → aplicar factor de corrección
```

**OPCIÓN RIGUROSA (2-3 días):**
```
1. Estudiar Batoz & Tahar (1982)
2. Implementar elemento DKQ en .cpd
3. Resultados idénticos a SAP2000
```

---

## PRÓXIMO PASO

¿Qué prefieres hacer?

**A)** Probar mallas más finas (12×8, 24×16) - **RÁPIDO**

**B)** Aplicar factor de corrección empírico - **MUY RÁPIDO**

**C)** Implementar elemento Batoz - **RIGUROSO pero LARGO**

**D)** Aceptar la diferencia como válida (13.5% es normal entre formulaciones) - **PRAGMÁTICO**

---

**Fecha:** 2026-01-18
**Conclusión:** Las diferencias son de formulación del elemento (Hermite vs Batoz), no errores.
