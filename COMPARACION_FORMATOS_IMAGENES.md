# COMPARACIÓN: Sistemas de Almacenamiento de Imágenes

## 1️⃣ CALCPAD ACTUAL (.cpd)
```
test.cpd (texto plano)
```
- ✅ **Texto plano puro** - Se puede renombrar a .txt
- ✅ **Funciona donde sea** - Cualquier editor
- ✅ **Control de versiones** - Git diff funciona perfecto
- ❌ **Sin imágenes embebidas** - Necesita carpeta externa
- ❌ **No portable** - Debes enviar archivo + carpeta

---

## 2️⃣ SMATH STUDIO (.sm)
```xml
<?xml version="1.0" encoding="utf-8"?>
<worksheet>
  <regions>
    <region>
      <picture>
        <raw format="png" encoding="base64">
          iVBORw0KGgoAAAANSUhEUgAACbUAAANrCAYAAAB7wufuAAAAAXNSR...
        </raw>
      </picture>
    </region>
  </regions>
</worksheet>
```
- ✅ **Texto plano puro** - XML sin comprimir
- ✅ **Imágenes embebidas** - Base64 en el XML
- ✅ **100% portable** - Un solo archivo
- ✅ **Funciona donde sea** - Se puede abrir en Notepad
- ✅ **Se puede renombrar a .txt** - Sigue funcionando
- ❌ **Archivos grandes** - Base64 aumenta 33% el tamaño
- ✅ **Control de versiones** - Git funciona (pero diffs grandes)

---

## 3️⃣ MATHCAD PRIME (.mcdx)
```
archivo.mcdx (ZIP binario)
├── worksheet.xml
└── media/
    └── Image0.png
```
- ❌ **NO es texto plano** - Es un ZIP
- ✅ **Imágenes embebidas** - Dentro del ZIP
- ✅ **100% portable** - Un solo archivo
- ❌ **NO se puede renombrar a .txt** - Es binario
- ❌ **Control de versiones difícil** - Git no puede hacer diff del contenido
- ✅ **Tamaño eficiente** - Compresión ZIP

---

## 4️⃣ PROPUESTA: CALCPAD con Base64 (.cpd)
```
'================================================
' Módulo de Elasticidad
'================================================
E = 2.535
ν = 0.20

'================================================
' IMAGEN: Diagrama de Reissner-Mindlin
'================================================
@{image png base64}
iVBORw0KGgoAAAANSUhEUgAACbUAAANrCAYAAAB7wufu
AAAAAXNSRIrs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcE
hZcwAAFiUAABYlAUlSJPAAALmvSURBVHhe7N197G1ZfRd
...
@{end image}

'================================================
' Matriz constitutiva a flexión
'================================================
Df = E*d^3/(12*(1-ν^2))*[1, ν, 0; ν, 1, 0; 0, 0, (1-ν)/2]
```

### **VENTAJAS:**
- ✅ **Texto plano puro** - Como .cpd actual
- ✅ **Imágenes embebidas** - Como SMath Studio
- ✅ **100% portable** - Un solo archivo
- ✅ **Se puede renombrar a .txt** - Sigue funcionando
- ✅ **Compatible con versión anterior** - Los .cpd sin imágenes siguen funcionando
- ✅ **Control de versiones** - Git diff funciona
- ❌ **Archivos grandes** - Si hay muchas imágenes

### **DESVENTAJAS:**
- Archivo más grande que .cpkg (pero sigue siendo texto)
- Base64 no es legible para humanos (pero tampoco importa)

---

## 5️⃣ PROPUESTA ALTERNATIVA: .CPKG (ZIP)
```
archivo.cpkg (ZIP)
├── worksheet.cpd
└── media/
    └── imagen1.png
```

### **VENTAJAS:**
- ✅ **Imágenes embebidas**
- ✅ **100% portable**
- ✅ **Tamaño eficiente** - Compresión ZIP

### **DESVENTAJAS:**
- ❌ **NO es texto plano** - Es binario como .mcdx
- ❌ **NO se puede renombrar a .txt**
- ❌ **Control de versiones difícil**
- ❌ **Pierde la filosofía Calcpad** de texto plano

---

## 🏆 RECOMENDACIÓN FINAL

**OPCIÓN GANADORA: Calcpad con Base64 (como SMath Studio)**

### **¿Por qué?**

1. **Mantiene la filosofía Calcpad** - Texto plano puro
2. **Añade portabilidad total** - Como SMath y Mathcad
3. **Backwards compatible** - Los .cpd sin imágenes siguen funcionando
4. **Se puede convertir** - .cpd ↔ .cpd+imágenes fácilmente

### **Implementación:**

```calcpad
' Sintaxis simple y clara
@{image png base64}
[contenido Base64 aquí]
@{end image}

' O alternativamente
@{image}
format: png
encoding: base64
data: iVBORw0KGgoAAAA...
@{end image}
```

### **Flujo de trabajo:**

1. **Crear .cpd con imagen:**
   - Usuario inserta imagen en Calcpad WPF
   - Calcpad convierte imagen a Base64
   - Inserta bloque `@{image}` en el .cpd

2. **Abrir .cpd con imagen:**
   - Parser detecta `@{image}`
   - Decodifica Base64 → PNG
   - Muestra en HTML de salida

3. **Compartir:**
   - Envías SOLO el archivo .cpd
   - Funciona en Windows, Linux, Mac
   - Se puede abrir en cualquier editor de texto

### **Ventaja sobre .cpkg:**

```
test.cpd (con imágenes Base64)
→ Renombrar a test.txt
→ Abrir en Notepad
→ ¡Funciona!

archivo.cpkg (ZIP)
→ Renombrar a archivo.txt
→ Abrir en Notepad
→ ✗ Basura binaria
```

---

## 📝 EJEMPLO REAL

**Archivo SMath Studio (Imagen.sm):**
- Tamaño: 63 KB (con imagen embebida)
- Formato: XML texto plano
- Líneas: 37
- Portable: ✓ 100%

**Mismo contenido en .cpkg:**
- Tamaño: ~20 KB (comprimido)
- Formato: ZIP binario
- Portable: ✓ 100%
- **PERO**: No es texto plano ✗

**Conclusión:**
SMath Studio sacrifica ~30% más de espacio para mantener
TODO como texto plano. Vale la pena para portabilidad máxima.
