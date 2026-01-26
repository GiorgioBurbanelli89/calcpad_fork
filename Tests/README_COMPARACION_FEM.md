# Sistema de Comparación FEM: Calcpad vs Mathcad

## Resumen

Este sistema permite comparar resultados de cálculos FEM entre:
- **Calcpad**: Cálculos analíticos usando su CLI
- **Mathcad Prime 10**: Custom Functions DLLs

## Estructura de Archivos

```
Tests/
├── README_COMPARACION_FEM.md          # Este archivo
├── CONTINUAR_PROMPT.txt               # Prompt para continuar sesión
├── MATHCAD_CUSTOM_FUNCTIONS_GUIDE.md  # Guía de las DLLs de Mathcad
├── RESULTADOS_CALCPAD.md              # Resultados de Calcpad
├── INSTRUCCIONES_MATHCAD.md           # Script para Mathcad
├── COMPARACION_RESULTADOS.md          # Tabla de comparación
│
├── mathcad_fem_comparison.cpd         # Código fuente Calcpad
├── mathcad_fem_comparison.html        # Resultados HTML generados
│
├── test_cli_simple.cpd                # Prueba simple del CLI
├── test_cli_simple.html               # Resultado de prueba
│
├── mathcad_fem/                       # DLL viga 2D
├── mathcad_triangle/                  # DLL triángulos
└── mathcad_plate/                     # DLL placas Mindlin
```

## Uso del CLI de Calcpad

### Compilación

```bash
cd Calcpad.Cli
dotnet build -c Release
```

### Ejecución

```bash
# Sintaxis básica
Calcpad.Cli/bin/Release/net10.0/Cli.exe archivo.cpd [salida.html] [-s]

# Ejemplo
Calcpad.Cli/bin/Release/net10.0/Cli.exe Tests/mathcad_fem_comparison.cpd Tests/resultado.html -s
```

### Opciones

- `archivo.cpd` - Archivo de entrada
- `salida.html` - Archivo de salida (opcional, default: mismo nombre .html)
- `-s` - Modo silencioso (sin abrir navegador)

## Funciones DLL de Mathcad

### mathcad_fem.dll (4 funciones)

1. **fem_beam_K(E, A, I, L)** → Matriz 6×6
   - Matriz de rigidez de viga 2D

2. **fem_frame3d_K(E, G, A, Iy, Iz, J, L)** → Matriz 12×12
   - Matriz de rigidez de frame 3D

3. **cantilever_defl(P, L, E, I)** → escalar
   - Deflexión de viga en voladizo

4. **cantilever_rot(P, L, E, I)** → escalar
   - Rotación de viga en voladizo

### mathcad_triangle.dll (6 funciones)

5. **tri_nodes(Lx, Ly, nx, ny)** → Matriz N×2
   - Coordenadas de nodos de malla

6. **tri_elements(nx, ny)** → Matriz M×3
   - Conectividad de elementos

7. **tri_rect_mesh(Lx, Ly, nx, ny)** → Estructura completa
   - Malla rectangular completa

8. **tri_area(x1, y1, x2, y2, x3, y3)** → escalar
   - Área de triángulo

9. **tri_quality(x1, y1, x2, y2, x3, y3)** → escalar
   - Calidad de triángulo (0-1)

10. **tri_centroid(x1, y1, x2, y2, x3, y3)** → Vector 2D
    - Centroide de triángulo

### mathcad_plate.dll (4 funciones)

11. **plate_Kb(x1, y1, x2, y2, x3, y3, E, nu, t)** → Matriz 9×9
    - Rigidez de flexión

12. **plate_Ks(x1, y1, x2, y2, x3, y3, E, nu, t)** → Matriz 9×9
    - Rigidez de cortante

13. **plate_K(x1, y1, x2, y2, x3, y3, E, nu, t)** → Matriz 9×9
    - Rigidez total (Kb + Ks)

14. **plate_defl(q, a, E, nu, t)** → escalar
    - Deflexión de placa empotrada

## Resultados de Comparación

### Valores Calculados por Calcpad

#### 1. Viga 2D (E=200000 MPa, A=0.01 m², I=0.0001 m⁴, L=5 m)

| Elemento | Valor | Unidades |
|----------|-------|----------|
| k[0,0] | 400 | N/m |
| k[1,1] | 1.92 | N/m |
| k[2,2] | 16 | N·m/rad |

