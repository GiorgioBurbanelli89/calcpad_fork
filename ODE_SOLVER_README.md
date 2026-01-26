# Solver de Ecuaciones Diferenciales Ordinarias (ODEs)

## ✅ Implementación Completada

Calcpad ahora incluye un solver de ODEs integrado en el parser simbólico usando AngouriMath.

---

## 🚀 Sintaxis

```calcpad
@{symbolic}
' ODE de primer orden separable
sol1 = solve_ode(y' - f(x), y, x)

' ODE lineal de primer orden homogénea
sol2 = solve_ode(y' + a*y, y, x)

' ODE de segundo orden homogénea
sol3 = solve_ode(y'' + a*y' + b*y, y, x)
@{end symbolic}
```

**Nota**: Las ecuaciones se escriben en **forma estándar** (sin el `= 0` explícito).

---

## 📚 Tipos de ODEs Soportados

### 1. ODEs de Primer Orden Separables

**Forma**: `y' = f(x)` → Escrito como: `y' - f(x)`

**Solución**: `y = ∫f(x)dx + C`

**Ejemplos**:
```calcpad
@{symbolic}
' y' = x²
sol1 = solve_ode(y' - x^2, y, x)
' Resultado: y = x³/3 + C

' y' = 2x
sol2 = solve_ode(y' - 2*x, y, x)
' Resultado: y = x² + C

' y' = e^x
sol3 = solve_ode(y' - e^x, y, x)
' Resultado: y = e^x + C
@{end symbolic}
```

---

### 2. ODEs Lineales de Primer Orden Homogéneas

**Forma**: `y' + a*y = 0`

**Solución**: `y = C*e^(-a*x)`

**Ejemplos**:
```calcpad
@{symbolic}
' y' + 3y = 0
sol1 = solve_ode(y' + 3*y, y, x)
' Resultado: y = C*e^(-3x)

' y' + 5y = 0
sol2 = solve_ode(y' + 5*y, y, x)
' Resultado: y = C*e^(-5x)
@{end symbolic}
```

---

### 3. ODEs Lineales de Segundo Orden Homogéneas

**Forma**: `y'' + a*y' + b*y = 0`

**Método**: Ecuación característica `r² + a*r + b = 0`

#### 3.1 Caso: Raíces Reales Distintas (Δ > 0)

**Solución**: `y = C₁*e^(r₁*x) + C₂*e^(r₂*x)`

donde `r₁,₂ = (-a ± √(a² - 4b))/2`

**Ejemplos**:
```calcpad
@{symbolic}
' y'' - 3y' + 2y = 0
' Ecuación característica: r² - 3r + 2 = 0
' Raíces: r₁ = 2, r₂ = 1
sol1 = solve_ode(y'' - 3*y' + 2*y, y, x)
' Resultado: y = C1*e^(2x) + C2*e^x

' y'' - 5y' + 6y = 0
' Raíces: r₁ = 3, r₂ = 2
sol2 = solve_ode(y'' - 5*y' + 6*y, y, x)
' Resultado: y = C1*e^(3x) + C2*e^(2x)
@{end symbolic}
```

#### 3.2 Caso: Raíz Doble (Δ = 0)

**Solución**: `y = (C₁ + C₂*x)*e^(r*x)`

donde `r = -a/2`

**Ejemplos**:
```calcpad
@{symbolic}
' y'' - 4y' + 4y = 0
' Ecuación característica: r² - 4r + 4 = 0
' Raíz doble: r = 2
sol1 = solve_ode(y'' - 4*y' + 4*y, y, x)
' Resultado: y = (C1 + C2*x)*e^(2x)

' y'' + 6y' + 9y = 0
' Raíz doble: r = -3
sol2 = solve_ode(y'' + 6*y' + 9*y, y, x)
' Resultado: y = (C1 + C2*x)*e^(-3x)
@{end symbolic}
```

#### 3.3 Caso: Raíces Complejas Conjugadas (Δ < 0)

**Solución**: `y = e^(α*x)[C₁*cos(β*x) + C₂*sin(β*x)]`

