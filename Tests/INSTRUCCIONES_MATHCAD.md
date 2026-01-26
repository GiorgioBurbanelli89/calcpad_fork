# Instrucciones para Verificar DLLs en Mathcad Prime 10

## Ubicación de las DLLs

Las DLLs deben estar instaladas en:
```
C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\
```

Archivos:
- `mathcad_fem.dll`
- `mathcad_triangle.dll`
- `mathcad_plate.dll`

## Script de Verificación para Mathcad

Copia y pega el siguiente código en Mathcad Prime 10:

---

### 1. VIGA 2D - Matriz de Rigidez

```
Parámetros de entrada:
E := 200000        (MPa)
A := 0.01          (m²)
I := 0.0001        (m⁴)
L := 5             (m)

Llamar a la función DLL:
K_beam := fem_beam_K(E, A, I, L)

Verificar elementos principales:
K_beam[0,0] =      (Esperado: 400 N/m)
K_beam[1,1] =      (Esperado: 1.92 N/m)
K_beam[2,2] =      (Esperado: 16 N·m/rad)
K_beam[3,3] =      (Esperado: 400 N/m)
K_beam[4,4] =      (Esperado: 1.92 N/m)
K_beam[5,5] =      (Esperado: 16 N·m/rad)
```

---

### 2. FRAME 3D - Matriz de Rigidez

```
Parámetros adicionales:
G := 80000         (MPa)
Iy := 0.0001       (m⁴)
Iz := 0.00008      (m⁴)
J := 0.00015       (m⁴)

Llamar a la función DLL:
K_frame := fem_frame3d_K(E, G, A, Iy, Iz, J, L)

Verificar elementos principales:
K_frame[0,0] =     (Esperado: 400 N/m)
K_frame[1,1] =     (Esperado: 1.536 N/m)
K_frame[2,2] =     (Esperado: 1.92 N/m)
K_frame[3,3] =     (Esperado: 2.4 N·m/rad)
K_frame[4,4] =     (Esperado: 16 N·m/rad)
K_frame[5,5] =     (Esperado: 12.8 N·m/rad)
```

---

### 3. VIGA EN VOLADIZO - Deflexión y Rotación

```
Carga:
P := 10000         (N)

Calcular deflexión:
δ := cantilever_defl(P, L, E, I)
δ =                (Esperado: 20833.33333 m)

Calcular rotación:
θ := cantilever_rot(P, L, E, I)
θ =                (Esperado: 6250 rad)
```

---

### 4. TRIÁNGULO - Nodos de Malla

```
Dimensiones de malla:
Lx := 6            (m)
Ly := 4            (m)
nx := 3            (nodos en X)
ny := 2            (nodos en Y)

Generar nodos:
nodes := tri_nodes(Lx, Ly, nx, ny)

Generar elementos:
elements := tri_elements(nx, ny)

Malla completa:
mesh := tri_rect_mesh(Lx, Ly, nx, ny)
```

---

### 5. TRIÁNGULO - Geometría

```
Coordenadas del triángulo:
x1 := 0            (m)
y1 := 0            (m)
x2 := 4            (m)
y2 := 0            (m)
x3 := 2            (m)
y3 := 3            (m)

Calcular área:
A_tri := tri_area(x1, y1, x2, y2, x3, y3)
A_tri =            (Esperado: 6 m²)

Calcular calidad:
Q := tri_quality(x1, y1, x2, y2, x3, y3)
Q =                (Esperado: ~0.5)

Calcular centroide:
centroid := tri_centroid(x1, y1, x2, y2, x3, y3)
centroid[0] =      (Esperado: 2 m)
centroid[1] =      (Esperado: 1 m)
```

---

### 6. PLACA MINDLIN - Matrices de Rigidez

```
Parámetros de placa:
E_plate := 30000   (MPa)
ν := 0.2
t := 0.15          (m)

Matriz de rigidez de flexión (9×9):
Kb := plate_Kb(x1, y1, x2, y2, x3, y3, E_plate, ν, t)

Matriz de rigidez de cortante (9×9):
Ks := plate_Ks(x1, y1, x2, y2, x3, y3, E_plate, ν, t)

Matriz de rigidez total (9×9):
K_plate := plate_K(x1, y1, x2, y2, x3, y3, E_plate, ν, t)
```

---

### 7. PLACA EMPOTRADA - Deflexión

```
Carga distribuida:
q := 10            (kN/m²)
a := 4             (m, lado de placa cuadrada)

Calcular deflexión máxima:
w_max := plate_defl(q, a, E_plate, ν, t)
w_max =            (Esperado: ~0.04 m)
```

---

## Comparación de Resultados

Una vez ejecutado el script en Mathcad:

1. Compara los valores obtenidos con los esperados (entre paréntesis)
2. Anota las diferencias en el archivo `COMPARACION_RESULTADOS.md`
3. Si hay diferencias significativas (>0.1%), verifica:
   - Unidades correctas
   - Orden de los parámetros
   - Implementación de las DLLs

## Tolerancia Aceptable

- Para valores enteros: diferencia < 0.001
- Para valores decimales: diferencia relativa < 0.1%

## Reporte de Errores

Si encuentras errores, reporta:
- Función que falla
- Parámetros de entrada
- Valor esperado vs valor obtenido
- Mensaje de error (si lo hay)
