# Comparacion Calcpad vs SAP2000 - Resumen

## Objetivo
Comparar los resultados del ejemplo "Rectangular Slab FEA.cpd" de Calcpad con SAP2000 usando el API de Python.

## Datos del Problema

| Parametro | Valor |
|-----------|-------|
| Dimensiones | 6m x 4m |
| Espesor | 0.1m |
| Carga | 10 kN/m2 |
| E | 35,000 MPa |
| nu | 0.15 |
| Malla | 6x4 elementos |
| Condiciones de borde | Simplemente apoyada en perimetro |

## Solucion Analitica (Navier)

Para losa rectangular simplemente apoyada con carga uniforme:

- **Rigidez a flexion**: D = E*t^3/(12*(1-nu^2)) = 2983.80 kNm
- **Desplazamiento en centro**: w_centro = 6.6269 mm (serie de Fourier, 100 terminos)

## Problema Encontrado con SAP2000 API

### Descripcion
Al crear el modelo mediante el API de SAP2000 v24.1.0, las restricciones de desplazamiento vertical (UZ=0) definidas en los nodos del borde **no se estan aplicando correctamente** en el analisis.

### Sintomas
1. **Desplazamientos antisimetricos**: El modelo muestra desplazamientos positivos en y<b/2 y negativos en y>b/2
2. **Cero reacciones**: `JointReact()` retorna 0 reacciones, indicando que no hay apoyos activos
3. **Desplazamiento cero en centro**: El nodo central muestra UZ=0 debido a la rotacion de cuerpo rigido

### Resultados SAP2000 (erroneos)
```
Matriz UZ (mm):
y\x        0.0     1.0     2.0     3.0     4.0     5.0     6.0
4.0     -0.005  -0.643  -1.057  -1.192  -1.057  -0.643  -0.005
3.0     -0.003  -0.443  -0.733  -0.829  -0.733  -0.443  -0.003
2.0     -0.000   0.000  -0.000  -0.000  -0.000   0.000   0.000  <- eje de rotacion
1.0      0.003   0.443   0.733   0.829   0.733   0.443   0.003
0.0      0.005   0.643   1.057   1.192   1.057   0.643   0.005
```

### Verificaciones Realizadas
1. **SetRestraint** retorna 0 (exito)
2. **GetRestraint** retorna las restricciones correctas para los 20 nodos del borde
3. **PointElm.CountRestraint** reporta 20 restricciones
4. **PointElm.GetRestraint(elm)** retorna listas VACIAS [] - aqui esta el bug
5. **CreateAnalysisModel** se ejecuta sin errores
6. **RunAnalysis** retorna 0 (exito)

### Hallazgo Clave
El bug se confirma en que:
- `PointElm.CountRestraint()` retorna 20 (correcto)
- `PointElm.GetRestraint(elm)` retorna `[]` (lista vacia) para todos los elementos

Las restricciones se definen en el modelo de objetos pero **no se transfieren** al modelo de analisis. Esto causa que el modelo se comporte como si no tuviera apoyos en los bordes y=0 e y=b.

### Comportamiento Observado
- Las reacciones solo aparecen parcialmente (-55 kN vs -240 kN esperados)
- Los nodos del borde y=0 e y=b tienen desplazamientos != 0 (hasta 1.19 mm)
- El modelo rota como cuerpo rigido alrededor del eje y=b/2

### Confirmacion del Bug
El API de SAP2000 v24.1.0 tiene un bug donde **NINGUNO** de los siguientes metodos funciona correctamente con elementos de area:
- `PointObj.SetRestraint()` - No transfiere restricciones al modelo de analisis
- `PointObj.SetSpring()` - No aplica springs correctamente
- Ambos reportan exito (retorno 0) pero no funcionan

Este bug afecta especificamente a nodos conectados a elementos de area (Shell/Plate).

## Scripts Creados

1. `sap2000_losa_completo.py` - Modelo completo con verificacion de reacciones
2. `sap2000_analysis_model_restraints.py` - Verificacion del modelo de analisis
3. Multiples versiones de prueba con diferentes configuraciones

## Solucion Recomendada

### Procedimiento Semi-Automatico (Recomendado)

1. **Ejecutar el script** `sap2000_losa_definitivo.py` para crear el modelo
2. **Abrir SAP2000 GUI** con el archivo `SAP2000_Losa_Definitivo.sdb`
3. **Verificar que el modelo esta correcto** (nodos, elementos, cargas)
4. **Aplicar restricciones manualmente**:
   - Seleccionar todos los nodos del perimetro (20 nodos)
   - Menu: Assign > Joint > Restraints
   - Marcar UZ = restringido
   - Para las esquinas, agregar restricciones adicionales:
     - (0,0): UX, UY, UZ
     - (a,0): UY, UZ
     - (0,b): UX, UZ
5. **Correr el analisis** (Analyze > Run Analysis)
6. **Leer los resultados con el script** `sap2000_leer_resultados.py`

### Otras Opciones (No probadas)

- Usar ETABS o CSiBridge con su API
- Actualizar a una version mas reciente de SAP2000
- Reportar el bug a CSI (Computers and Structures Inc.)

## Calcpad

El ejemplo "Rectangular Slab FEA.cpd" de Calcpad utiliza un elemento de 16 DOF basado en teoria de Kirchhoff. Los resultados esperados deberian ser cercanos a la solucion analitica de Navier.

Para ejecutar la comparacion completa, es necesario resolver primero el problema con el API de SAP2000 o usar un metodo alternativo.

---
*Documento generado durante diagnostico de problema con API SAP2000*
*Fecha: 2026-01-17*
