# Inicio Rápido: Comparación FEM Calcpad vs Mathcad

## Uso Inmediato

### Paso 1: Ejecutar Script de Comparación

```bash
cd C:\Users\j-b-j\Documents\Calcpad-7.5.7\Tests
run_comparison.bat
```

**Qué hace:**
1. Compila el CLI de Calcpad (si es necesario)
2. Genera `mathcad_fem_comparison.html` con resultados
3. **Abre automáticamente el HTML en el navegador**

### Paso 2: Revisar Resultados de Calcpad

El HTML abierto muestra:
- ✅ Matriz de rigidez viga 2D: k[0,0] = 400 N/m
- ✅ Matriz de rigidez frame 3D: k3d[3,3] = 2.4 N·m/rad
- ✅ Voladizo: δ = 20833.33 m, θ = 6250 rad
- ✅ Triángulo: Área = 6 m², Centroide = (2, 1) m

### Paso 3: Ejecutar en Mathcad

1. Abre **Mathcad Prime 10**
2. Abre el archivo: `Tests\INSTRUCCIONES_MATHCAD.md`
3. Copia el código sección por sección
4. Ejecuta cada sección en Mathcad
5. Anota los resultados de Mathcad

### Paso 4: Comparar Resultados

1. Abre `Tests\COMPARACION_RESULTADOS.md`
2. Llena la columna "Mathcad" con los valores obtenidos
3. Calcula la diferencia relativa
4. Marca el estado:
   - ✅ si diferencia < 0.1%
   - ⚠️ si diferencia 0.1% - 1%
   - ❌ si diferencia > 1%

---

## Archivos Clave

| Archivo | Descripción |
|---------|-------------|
| `run_comparison.bat` | **Script principal** - Ejecutar este |
| `mathcad_fem_comparison.html` | Resultados de Calcpad (se abre automáticamente) |
| `INSTRUCCIONES_MATHCAD.md` | Código para copiar a Mathcad |
| `COMPARACION_RESULTADOS.md` | Tabla para llenar |
| `README_COMPARACION_FEM.md` | Guía completa |

---

## Ejemplo de Flujo

```
┌─────────────────────────────────────┐
│ 1. Ejecutar run_comparison.bat     │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 2. HTML se abre automáticamente     │
│    (mathcad_fem_comparison.html)    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 3. Revisar resultados de Calcpad    │
│    k[0,0] = 400 N/m ✅               │
│    k3d[3,3] = 2.4 N·m/rad ✅         │
│    δ = 20833.33 m ✅                 │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 4. Abrir Mathcad Prime 10           │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 5. Copiar script de                 │
│    INSTRUCCIONES_MATHCAD.md         │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 6. Ejecutar en Mathcad              │
│    K_beam := fem_beam_K(...)        │
│    K_beam[0,0] = ???                │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 7. Anotar resultados en             │
│    COMPARACION_RESULTADOS.md        │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 8. Validar: ✅ / ⚠️ / ❌             │
└─────────────────────────────────────┘
```

---

## Resultados Esperados de Calcpad

### Viga 2D
```
k[0,0] = 400 N/m         (EA/L)
k[1,1] = 1.92 N/m        (12EI/L³)
k[2,2] = 16 N·m/rad      (4EI/L)
```

### Frame 3D
```
k3d[0,0] = 400 N/m       (EA/L)
k3d[3,3] = 2.4 N·m/rad   (GJ/L)
k3d[4,4] = 16 N·m/rad    (4EIy/L)
```

### Voladizo
```
δ = 20833.33 m           (PL³/3EI)
θ = 6250 rad             (PL²/2EI)
```

### Triángulo
```
Área = 6 m²              (|(x2-x1)(y3-y1)-(x3-x1)(y2-y1)|/2)
Centroide = (2, 1) m     ((x1+x2+x3)/3, (y1+y2+y3)/3)
```

---

## Comandos Rápidos

```bash
# Ejecutar comparación (abre HTML automáticamente)
Tests\run_comparison.bat

# Recompilar CLI si es necesario
cd Calcpad.Cli
dotnet build -c Release
cd ..\Tests

# Generar HTML manualmente
..\Calcpad.Cli\bin\Release\net10.0\Cli.exe mathcad_fem_comparison.cpd

# Generar sin abrir navegador (modo silencioso)
..\Calcpad.Cli\bin\Release\net10.0\Cli.exe mathcad_fem_comparison.cpd -s
```

---

## Solución de Problemas

### Error: "Cannot find CLI"
**Solución:** El script compilará automáticamente. O ejecuta manualmente:
```bash
cd Calcpad.Cli && dotnet build -c Release
```

### Error: "Cannot read keys"
**Solución:** Ya solucionado. El script ahora NO usa el flag `-s` cuando quiere abrir el navegador.

### HTML no se abre
**Solución:** Abre manualmente `Tests\mathcad_fem_comparison.html`

### DLLs no se encuentran en Mathcad
**Solución:** Copia las DLLs a:
```
C:\Program Files\PTC\Mathcad Prime 10.0.0.0\Custom Functions\
```

---

## Siguiente Sesión

Si necesitas continuar en otra sesión de Claude Code:

1. Abre `Tests\CONTINUAR_PROMPT.txt`
2. Copia el prompt
3. Pega en nueva sesión de Claude Code
4. Agrega tu tarea específica

---

**¡Listo para usar!** Ejecuta `run_comparison.bat` y comienza la comparación.
