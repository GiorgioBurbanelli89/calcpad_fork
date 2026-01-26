# Comparación: Calcpad vs Mathcad Prime - Funcionalidades de Resolución

## Resumen Ejecutivo

Este documento compara las funcionalidades de resolución de ecuaciones entre **Calcpad 7.5.7** y **Mathcad Prime 11.0**, basado en el tutorial oficial de PTC.

---

## 1. Sistemas Lineales de Ecuaciones

### Mathcad Prime
| Método | Función | Descripción |
|--------|---------|-------------|
| Cálculo matricial | `X := M^(-1) · v` | Inversión de matriz |
| Solver directo | `lsolve(M, v)` | Función integrada |
| Bloque de resolución | `find(x, y)` con valores iniciales | Método iterativo |

### Calcpad ✅ IMPLEMENTADO
| Método | Función | Estado |
|--------|---------|--------|
| Cálculo matricial | `X = inverse(M)*v` | ✅ Disponible |
| Solver directo | `lsolve(M, v)` | ✅ Disponible |
| Solver complejo | `clsolve(M, v)` | ✅ Disponible |
| Solver múltiple | `msolve(M, B)` | ✅ Disponible |
| Solver iterativo | `slsolve(A, b, tol)` | ✅ Disponible |

---

## 2. Sistemas No Lineales de Ecuaciones

### Mathcad Prime
| Método | Función | Descripción |
|--------|---------|-------------|
| Bloque de resolución | `find(x, y, ...)` | Valores iniciales + restricciones |
| Búsqueda de raíces | `root(f(x), x, a, b)` | Encontrar x donde f(x)=0 |

### Calcpad ✅ PARCIALMENTE IMPLEMENTADO
| Método | Función | Estado |
|--------|---------|--------|
| $Find | `$Find{f(x) @ x = a : b}` | ✅ Encuentra máximo local |
| $Root | `$Root{f(x) @ x = a : b}` | ✅ Encuentra raíz f(x)=0 |
| $Root con ecuación | `$Root{f(x) = g(x) @ x = a : b}` | ✅ Encuentra x donde f(x)=g(x) |

**⚠️ FALTANTE**: Calcpad solo resuelve para **una variable**. No tiene soporte nativo para sistemas multivariable como `find(x, y)`.

---

## 3. Optimización

### Mathcad Prime
| Método | Función | Descripción |
|--------|---------|-------------|
| Minimizar | `minimize(f, x)` | Encuentra mínimo |
| Minimizar con restricciones | `minimize(f, x, ...)` en bloque | Con restricciones |
| Maximizar | `maximize(f, x)` | Encuentra máximo |

### Calcpad ✅ IMPLEMENTADO
| Método | Función | Estado |
|--------|---------|--------|
| Supremo (máximo) | `$Sup{f(x) @ x = a : b}` | ✅ Encuentra máximo en intervalo |
| Ínfimo (mínimo) | `$Inf{f(x) @ x = a : b}` | ✅ Encuentra mínimo en intervalo |

**⚠️ FALTANTE**: No hay soporte para optimización con restricciones (programación no lineal).

---

## 4. Ecuaciones Diferenciales Ordinarias (EDO)

### Mathcad Prime
| Método | Función | Descripción |
|--------|---------|-------------|
| ODE solver | `odesolve(f, t, t_end)` | Resuelve EDO |
| Rkadapt | `rkadapt(y, t0, t1, n, F)` | Runge-Kutta adaptativo |
| Radau | `radau(y, t0, t1, n, F)` | Método implícito |
| Bulstoer | `bulstoer(y, t0, t1, n, F)` | Bulirsch-Stoer |
| Bloque de resolución | `odesolve` en bloque | Notación natural |

### Calcpad ❌ NO IMPLEMENTADO
| Método | Estado |
|--------|--------|
| odesolve | ❌ No disponible |
| rkadapt | ❌ No disponible |
| Solvers de EDO | ❌ No disponible |

