# Comparación de Análisis: Calcpad vs SAP2000

## Modelo Analizado: Losa Rectangular 6m x 4m

### Datos del Problema

| Parámetro | Valor |
|-----------|-------|
| Dimensiones | a = 6 m, b = 4 m |
| Espesor | t = 0.1 m |
| Carga uniformemente distribuida | q = 10 kN/m² |
| Módulo de elasticidad | E = 35,000 MPa |
| Coeficiente de Poisson | ν = 0.15 |
| Condiciones de apoyo | Simplemente apoyada en los cuatro bordes |

### Discretización de la Malla

| Software | Elementos en dirección a | Elementos en dirección b | Total Elementos | Total Nodos |
|----------|-------------------------|-------------------------|-----------------|-------------|
| Calcpad  | 6 | 4 | 24 | 35 |
| SAP2000  | 6 | 4 | 24 | 35 |

### Archivos

- **Calcpad**: `Rectangular Slab FEA.cpd`
- **SAP2000**: `Plate-6x4.s2k`

### Teoría de Elementos Finitos

Ambos modelos utilizan:
- **Tipo de elemento**: Placa rectangular de Mindlin (con 16 DOF: 4 nodos × 4 DOF/nodo)
- **Grados de libertad por nodo**:
  - w (desplazamiento vertical)
  - θₓ (rotación alrededor de x)
  - θᵧ (rotación alrededor de y)
  - ψ (twist/torsión)

### Matriz Constitutiva

```
D = E·t³ / (12(1-ν²)) × [1   ν   0  ]
                        [ν   1   0  ]
                        [0   0 (1-ν)/2]
```

Con los valores dados:
```
D = 35000 × 0.1³ / (12(1-0.15²)) × [matriz]
D = 35000 × 0.001 / (12 × 0.9775) × [matriz]
D ≈ 2.98 × [matriz]
```

### Resultados Esperados

#### Punto Central (x = a/2 = 3m, y = b/2 = 2m)

| Resultado | Calcpad | SAP2000 | Diferencia |
|-----------|---------|---------|------------|
| Desplazamiento vertical w (mm) | _Por calcular_ | _Por ejecutar_ | - |
| Momento Mₓ (kN·m/m) | _Por calcular_ | _Por ejecutar_ | - |
| Momento Mᵧ (kN·m/m) | _Por calcular_ | _Por ejecutar_ | - |
| Momento Mₓᵧ (kN·m/m) | _Por calcular_ | _Por ejecutar_ | - |

### Notas Técnicas

1. **SAP2000 API**:
   - Archivo de documentación: `CSI_OAPI_Documentation.chm`
   - Versión utilizada: SAP2000 v25
   - Unidades: kN-m-C

2. **Calcpad**:
   - Versión: 7.5.7
   - Método de integración numérica para matriz de rigidez
   - Solver: Cholesky para sistemas simétricos

3. **Diferencias Potenciales**:
   - Precisión numérica en la integración
   - Métodos de solución del sistema de ecuaciones
   - Tratamiento de condiciones de borde

### Próximos Pasos

1. ✅ Revisar documentación de SAP2000 API
2. ✅ Crear script para ejecutar modelo en SAP2000
3. ⏳ Compilar y ejecutar script de SAP2000
4. ⏳ Extraer resultados de SAP2000
5. ⏳ Ejecutar análisis en Calcpad
6. ⏳ Comparar resultados numéricos
7. ⏳ Validar precisión de Calcpad

### Referencias

- Calcpad Examples: `C:\Users\j-b-j\Documents\Calcpad\Examples\Mechanics\Finite Elements\`
- SAP2000 Model: `Plate-6x4.s2k`
- API Documentation: `CSI_OAPI_Documentation.chm`
