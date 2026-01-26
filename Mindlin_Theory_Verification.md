# Verificación de la Teoría de Placas Mindlin en Calcpad
## Comparación con Reddy (2006) - Theory and Analysis of Elastic Plates and Shells

### 1. Campo de Desplazamientos (Cinemática)

**Reddy (2006) Eq. 10.1.1:**
```
u(x,y,z,t) = u₀(x,y,t) + z·φₓ(x,y,t)
v(x,y,z,t) = v₀(x,y,t) + z·φᵧ(x,y,t)
w(x,y,z,t) = w₀(x,y,t)
```

**Calcpad:** El elemento Q4-Mindlin tiene 3 GDL por nodo: w, θₓ, θᵧ
- ✅ Correcto: Se usan rotaciones independientes (φₓ, φᵧ en Reddy = θₓ, θᵧ en Calcpad)

### 2. Deformaciones de Cortante Transversal

**Reddy (2006) Eq. 10.1.4:**
```
γₓz = ∂w₀/∂x + φₓ
γᵧz = ∂w₀/∂y + φᵧ
```

**Calcpad (matriz B_s):**
```
B_s.(1; col) = dNx       → ∂w/∂x
B_s.(1; col + 1) = Ni    → φₓ (= θₓ)
B_s.(2; col) = dNy       → ∂w/∂y
B_s.(2; col + 2) = Ni    → φᵧ (= θᵧ)
```
- ✅ Correcto: γ = B_s × u = {∂w/∂x + θₓ, ∂w/∂y + θᵧ}

### 3. Curvaturas (Flexión)

**Reddy (2006) Eq. 10.1.5b (ε¹):**
```
κₓₓ = ∂φₓ/∂x
κᵧᵧ = ∂φᵧ/∂y
κₓᵧ = ∂φₓ/∂y + ∂φᵧ/∂x
```

**Calcpad (matriz B_b):**
```
B_b.(1; col + 1) = dNx   → ∂θₓ/∂x
B_b.(2; col + 2) = dNy   → ∂θᵧ/∂y
B_b.(3; col + 1) = dNy   → ∂θₓ/∂y
B_b.(3; col + 2) = dNx   → ∂θᵧ/∂x
```
- ✅ Correcto: κ = B_b × θ = {∂θₓ/∂x, ∂θᵧ/∂y, ∂θₓ/∂y + ∂θᵧ/∂x}

### 4. Factor de Corrección por Cortante

**Reddy (2006) Eq. 10.1.11-13:**
El factor de corrección κₛ = 5/6 se usa para compensar la distribución parabólica
real del esfuerzo cortante vs. la distribución constante asumida en FSDT.

**Calcpad:**
```
κ = 5/6
D_s = κ*G*t*[1; 0|0; 1]
```
- ✅ Correcto: Usa κ = 5/6 para secciones rectangulares homogéneas

### 5. Matrices Constitutivas

**Flexión:**
```
D_b = E·t³/(12(1-ν²)) × [1    ν    0  ]
                        [ν    1    0  ]
                        [0    0  (1-ν)/2]
```

**Cortante:**
```
D_s = κ·G·t × [1  0]
              [0  1]
donde G = E/(2(1+ν))
```
- ✅ Correcto en Calcpad

### 6. Integración Selectiva (Evitar Shear Locking)

**Teoría:** Para evitar el "shear locking" en elementos Q4 de placa gruesa:
- Flexión: Integración completa (2×2 Gauss)
- Cortante: Integración reducida (1×1 Gauss en el centro)

**Calcpad:**
```
'Integración 2×2 para flexión
#for gp_ξ = 1 : 2
    #for gp_η = 1 : 2
        ...
        K_b = transp(B_b)*D_b*B_b*detJ*w_2*w_2
        K_e = K_e + K_b

'Integración 1×1 para cortante
ξ = 0
η = 0
...
K_s = transp(B_s)*D_s*B_s*detJ*4   (peso total = 2×2 = 4)
```
- ✅ Correcto: Usa integración selectiva

### 7. Comparación de Resultados

**Calcpad reporta:**
- Deflexión máxima: w = 0.073 mm
- Momento en centro: Mx = My ≈ 6.67 kNm/m
- Ratio Mindlin/Kirchhoff: ~1.17

**Esperado (Reddy Table 10.4.1 para a/h = 10, placa cuadrada SS):**
- Para placas con a/h = 10, FSDT da deflexiones ~15-20% mayores que CPT
- ✅ El ratio 1.17 es consistente con la teoría

### 8. Conclusión

La implementación en Calcpad es **CORRECTA** y consistente con:
1. La cinemática FSDT de Reddy (2006)
2. Las matrices constitutivas para placas isotrópicas
3. El factor de corrección por cortante κ = 5/6
4. La integración selectiva para evitar shear locking
5. Los resultados esperados para placas moderadamente gruesas (a/h = 10)

El único detalle menor es la convención de signos para las rotaciones, pero esto
es consistente internamente en el código y produce resultados correctos.