**🔴 CRÍTICO**: Calcpad **NO tiene soporte nativo para EDO**. Se requiere usar lenguajes externos (Python, Octave).

---

## 5. Cálculo (Derivadas e Integrales)

### Mathcad Prime
| Método | Función | Descripción |
|--------|---------|-------------|
| Derivada | `d/dx f(x)` | Derivada simbólica |
| Derivada numérica | Evaluación en punto | Aproximación numérica |
| Integral definida | `∫[a,b] f(x) dx` | Integración numérica |
| Jacobiano | `jacobian(F, x)` | Matriz de derivadas parciales |

### Calcpad ✅ IMPLEMENTADO
| Método | Función | Estado |
|--------|---------|--------|
| Derivada numérica | `$Derivative{f(x) @ x = a}` o `$Slope{...}` | ✅ En un punto |
| Integral definida | `$Integral{f(x) @ x = a : b}` | ✅ TanhSinh |
| Área (Lobatto) | `$Area{f(x) @ x = a : b}` | ✅ Adaptive Lobatto |

**⚠️ FALTANTE**: No hay cálculo simbólico de derivadas ni jacobiano automático.

---

## 6. Funciones Matriciales Avanzadas

### Comparación detallada:

| Función | Mathcad Prime | Calcpad | Estado |
|---------|---------------|---------|--------|
| Identidad | `identity(n)` | `identity(n)` | ✅ |
| Determinante | `det(M)` | `det(M)` | ✅ |
| Inversa | `M^(-1)` | `inverse(M)` | ✅ |
| Transpuesta | `M^T` | `transp(M)` | ✅ |
| Traza | `trace(M)` | `trace(M)` | ✅ |
| Eigenvalores | `eigenvals(M)` | `eigenvals(M, tol)` | ✅ |
| Eigenvectores | `eigenvecs(M)` | `eigenvecs(M, tol)` | ✅ |
| LU decomposition | `lu(M)` | `lu(M)` | ✅ |
| QR decomposition | `qr(M)` | `qr(M)` | ✅ |
| SVD | `svd(M)` | `svd(M)` | ✅ |
| Cholesky | `chol(M)` | `cholesky(M)` | ✅ |
| Rango | `rank(M)` | `rank(M)` | ✅ |
| Número de condición | `cond(M)` | `cond(M)`, `cond_1`, `cond_2`, `cond_e`, `cond_i` | ✅ |
| Norma | `norm(M)` | `mnorm`, `mnorm_1`, `mnorm_2`, `mnorm_e`, `mnorm_i` | ✅ |
| Resolver AX=B | `lsolve(A, B)` | `lsolve(A, B)`, `msolve(A, B)` | ✅ |
| FFT | `fft(v)` | `fft(v)` | ✅ |
| IFFT | `ifft(v)` | `ift(v)` | ✅ |

---

## 7. Iteración y Control de Flujo

### Mathcad Prime
| Estructura | Descripción |
|------------|-------------|
| for loop | `for i ∈ 1..n` |
| while loop | `while condition` |
| if/else | Condicionales |
| break/continue | Control de bucles |

### Calcpad ✅ IMPLEMENTADO
| Estructura | Sintaxis | Estado |
|------------|----------|--------|
| Suma | `$Sum{f(i) @ i = a : b}` | ✅ |
| Producto | `$Product{f(i) @ i = a : b}` | ✅ |
| Repeat | `$Repeat{expr @ i = a : b}` | ✅ |
| While | `$While{condition; body}` | ✅ |
| Inline block | `$Inline{expr1; expr2; ...}` | ✅ |
| Block | `$Block{expr1; expr2; ...}` | ✅ |
| Condicionales | `#if`, `#else`, `#end if` | ✅ |

---

## 8. Funcionalidades Faltantes en Calcpad

### 🔴 Críticas (Alta prioridad)
1. **odesolve** - Solver de ecuaciones diferenciales ordinarias
2. **find(x, y, ...)** - Sistemas no lineales multivariable
3. **minimize/maximize con restricciones** - Optimización con restricciones