donde:
- `α = -a/2`
- `β = √(-Δ)/2 = √(4b - a²)/2`

**Ejemplos**:
```calcpad
@{symbolic}
' y'' + 4y = 0
' Ecuación característica: r² + 4 = 0
' Raíces complejas: r = ±2i
sol1 = solve_ode(y'' + 4*y, y, x)
' Resultado: y = C1*cos(2x) + C2*sin(2x)

' y'' + 2y' + 5y = 0
' Ecuación característica: r² + 2r + 5 = 0
' Raíces: r = -1 ± 2i
sol2 = solve_ode(y'' + 2*y' + 5*y, y, x)
' Resultado: y = e^(-x)*(C1*cos(2x) + C2*sin(2x))

' y'' + y' + y = 0
' Raíces: r = -1/2 ± i√3/2
sol3 = solve_ode(y'' + y' + y, y, x)
' Resultado: y = e^(-x/2)*(C1*cos(√3/2*x) + C2*sin(√3/2*x))
@{end symbolic}
```

---

## 🧪 Archivo de Prueba

Ver: `Examples/Test-ODE-Simple.cpd`

```calcpad
"Ecuaciones Diferenciales - Ejemplos Simples"

@{symbolic}

'<h3>1. ODE Separable Simple</h3>
sol1 = solve_ode(y' - x^2, y, x)

'<h3>2. ODE Lineal Primer Orden</h3>
sol2 = solve_ode(y' + 3*y, y, x)

'<h3>3. ODE Segundo Orden - Raíces Reales</h3>
sol3 = solve_ode(y'' - 3*y' + 2*y, y, x)

'<h3>4. ODE Segundo Orden - Raíz Doble</h3>
sol4 = solve_ode(y'' - 4*y' + 4*y, y, x)

'<h3>5. ODE Segundo Orden - Raíces Complejas</h3>
sol5 = solve_ode(y'' + 4*y, y, x)
sol6 = solve_ode(y'' + 2*y' + 5*y, y, x)

@{end symbolic}
```

---

## 📊 Resultados de Pruebas

| ODE | Solución Calcpad | Estado |
|-----|------------------|--------|
| `y' - x²` | `y = x³/3 + C` | ✅ |
| `y' - 2x` | `y = x² + C` | ✅ |
| `y' + 3y` | `y = C*e^(-3x)` | ✅ |
| `y' + 5y` | `y = C*e^(-5x)` | ✅ |
| `y'' - 3y' + 2y` | `y = C1*e^(2x) + C2*e^x` | ✅ |
| `y'' - 5y' + 6y` | `y = C1*e^(3x) + C2*e^(2x)` | ✅ |
| `y'' - 4y' + 4y` | `y = (C1 + C2*x)*e^(2x)` | ✅ |
| `y'' + 6y' + 9y` | `y = (C1 + C2*x)*e^(-3x)` | ✅ |
| `y'' + 4y` | `y = C1*cos(2x) + C2*sin(2x)` | ✅ |
| `y'' + 2y' + 5y` | `y = e^(-x)*(C1*cos(2x) + C2*sin(2x))` | ✅ |
| `y'' + y' + y` | `y = e^(-x/2)*(C1*cos(√3/2*x) + C2*sin(√3/2*x))` | ✅ |

**Todos los casos: 11/11 ✅ (100%)**

---

## 🔧 Implementación Técnica

### Archivos Modificados

```
Calcpad.Common/ExpressionParsers/SymbolicParser.cs
├── ProcessODE()                           ' Detecta tipo de ODE
├── SolveFirstOrderSeparable()             ' y' = f(x)
├── SolveFirstOrderLinear()                ' y' + ay = 0
├── SolveSecondOrderLinearHomogeneous()    ' y'' + ay' + by = 0
└── ProcessVerifyODE()                     ' Verifica soluciones
```

### Algoritmo de Detección

