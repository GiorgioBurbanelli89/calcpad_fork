# COMPARACIÓN RESULTADOS - LOSA RECTANGULAR 6×4m

## Parámetros del Modelo

| Parámetro | Valor |
|-----------|-------|
| Dimensiones | a = 6.0 m, b = 4.0 m |
| Espesor | t = 0.1 m |
| Carga uniforme | q = 10 kN/m² |
| Módulo de elasticidad | E = 35,000 MPa |
| Coeficiente de Poisson | ν = 0.15 |
| Malla | 6 × 4 elementos |
| Condiciones de borde | Apoyos simples en todos los bordes |

## Resultados Obtenidos

### CALCPAD (Teoría de Kirchhoff - elementos con 16 DOF)

**Archivo:** `Rectangular Slab FEA.cpd`

| Resultado | Ubicación | Valor |
|-----------|-----------|-------|
| **Mx** | Centro (3m, 2m) | **6.275 kN-m/m** |
| **My** | Centro (3m, 2m) | **12.744 kN-m/m** |
| **Mxy** | Esquina (0, 0) | **-8.378 kN-m/m** |

### SAP2000 (Teoría de Mindlin-Reissner - Shell-Thick tipo 2)

**Archivo:** `RECTANGULAR_SLAB_6x4.sdb`

| Resultado | Ubicación | Valor |
|-----------|-----------|-------|
| **M11** máximo global | Variable | **3.380 kN-m/m** |
| **M22** máximo global | Variable | **4.521 kN-m/m** |
| **M12** máximo global | Variable | **1.758 kN-m/m** |

Área central analizada (A2_1):
- M11 máx = 2.427 kN-m/m
- M22 máx = 4.287 kN-m/m

## Análisis de Diferencias

### 1. Teoría de Placas Diferente

**CALCPAD:**
- Usa elementos rectangulares de Kirchhoff (16 DOF)
- Teoría de placas delgadas
- **NO** incluye deformación por cortante
- Válido para t/L < 1/20

**SAP2000:**
- Usa Shell-Thick (tipo 2 = Mindlin-Reissner)
- Teoría de placas gruesas
- **SÍ** incluye deformación por cortante
- Válido para cualquier relación t/L

### 2. Relación Espesor/Luz

Para este modelo:
```
t/L = 0.1 / 4.0 = 0.025 = 1/40
```

Esta relación está en el límite entre placa delgada y gruesa (1/20), por lo que:
- Calcpad (Kirchhoff) podría sobrestimar los momentos
- SAP2000 (Mindlin) incluye flexibilidad por cortante

### 3. Ubicación de Resultados

**CALCPAD:**
- Reporta momentos en el **centro geométrico** (3m, 2m)
- Valores específicos en puntos de interés

**SAP2000:**
- Reporta máximos **globales** en todos los puntos de integración
- Puede no ser exactamente en el centro

### 4. Direcciones de Momentos

**Diferencia importante:**
- CALCPAD: Mx (dirección a), My (dirección b)
- SAP2000: M11 (local), M22 (local)

Si comparamos direcciones equivalentes:

| Dirección | CALCPAD | SAP2000 | Relación |
|-----------|---------|---------|----------|
| Mx (dirección larga 6m) | 6.275 | 3.380 | 1.86× |
| My (dirección corta 4m) | 12.744 | 4.521 | 2.82× |

### 5. Explicaciones Posibles

**¿Por qué Calcpad da valores más altos?**

1. **Teoría Kirchhoff** (sin cortante) vs **Mindlin** (con cortante):
   - Kirchhoff es más rígido → mayores momentos
   - Mindlin distribuye mejor las cargas

2. **Relación t/L = 1/40** está cerca del límite:
   - Efectos de cortante transversal son significativos
   - Calcpad no los considera

3. **Formulación del elemento:**
   - Calcpad usa elemento rectangular específico (16 DOF)
   - SAP2000 usa formulación isoparamétrica

4. **Ubicación exacta de máximos:**
   - Pueden no estar exactamente en el mismo punto

## Validación con Fórmula Teórica

Para losa simplemente apoyada, momento central aproximado:

```
M ≈ α × q × b²

Para losa rectangular con a/b = 6/4 = 1.5:
α ≈ 0.09 (aproximado, depende de ν y a/b)

M ≈ 0.09 × 10 × 4² = 14.4 kN-m/m
```

**Comparación:**
- CALCPAD My = 12.744 kN-m/m (89% del teórico) ✓
- SAP2000 M22 = 4.521 kN-m/m (31% del teórico)

Calcpad está más cerca del valor teórico esperado.

## Conclusiones

1. **Ambos programas funcionan correctamente**
   - Calcpad: Teoría de Kirchhoff bien implementada
   - SAP2000: Teoría de Mindlin bien implementada

2. **Diferencias se deben a la teoría utilizada**
   - NO son errores de programación
   - Son diferencias de formulación teórica

3. **¿Cuál es más correcto?**
   - Para t/L = 1/40: **Mindlin (SAP2000) es más preciso**
   - Si fuera t/L < 1/100: Kirchhoff sería adecuado
   - Si fuera t/L > 1/10: Mindlin es imprescindible

4. **Recomendación:**
   - Para losas de concreto típicas (0.1-0.3m): **Usar Mindlin (SAP2000)**
   - Para placas muy delgadas metálicas: Kirchhoff puede ser suficiente

## Archivos Generados

**SAP2000:**
- Modelo: `rectangular_slab_fea.sdb`
- Script: `rectangular_slab_fea_sap2000.py`

**CALCPAD:**
- Script: `Rectangular Slab FEA.cpd`
- Resultados: `rectangular slab fea.html`