### 🟡 Importantes (Media prioridad)
4. **jacobian(F, x)** - Cálculo automático del jacobiano
5. **Derivadas de orden superior** - d²f/dx², d³f/dx³
6. **genfit** - Ajuste de curvas no lineales
7. **linfit** - Ajuste de curvas lineales (mínimos cuadrados)

### 🟢 Deseables (Baja prioridad)
8. **Cálculo simbólico** - Derivadas e integrales simbólicas
9. **pdesolve** - Ecuaciones diferenciales parciales
10. **Animaciones** - Gráficas animadas

---

## 9. Ventajas de Calcpad sobre Mathcad Prime

| Característica | Calcpad | Mathcad Prime |
|----------------|---------|---------------|
| **Precio** | Gratuito/Open Source | Licencia costosa |
| **Multi-lenguaje** | Python, TypeScript, Octave, C#, Rust, Fortran | Solo Mathcad |
| **Alta precisión** | Matrices HP (High Precision) | Limitado |
| **Exportación** | HTML, DOCX, PDF | Limitado |
| **Personalización** | Código fuente disponible | Cerrado |
| **Interpolación** | take, line, spline, lookup | Similar |
| **Soporte de unidades** | Extensivo | Extensivo |

---

## 10. Recomendaciones de Implementación

### Fase 1: EDO Solver
```
$ODESolve{y' = f(t, y) @ y(t0) = y0 : t = t0 : t1}
```
- Implementar Runge-Kutta 4/5 (RK45)
- Soporte para sistemas de EDO
- Método adaptativo

### Fase 2: Sistemas No Lineales
```
$FindMulti{
  f1(x, y) = 0
  f2(x, y) = 0
  @ x = x0; y = y0
}
```
- Método de Newton-Raphson multivariable
- Cálculo automático del jacobiano

### Fase 3: Optimización con Restricciones
```
$Minimize{
  f(x, y)
  @ g1(x, y) <= 0
  @ g2(x, y) = 0
}
```
- Método de multiplicadores de Lagrange
- Penalización/Barrera

---

## Conclusión

Calcpad tiene **excelente soporte** para:
- ✅ Álgebra lineal y matrices
- ✅ Resolución de ecuaciones de una variable
- ✅ Integración numérica
- ✅ Derivadas numéricas
- ✅ Iteración y control de flujo

Calcpad **necesita mejorar** en:
- ❌ Ecuaciones diferenciales (crítico)
- ❌ Sistemas no lineales multivariable
- ❌ Optimización con restricciones

**Workaround actual**: Usar bloques `#columns` con Python/Octave para EDO y optimización avanzada.

---

## 11. Impacto en el Convertidor MCDX → Calcpad

Esta sección documenta cómo el convertidor debe manejar las funcionalidades de Mathcad Prime que no tienen equivalente directo en Calcpad.

### 11.1 Tabla de Conversión de Funciones

| Mathcad Prime | Calcpad Equivalente | Acción del Convertidor |
|---------------|---------------------|------------------------|
| `lsolve(M, v)` | `lsolve(M; v)` | ✅ Conversión directa (cambiar `,` por `;`) |
| `eigenvals(M)` | `eigenvals(M; 1e-10)` | ✅ Agregar tolerancia por defecto |
| `eigenvecs(M)` | `eigenvecs(M; 1e-10)` | ✅ Agregar tolerancia por defecto |
| `M^(-1)` | `inverse(M)` | ✅ Conversión directa |
| `M^T` | `transp(M)` | ✅ Conversión directa |
| `det(M)` | `det(M)` | ✅ Idéntico |
| `identity(n)` | `identity(n)` | ✅ Idéntico |
| `rank(M)` | `rank(M)` | ✅ Idéntico |
| `trace(M)` | `trace(M)` | ✅ Idéntico |
| `qr(M)` | `qr(M)` | ✅ Idéntico |
| `svd(M)` | `svd(M)` | ✅ Idéntico |
| `lu(M)` | `lu(M)` | ✅ Idéntico |
| `chol(M)` | `cholesky(M)` | ✅ Renombrar función |
| `fft(v)` | `fft(v)` | ✅ Idéntico |
| `ifft(v)` | `ift(v)` | ✅ Renombrar función |

