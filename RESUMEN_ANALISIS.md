# Resumen: Familiarización con SAP2000 y Comparación con Calcpad

## 📋 Objetivo

Comparar los resultados de análisis por elementos finitos entre:
- **Calcpad**: Software de cálculos ingenieriles con capacidades FEA
- **SAP2000**: Software profesional de análisis estructural

## 🔍 Hallazgos Iniciales

### 1. Archivos Encontrados

#### Documentación SAP2000 API
- **Archivo**: `CSI_OAPI_Documentation.chm` (3.17 MB)
- **Ubicación**: `C:\Users\j-b-j\Documents\Calcpad-7.5.7\`
- **Contenido**: Documentación completa de la API OAPI de SAP2000
- **Fecha**: 11 de octubre de 2022

#### Ejemplos de Calcpad
- **Carpeta**: `C:\Users\j-b-j\Documents\Calcpad\Examples\Mechanics\Finite Elements\`
- **Ejemplos encontrados**:
  1. `Rectangular Slab FEA.cpd` (Análisis de losa rectangular)
  2. `Deep Beam FEA.cpd` (Viga de gran peralte)
  3. `Flat Slab FEA.cpd` (Losa plana)
  4. `Mindlin Plate FEA.cpd` (Placa de Mindlin)

#### Modelos SAP2000
- **Carpeta**: `SAP 2000/`
- **Archivos**:
  - `Plate-6x4.s2k` (Modelo de placa 6m × 4m)
  - `Plane-20x10.s2k` (Modelo plano 20m × 10m)

### 2. Análisis del Modelo de Losa Rectangular

#### Configuración del Modelo (Ambos Programas)

```
Geometría:
  - Dimensiones: a = 6m, b = 4m
  - Espesor: t = 0.1m
  - Condiciones de apoyo: Simplemente apoyada en los 4 bordes

Material:
  - Concreto
  - E = 35,000 MPa
  - ν = 0.15

Carga:
  - Tipo: Uniformemente distribuida
  - Magnitud: q = 10 kN/m²

Discretización:
  - Elementos en X: 6
  - Elementos en Y: 4
  - Total elementos: 24
  - Total nodos: 35
```

#### Estructura del Archivo SAP2000 (.s2k)

El archivo `Plate-6x4.s2k` contiene:

1. **SYSTEM**: Define unidades (kN-m) y grados de libertad (UZ, RX, RY)

2. **JOINT**: 35 nodos con coordenadas
   ```
   Nodo 1: X=-3, Y=-2, Z=0
   Nodo 18: X=0, Y=0, Z=0 (centro)
   Nodo 35: X=3, Y=2, Z=0
   ```

3. **RESTRAINT**: Restricciones en bordes
   - Bordes: U3, R1, R2 restringidos
   - Esquinas: Restricciones completas

4. **MATERIAL**: Definición de concreto
   ```
   NAME=CONC
   E=3.5E+07 (35,000 MPa)
   U=.15 (ν=0.15)
   ```

5. **SHELL SECTION**: Sección de placa delgada
   ```
   TYPE=Plate,Thin
   TH=.1 (espesor 0.1m)
   ```

6. **SHELL**: 24 elementos rectangulares

7. **LOAD**: Carga uniforme
   ```
   TYPE=UNIFORM
   UZ=-10 (10 kN/m² en dirección -Z)
   ```

#### Estructura del Ejemplo Calcpad (.cpd)

El archivo `Rectangular Slab FEA.cpd` implementa:

1. **Funciones de forma**: Funciones cúbicas de Hermite para elementos de placa
   - Base functions: Φ₁, Φ₂, Φ₃, Φ₄
   - Derivadas primera y segunda

2. **Matriz de rigidez del elemento**:
   ```
   K_e,ij = a₁·b₁·∬ Bᵢᵀ·D·Bⱼ dξdη
   ```

3. **Matriz constitutiva**:
   ```
   D = E·t³/(12(1-ν²)) × [1 ν 0; ν 1 0; 0 0 (1-ν)/2]
   ```

4. **Ensamblaje global**: Construcción de la matriz K global

5. **Solución**: Método de Cholesky para sistemas simétricos
   ```
   Z = clsolve(K; F)
   ```

6. **Post-procesamiento**:
   - Desplazamientos en nodos
   - Momentos flectores Mx, My, Mxy
   - Mapas de contorno

### 3. API de SAP2000 - Conceptos Clave

#### Creación del Objeto SAP2000
```csharp
// Crear helper
Helper myHelper = new Helper();