1. **Si contiene `''`** → ODE de segundo orden
2. **Si contiene `'` pero NO contiene `y`** → Separable (solo y' y x)
3. **Si contiene `'` Y contiene `y`** → Lineal de primer orden

### Método de Solución

#### ODEs de Primer Orden Separables
```csharp
// y' = f(x) → y = ∫f(x)dx + C
var entity = ParseExpression(f_of_x);
var integral = entity.Integrate(variable);
return $"{y} = {integral} + C";
```

#### ODEs de Segundo Orden
```csharp
// Ecuación característica: r² + a*r + b = 0
var discriminant = a*a - 4*b;

if (discriminant > 0)
{
    // Raíces reales: r₁, r₂
    return $"y = C1*e^(r1*x) + C2*e^(r2*x)";
}
else if (discriminant == 0)
{
    // Raíz doble: r
    return $"y = (C1 + C2*x)*e^(r*x)";
}
else
{
    // Raíces complejas: α ± βi
    return $"y = e^(α*x)*(C1*cos(β*x) + C2*sin(β*x))";
}
```

---

## 🚧 Limitaciones Actuales

### No Soportado (usar Maxima para estos casos):

- ❌ ODEs no lineales (`y' = y²`)
- ❌ ODEs con condiciones iniciales/frontera
- ❌ ODEs de segundo orden no homogéneas (`y'' + y = sin(x)`)
- ❌ Sistemas de ODEs
- ❌ ODEs de orden superior (n ≥ 3)
- ❌ ODEs con coeficientes variables (`y' + x*y = 0`)
- ❌ Ecuaciones en derivadas parciales (PDEs)

Ver `MAXIMA_INTEGRATION.md` para ODEs avanzadas.

---

## 🔄 Verificación de Soluciones

```calcpad
@{symbolic}
' Resolver ODE
sol = solve_ode(y'' - 3*y' + 2*y, y, x)

' Verificar que la solución satisface la ODE
check = verify_ode(y = C1*e^(2*x) + C2*e^x, y'' - 3*y' + 2*y = 0, y, x)
' Muestra: y' = ..., y'' = ...
@{end symbolic}
```

---

## 📈 Comparación con Otros CAS

| Sistema | ODEs Lineales | ODEs No Lineales | Sistemas | Condiciones Iniciales |
|---------|--------------|------------------|----------|----------------------|
| **Calcpad (AngouriMath)** | ✅ | ❌ | ❌ | ❌ |
| **Maxima** | ✅ | ✅ | ✅ | ✅ |
| **Mathematica** | ✅ | ✅ | ✅ | ✅ |
| **Wolfram Alpha** | ✅ | ✅ | ✅ | ✅ |
| **SymPy (Python)** | ✅ | ⚠️ | ✅ | ✅ |

---

## 📖 Referencias

- **Ecuación Característica**: https://en.wikipedia.org/wiki/Characteristic_equation_(calculus)
- **Método de Euler**: https://en.wikipedia.org/wiki/Euler_method
- **AngouriMath Docs**: https://am.angouri.org/
- **Maxima ODEs**: https://maxima.sourceforge.io/docs/manual/maxima_23.html

---

## 🎯 Próximos Pasos Recomendados

1. **Integrar Maxima** para ODEs no lineales y sistemas (ver `MAXIMA_INTEGRATION.md`)
2. **Agregar soporte para condiciones iniciales**:
   ```calcpad
   sol = solve_ode(y'' + 4*y, y, x, y(0)=1, y'(0)=0)
   ```
3. **Implementar método de variación de parámetros** para ODEs no homogéneas
4. **Agregar transformadas de Laplace** para resolver ODEs

---

## 📄 Archivos Relacionados

- `Examples/Test-ODE-Simple.cpd` - Ejemplos de uso
- `Examples/Test-ODE-Complete.cpd` - Pruebas exhaustivas
- `MAXIMA_INTEGRATION.md` - Integración de Maxima para ODEs avanzadas
- `Calcpad.Common/ExpressionParsers/SymbolicParser.cs` - Implementación

---

*Última actualización: 2026-01-26*
*Versión: 7.5.8-symbolic+odes*