### 11.2 Funciones que Requieren Workaround con Python

| Mathcad Prime | Workaround en Calcpad |
|---------------|----------------------|
| `odesolve(...)` | Generar bloque Python con `scipy.integrate.solve_ivp` |
| `rkadapt(...)` | Generar bloque Python con `scipy.integrate.RK45` |
| `radau(...)` | Generar bloque Python con `scipy.integrate.Radau` |
| `find(x, y, ...)` | Generar bloque Python con `scipy.optimize.fsolve` |
| `minimize(f, x, ...)` | Generar bloque Python con `scipy.optimize.minimize` |
| `maximize(f, x, ...)` | Generar bloque Python con `scipy.optimize.minimize` (negado) |
| `genfit(...)` | Generar bloque Python con `scipy.optimize.curve_fit` |
| `linfit(...)` | Generar bloque Python con `numpy.linalg.lstsq` |
| `jacobian(F, x)` | Generar bloque Python con cálculo numérico |

### 11.3 Bloques de Resolución (Solve Blocks)

#### Mathcad Prime Solve Block:
```
Given
  x := 1    ' valor inicial
  y := 1    ' valor inicial

  y1(x) = y2(x)    ' restricción 1
  y = y1(x)        ' restricción 2

find(x, y)
```

#### Conversión para Calcpad (Caso 1 variable):
```
' Bloque de resolución importado de Mathcad Prime
' Variable: x en intervalo [a, b]
$Root{y1(x) - y2(x) @ x = 0 : 10}
```

#### Conversión para Calcpad (Caso multivariable - Python):
```
#columns 1 python
from scipy.optimize import fsolve
import numpy as np

# Funciones importadas de Mathcad Prime
def y1(x): return (1/2.5)*(x - 7.5)
def y2(x): return -0.3*x + 1

# Sistema de ecuaciones
def equations(vars):
    x, y = vars
    eq1 = y1(x) - y2(x)
    eq2 = y - y1(x)
    return [eq1, eq2]

# Valores iniciales
x0, y0 = 1, 1

# Resolver
solution = fsolve(equations, [x0, y0])
print(f"x = {solution[0]:.6f}")
print(f"y = {solution[1]:.6f}")
#end columns
```

### 11.4 Conversión de ODESolve

#### Mathcad Prime:
```
Given
  M·x_a''(t) + K·x_a(t) = 0
  x_a(t0) = x0
  x_a'(t0) = v0

x_a := odesolve(t, 2·s)
```

#### Conversión para Calcpad (Python):
```
#columns 1 python
from scipy.integrate import solve_ivp
import numpy as np

# Parámetros del sistema (definidos arriba en Calcpad)
M = 3.877  # tonnef·s²/m
K = 1766.568  # tonnef/m
x0 = 0.05  # m (5 cm)
v0 = 0  # m/s

# Sistema en forma de estado-espacio: y = [x, x']
def sistema(t, y):
    x, v = y
    dxdt = v
    dvdt = -K/M * x
    return [dxdt, dvdt]

# Resolver
t_span = (0, 2)
t_eval = np.linspace(0, 2, 201)
sol = solve_ivp(sistema, t_span, [x0, v0], t_eval=t_eval)

# Resultados
t = sol.t
x_a = sol.y[0]  # posición
v_a = sol.y[1]  # velocidad
#end columns
```

### 11.5 Conversión de chartComponent con Derivadas

#### Mathcad Prime (XML):
```xml
<chartComponent>
  <math><ml:define>
    <ml:apply><ml:indexer/><ml:id>X</ml:id><ml:real>1</ml:real></ml:apply>
    <ml:id>t'</ml:id>
  </ml:define></math>
  <math><ml:define>
    <ml:apply><ml:indexer/><ml:id>Y</ml:id><ml:real>1</ml:real></ml:apply>
    <ml:apply><ml:div/>
      <ml:apply><ml:id>x_a</ml:id><ml:id>t'</ml:id></ml:apply>
      <ml:id>mm</ml:id>
    </ml:apply>
  </ml:define></math>
</chartComponent>
```

