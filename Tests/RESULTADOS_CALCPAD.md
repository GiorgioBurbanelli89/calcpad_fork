# Resultados de Calcpad - Funciones FEM

Estos son los valores calculados por Calcpad para comparar con las DLLs de Mathcad.

## 1. Matriz de Rigidez de Viga 2D

**Parámetros:**
- E = 200000 MPa
- A = 0.01 m²
- I = 0.0001 m⁴
- L = 5 m

**Resultados:**
| Elemento | Valor | Unidades |
|----------|-------|----------|
| k[0,0] = EA/L | 400 | N/m |
| k[1,1] = 12EI/L³ | 1.92 | N/m |
| k[2,2] = 4EI/L | 16 | N·m/rad |
| k[3,3] = EA/L | 400 | N/m |
| k[4,4] = 12EI/L³ | 1.92 | N/m |
| k[5,5] = 4EI/L | 16 | N·m/rad |

## 2. Matriz de Rigidez de Frame 3D

**Parámetros adicionales:**
- G = 80000 MPa
- Iy = 0.0001 m⁴
- Iz = 0.00008 m⁴
- J = 0.00015 m⁴

**Resultados:**
| Elemento | Valor | Unidades |
|----------|-------|----------|
| k3d[0,0] = EA/L | 400 | N/m |
| k3d[1,1] = 12EIz/L³ | 1.536 | N/m |
| k3d[2,2] = 12EIy/L³ | 1.92 | N/m |
| k3d[3,3] = GJ/L | 2.4 | N·m/rad |
| k3d[4,4] = 4EIy/L | 16 | N·m/rad |
| k3d[5,5] = 4EIz/L | 12.8 | N·m/rad |

## 3. Viga en Voladizo

**Parámetros:**
- P = 10000 N
- L = 5 m
- E = 200000 MPa
- I = 0.0001 m⁴

**Resultados:**
| Variable | Valor | Unidades |
|----------|-------|----------|
| Deflexión (δ) | 20833.33333 | m |
| Rotación (θ) | 6250 | rad |

## 4. Triángulo - Geometría

**Coordenadas:**
- (x1, y1) = (0, 0)
- (x2, y2) = (4, 0)
- (x3, y3) = (2, 3)

**Resultados:**
| Variable | Valor | Unidades |
|----------|-------|----------|
| Área | 6 | m² |
| Lado a | 4 | m |
| Lado b | 3.60555 | m |
| Lado c | 3.60555 | m |
| Calidad (r_in/r_out) | ~0.5 | - |
| Centroide x | 2 | m |
| Centroide y | 1 | m |

## 5. Placa Mindlin

**Parámetros:**
- E = 30000 MPa
- ν = 0.2
- t = 0.15 m

**Resultados:**
| Variable | Valor | Unidades |
|----------|-------|----------|
| Rigidez D | 8789.0625 | N·m |
| Módulo G | 12500 | MPa |

## 6. Deflexión de Placa Empotrada

**Parámetros:**
- q = 10 kN/m²
- a = 4 m (lado)
- E = 30000 MPa
- ν = 0.2
- t = 0.15 m

**Resultados:**
| Variable | Valor | Unidades |
|----------|-------|----------|
| w_max | ~0.04 | m |

---

**Nota:** Estos valores deben coincidir con los resultados de las funciones DLL de Mathcad:
- `fem_beam_K(200000, 0.01, 0.0001, 5)`
- `fem_frame3d_K(200000, 80000, 0.01, 0.0001, 0.00008, 0.00015, 5)`
- `cantilever_defl(10000, 5, 200000, 0.0001)`
- `cantilever_rot(10000, 5, 200000, 0.0001)`
- `tri_area(0, 0, 4, 0, 2, 3)`
- `tri_quality(0, 0, 4, 0, 2, 3)`
- `tri_centroid(0, 0, 4, 0, 2, 3)`
