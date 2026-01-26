# ANÁLISIS - Condiciones de Frontera (Boundary Conditions)

## Comparación Calcpad vs SAP2000

---

## CALCPAD - Rectangular Slab FEA.cpd (líneas 237-249)

### Código Calcpad:
```calcpad
k_s = 10^20
'Addition of supports
#for i = 1 : n_s
	j = k_1*(s_j.i - 1) + 1      # j apunta al DOF 1 (w)
	K.(j; j) = K.(j; j) + k_s    # Restringir w (desplazamiento vertical)
	j = j + 1                     # j apunta al DOF 2 (θx)
	#if y_j.s_j.i ≡ 0 ∨ y_j.s_j.i ≡ b    # Si y=0 o y=b
		K.(j; j) = K.(j; j) + k_s        # Restringir θx (rotación sobre eje X)
	#end if
	j = j + 1                     # j apunta al DOF 3 (θy)
	#if x_j.s_j.i ≡ 0 ∨ x_j.s_j.i ≡ a    # Si x=0 o x=a
		K.(j; j) = K.(j; j) + k_s        # Restringir θy (rotación sobre eje Y)
	#end if
#loop
```

### DOFs en Calcpad:
Para cada joint: `[w, θx, θy, ψ]`
- **w** = desplazamiento vertical
- **θx** = rotación alrededor del eje X
- **θy** = rotación alrededor del eje Y
- **ψ** = twist

### Restricciones:
1. **w (desplazamiento vertical)**: SIEMPRE restringido en todos los bordes
2. **θx (rotación sobre X)**: Restringido si `y = 0` o `y = b` (bordes paralelos a X)
3. **θy (rotación sobre Y)**: Restringido si `x = 0` o `x = a` (bordes paralelos a Y)

---

## SAP2000 - rectangular_slab_fea_sap2000.py (líneas 96-121)

### Código SAP2000 ACTUAL:
```python
support_count = 0
for i, j, name in point_names:
    is_x_border = (i == 0 or i == n_a)  # x=0 o x=a
    is_y_border = (j == 0 or j == n_b)  # y=0 o y=b

    if is_x_border or is_y_border:
        # U1, U2, U3, R1, R2, R3
        Restraint = [
            False,           # U1
            False,           # U2
            True,            # U3 - siempre restringido en bordes
            is_x_border,     # R1 - restringido si esta en x=0 o x=a
            is_y_border,     # R2 - restringido si esta en y=0 o y=b
            False            # R3
        ]
        SapModel.PointObj.SetRestraint(name, Restraint)
        support_count += 1
```

### DOFs en SAP2000:
- **U1** = desplazamiento en X
- **U2** = desplazamiento en Y
- **U3** = desplazamiento en Z (vertical) ← equivalente a `w`
- **R1** = rotación alrededor del eje X ← equivalente a `θx`
- **R2** = rotación alrededor del eje Y ← equivalente a `θy`
- **R3** = rotación alrededor del eje Z

### Restricciones ACTUALES:
1. **U3**: SIEMPRE restringido en todos los bordes ✅
2. **R1** (rotación sobre X): Restringido si `x = 0` o `x = a` ⚠️
3. **R2** (rotación sobre Y): Restringido si `y = 0` o `y = b` ⚠️

---

## ⚠️ PROBLEMA DETECTADO

### Comparación:

| Rotación | CALCPAD | SAP2000 ACTUAL | ¿Coincide? |
|----------|---------|----------------|------------|
| **θx / R1** (sobre eje X) | Si y=0 o y=b | Si x=0 o x=a | ❌ **NO** |
| **θy / R2** (sobre eje Y) | Si x=0 o x=a | Si y=0 o y=b | ❌ **NO** |

**Las condiciones están INVERTIDAS.**

---

## ✅ CORRECCIÓN NECESARIA

### Código CORRECTO:

```python
support_count = 0
for i, j, name in point_names:
    is_x_border = (i == 0 or i == n_a)  # x=0 o x=a
    is_y_border = (j == 0 or j == n_b)  # y=0 o y=b

    if is_x_border or is_y_border:
        # U1, U2, U3, R1, R2, R3
        Restraint = [
            False,           # U1
            False,           # U2
            True,            # U3 - siempre restringido en bordes
            is_y_border,     # R1 - restringido si esta en y=0 o y=b (como Calcpad)
            is_x_border,     # R2 - restringido si esta en x=0 o x=a (como Calcpad)
            False            # R3
        ]
        SapModel.PointObj.SetRestraint(name, Restraint)
        support_count += 1
```

### Cambios:
- **Línea 114**: `is_x_border` → `is_y_border` (R1 restringido si y=0 o y=b)
- **Línea 115**: `is_y_border` → `is_x_border` (R2 restringido si x=0 o x=a)

---

## LÓGICA FÍSICA

### ¿Por qué estas restricciones?

Para un apoyo simple en una placa:

1. **Borde paralelo al eje X** (y=0 o y=b):
   - La placa NO puede rotar sobre el eje X (perpendicular al borde)
   - Es decir, **θx = 0** o **R1 = 0**
   - La placa SÍ puede rotar sobre el eje Y (paralelo al borde)

2. **Borde paralelo al eje Y** (x=0 o x=a):
   - La placa NO puede rotar sobre el eje Y (perpendicular al borde)
   - Es decir, **θy = 0** o **R2 = 0**
   - La placa SÍ puede rotar sobre el eje X (paralelo al borde)

### Visualización:

```
      y
      ↑
      │
      b ●─────●─────●  ← Borde en y=b: R1 restringido (no rota sobre X)
      │ │     │     │
      │ │     │     │
      0 ●─────●─────● ─→ x
        0           a
        ↑
        Borde en x=0:
        R2 restringido
        (no rota sobre Y)
```

---

## CONCLUSIÓN

**El script SAP2000 tiene las condiciones de frontera INVERTIDAS.**

Para coincidir exactamente con Calcpad, necesitas:
- **R1 restringido** cuando **y = 0 o y = b**
- **R2 restringido** cuando **x = 0 o x = a**

Esto podría explicar parte de las diferencias en los resultados (especialmente en My).