// Crear objeto SAP2000
SapObject mySapObject = myHelper.CreateObjectProgID("CSI.SAP2000.API.SapObject");

// Iniciar aplicación
mySapObject.ApplicationStart(Units: eUnits.kN_m_C, Visible: false);

// Obtener modelo
cSapModel mySapModel = mySapObject.SapModel;
```

#### Operaciones Principales

1. **Abrir modelo**:
   ```csharp
   mySapModel.File.OpenFile(path);
   ```

2. **Desactivar alertas** (IMPORTANTE):
   ```csharp
   mySapModel.SetModelIsLocked(false);
   ```

3. **Ejecutar análisis**:
   ```csharp
   mySapModel.Analyze.RunAnalysis();
   ```

4. **Guardar modelo**:
   ```csharp
   mySapModel.File.Save(path);
   ```

5. **Obtener resultados**:
   ```csharp
   // Desplazamientos en nodos
   mySapModel.Results.JointDispl(...);

   // Esfuerzos en shells
   mySapModel.Results.AreaStressShell(...);
   ```

### 4. Scripts Creados

#### SAP2000_Runner.cs
- **Propósito**: Ejecutar modelo en SAP2000 sin intervención manual
- **Características**:
  - Inicia SAP2000 en modo invisible
  - Desactiva todas las alertas
  - Ejecuta el análisis
  - Guarda el modelo automáticamente
  - Extrae resultados del nodo central
  - Extrae momentos del elemento central

#### extract_chm.ps1
- **Propósito**: Leer información del archivo CHM
- **Uso**: Visualizar documentación de la API

### 5. Comparación de Métodos

| Aspecto | Calcpad | SAP2000 |
|---------|---------|---------|
| Tipo de elemento | Placa Mindlin (16 DOF) | Shell delgado |
| Funciones de forma | Cúbicas de Hermite | Propias de SAP |
| Integración numérica | Cuadratura de Gauss | Interna |
| Solver | Cholesky | Interno (múltiples opciones) |
| Interfaz | Código + HTML | GUI + API |
| Resultados | Texto + Gráficos | Tablas + Diagramas |

## 📊 Próximos Pasos

1. ✅ Familiarización con SAP2000 API
2. ✅ Identificación del modelo equivalente
3. ✅ Creación de script automatizado
4. ⏳ Compilación y ejecución del script
5. ⏳ Extracción de resultados numéricos
6. ⏳ Ejecución del ejemplo en Calcpad
7. ⏳ Comparación cuantitativa de resultados
8. ⏳ Análisis de diferencias (si existen)

## 🎯 Métricas de Comparación

Se compararán los siguientes valores en el **punto central** (x=3m, y=2m):

1. **Desplazamiento vertical** w (mm)
2. **Momento flector Mx** (kN·m/m)
3. **Momento flector My** (kN·m/m)
4. **Momento torsor Mxy** (kN·m/m)

Tolerancia esperada: < 5% de diferencia

## 📚 Recursos

- **Calcpad CLI**: `C:\Users\j-b-j\Documents\Calcpad-7.5.7\Calcpad.Cli\bin\Debug\net10.0\Cli.exe`
- **Ejemplos**: `C:\Users\j-b-j\Documents\Calcpad\Examples\Mechanics\Finite Elements\`
- **API Docs**: `CSI_OAPI_Documentation.chm`
- **Modelos SAP**: `SAP 2000\Plate-6x4.s2k`

## 🔧 Comandos Útiles

### Ejecutar Calcpad CLI
```bash
Cli.exe "Rectangular Slab FEA.cpd"
```

### Abrir documentación SAP2000
```bash
hh.exe "CSI_OAPI_Documentation.chm"
```

### Compilar script C#
```bash
csc /reference:SAP2000v25.dll SAP2000_Runner.cs
```

---

**Fecha**: 17 de enero de 2026
**Estado**: Familiarización completa - Listo para ejecutar comparación