#### Conversión actual del McdxConverter:
```
' Series encontradas: 3
' Serie 1: X = t', Y = xa(t')/mm
' Serie 2: X = t', Y = xa'(t')/(cm/s²)  <- Primera derivada
' Serie 3: X = t', Y = xa''(t')/(m/s)   <- Segunda derivada

X[1] = t'
Y[1] = xa(t')/mm
X[2] = t'
Y[2] = xa'(t')/(cm/s^2)
X[3] = t'
Y[3] = xa''(t')/(m/s)
```

### 11.6 Operadores Especiales de Mathcad

| Operador Mathcad | XML | Calcpad | Notas |
|------------------|-----|---------|-------|
| `:=` (define) | `<ml:define>` | `=` | Asignación |
| `=` (evaluate) | `<ml:eval>` | `= ?` | Evaluación |
| `≡` (global define) | `<ml:globalDefine>` | `=` | Igual que define |
| `→` (symbolic eval) | `<ml:symbolic>` | ❌ | No soportado |
| `|` (such that) | `<ml:condition>` | ❌ | No soportado |
| `∑` (sum) | `<ml:sum>` | `$Sum{...}` | Convertir sintaxis |
| `∏` (product) | `<ml:product>` | `$Product{...}` | Convertir sintaxis |
| `∫` (integral) | `<ml:integral>` | `$Integral{...}` | Convertir sintaxis |
| `d/dx` (derivative) | `<ml:derivative>` | `$Derivative{...}` | Convertir sintaxis |

### 11.7 Código del Convertidor a Mejorar

#### Archivo: `Calcpad.Common/McdxConverter.cs`

##### Funciones implementadas ✅:
- `ProcessMathRegion()` - Regiones matemáticas
- `ProcessTextRegion()` - Regiones de texto
- `ProcessPlotRegion()` - Gráficas xyPlot
- `ProcessChartComponent()` - Gráficas chartComponent
- `ProcessPictureRegion()` - Imágenes
- `ProcessSolveBlock()` - Bloques de resolución (parcial)
- `ExtractExpression()` - Extracción de expresiones
- `ProcessApply()` - Operaciones matemáticas
- `functionDerivative` - Derivadas de funciones

##### Funciones por implementar ❌:
- `ConvertODESolve()` - Generar código Python para EDO
- `ConvertMultiVariableFind()` - Generar código Python para sistemas no lineales
- `ConvertOptimization()` - Generar código Python para optimización
- `ConvertSymbolic()` - Advertir que no hay soporte simbólico
- `ConvertJacobian()` - Generar cálculo numérico del jacobiano

### 11.8 Estrategia de Conversión Recomendada

```
┌─────────────────────────────────────────────────────────────┐
│                    MCDX Input                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Analizar tipo de elemento                       │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Soportado    │    │   Parcial     │    │ No Soportado  │
│  en Calcpad   │    │   Workaround  │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ Convertir     │    │ Generar       │    │ Comentario    │
│ directamente  │    │ código Python │    │ de advertencia│
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Calcpad Output (.cpd)                     │
└─────────────────────────────────────────────────────────────┘
```

### 11.9 Lista de Tareas para el Convertidor

- [x] Conversión básica de expresiones matemáticas
- [x] Conversión de matrices y vectores
- [x] Conversión de gráficas xyPlot
- [x] Conversión de chartComponent con derivadas
- [x] Manejo de unidades
- [x] Conversión de imágenes a Base64
- [ ] Conversión de ODESolve → Python
- [ ] Conversión de Find multivariable → Python
- [ ] Conversión de Minimize/Maximize → Python
- [ ] Advertencias para funciones no soportadas
- [ ] Manejo de cálculo simbólico (advertencia)