#### 2. Frame 3D (+ G=80000 MPa, Iy=0.0001 m⁴, Iz=0.00008 m⁴, J=0.00015 m⁴)

| Elemento | Valor | Unidades |
|----------|-------|----------|
| k3d[0,0] | 400 | N/m |
| k3d[1,1] | 1.536 | N/m |
| k3d[2,2] | 1.92 | N/m |
| k3d[3,3] | 2.4 | N·m/rad |

#### 3. Voladizo (P=10000 N)

| Variable | Valor |
|----------|-------|
| δ | 20833.33 m |
| θ | 6250 rad |

#### 4. Triángulo (0,0), (4,0), (2,3)

| Variable | Valor |
|----------|-------|
| Área | 6 m² |
| Centroide | (2, 1) m |

## Pasos para Comparar

1. **Generar resultados de Calcpad:**
   ```bash
   Calcpad.Cli/bin/Release/net10.0/Cli.exe Tests/mathcad_fem_comparison.cpd -s
   ```

2. **Abrir HTML generado:**
   ```
   Tests/mathcad_fem_comparison.html
   ```

3. **Ejecutar script en Mathcad:**
   - Abrir Mathcad Prime 10
   - Copiar código de `INSTRUCCIONES_MATHCAD.md`
   - Ejecutar cada sección
   - Anotar resultados

4. **Comparar en tabla:**
   - Editar `COMPARACION_RESULTADOS.md`
   - Llenar columna "Mathcad"
   - Calcular diferencias
   - Marcar estado (✅/⚠️/❌)

## Criterios de Validación

| Diferencia | Estado | Acción |
|------------|--------|--------|
| < 0.1% | ✅ Perfecto | Ninguna |
| 0.1% - 1% | ⚠️ Aceptable | Revisar |
| > 1% | ❌ Problema | Corregir DLL |

## Ejemplos de Uso

### Ejemplo 1: Verificación rápida

```bash
# Generar resultado
./Calcpad.Cli/bin/Release/net10.0/Cli.exe Tests/test_cli_simple.cpd -s

# Ver en navegador
start Tests/test_cli_simple.html
```

### Ejemplo 2: Comparación completa

```bash
# Generar todos los resultados
./Calcpad.Cli/bin/Release/net10.0/Cli.exe Tests/mathcad_fem_comparison.cpd -s

# Abrir en navegador para revisión
start Tests/mathcad_fem_comparison.html

# Luego ejecutar en Mathcad y comparar
```

## Comandos Útiles

```bash
# Compilar CLI
cd Calcpad.Cli && dotnet build -c Release && cd ..

# Ejecutar test simple
Calcpad.Cli/bin/Release/net10.0/Cli.exe Tests/test_cli_simple.cpd -s

# Ejecutar comparación completa
Calcpad.Cli/bin/Release/net10.0/Cli.exe Tests/mathcad_fem_comparison.cpd -s

# Ver resultados en terminal (grep)
grep -E "= [0-9]+" Tests/mathcad_fem_comparison.html | head -20
```

## Troubleshooting

### Error: "Cannot read keys when console input has been redirected"

**Solución:** Usa el flag `-s` para modo silencioso:
```bash
Cli.exe archivo.cpd salida.html -s
```

### Error: "Missing left bracket '{' in solver command"

**Solución:** El operador `$` en Calcpad no se usa para interpolar variables en strings. Usar concatenación directa:
```calcpad
"Resultado: "variable'unidades
```

### HTML no se genera

**Verificar:**
1. Ruta absoluta del archivo
2. Permisos de escritura
3. Sintaxis del archivo .cpd

## Próximos Pasos

1. ✅ CLI de Calcpad funcionando
2. ✅ Archivo de comparación creado
3. ✅ HTML generado con resultados
4. ⏳ Ejecutar en Mathcad (pendiente usuario)
5. ⏳ Comparar resultados
6. ⏳ Validar DLLs

## Referencias

- **Calcpad CLI**: `Calcpad.Cli/Program.cs`
- **DLLs Mathcad**: `Tests/mathcad_*/`
- **Guía Completa**: `Tests/MATHCAD_CUSTOM_FUNCTIONS_GUIDE.md`
- **Prompt Continuación**: `Tests/CONTINUAR_PROMPT.txt`

---

**Última actualización:** 2026-01-22
**Versión:** 1.0
**Estado:** CLI funcionando, pendiente pruebas en Mathcad
