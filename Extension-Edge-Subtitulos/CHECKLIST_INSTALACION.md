# ✅ Checklist de Instalación - Extensión Subtítulos en Español

Usa esta lista para verificar que todo esté correctamente configurado antes de usar la extensión.

## 📦 Archivos requeridos

### Archivos principales (Ya incluidos)

- [x] `manifest.json` - Configuración de la extensión
- [x] `popup.html` - Interfaz de usuario
- [x] `popup.js` - Lógica del popup
- [x] `content.js` - Script principal (inyectado en páginas)
- [x] `background.js` - Service worker
- [x] `styles.css` - Estilos para subtítulos

### Documentación (Ya incluida)

- [x] `README.md` - Documentación completa
- [x] `INICIO_RAPIDO.md` - Guía de inicio rápido
- [x] `INTEGRACION_LOKENDO.md` - Guía de integración Lokendo API
- [x] `CHECKLIST_INSTALACION.md` - Este archivo
- [x] `generar_iconos.html` - Generador de iconos

### Archivos por crear

- [ ] `icons/icon16.png` - Icono 16x16 píxeles
- [ ] `icons/icon48.png` - Icono 48x48 píxeles
- [ ] `icons/icon128.png` - Icono 128x128 píxeles

**Cómo crear los iconos**:
1. Abre `generar_iconos.html` en tu navegador
2. Haz clic en "Generar y Descargar Iconos"
3. Crea la carpeta `icons/` si no existe
4. Mueve los 3 archivos descargados a `icons/`

## 🚀 Instalación Básica

### Paso 1: Verificar archivos

```
Extension-Edge-Subtitulos/
├── manifest.json              ✅
├── popup.html                 ✅
├── popup.js                   ✅
├── content.js                 ✅
├── background.js              ✅
├── styles.css                 ✅
├── generar_iconos.html        ✅
├── README.md                  ✅
├── INICIO_RAPIDO.md          ✅
├── INTEGRACION_LOKENDO.md    ✅
├── CHECKLIST_INSTALACION.md  ✅
├── .gitignore                 ✅
└── icons/
    ├── icon16.png             ⚠️ Crear
    ├── icon48.png             ⚠️ Crear
    └── icon128.png            ⚠️ Crear
```

### Paso 2: Crear iconos

- [ ] Abrir `generar_iconos.html` en Edge/Chrome
- [ ] Clic en "Generar y Descargar Iconos"
- [ ] Crear carpeta `icons/` dentro de `Extension-Edge-Subtitulos/`
- [ ] Mover `icon16.png`, `icon48.png`, `icon128.png` a `icons/`
- [ ] Verificar que los iconos existen:
  ```
  icons/icon16.png  ✅
  icons/icon48.png  ✅
  icons/icon128.png ✅
  ```

### Paso 3: Cargar en Edge

- [ ] Abrir Microsoft Edge
- [ ] Ir a `edge://extensions/`
- [ ] Activar "Modo de desarrollador" (esquina inferior izquierda)
- [ ] Clic en "Cargar extensión desempaquetada"
- [ ] Seleccionar carpeta `Extension-Edge-Subtitulos`
- [ ] Verificar que aparece el icono 🎬 en la barra de herramientas
- [ ] Sin errores en la consola de extensiones

### Paso 4: Prueba básica

- [ ] Ir a YouTube: https://www.youtube.com/watch?v=jNQXAC9IVRw
- [ ] Hacer clic en el icono 🎬 de la extensión
- [ ] Ver el popup con botones:
  - "Activar en esta página"
  - Checkbox "Generar subtítulos automáticamente"
  - Dropdown de voces TTS
  - Slider de velocidad
- [ ] Clic en "Activar en esta página"
- [ ] Mensaje: "1 video(s) detectado(s)" o similar
- [ ] Estado cambia a "Activo" (fondo verde)

## ⚙️ Configuración Avanzada (Opcional)

### Opción A: Solo modo simulación (Sin APIs)

- [x] Funciona out-of-the-box
- [x] Subtítulos de ejemplo (no transcribe audio real)
- [x] TTS usando Web Speech API del navegador
- [x] No requiere API keys
- [x] Perfecto para probar la extensión

✅ **No se requiere configuración adicional**

### Opción B: TTS mejorado con Edge TTS (Gratis)

#### Requisitos
- [ ] Python instalado: https://www.python.org/downloads/
- [ ] Versión Python >= 3.7

#### Pasos
- [ ] Abrir terminal/PowerShell
- [ ] Instalar dependencias:
  ```bash
  pip install edge-tts flask flask-cors
  ```
- [ ] Crear archivo `tts_server.py` (ver `INICIO_RAPIDO.md`)
- [ ] Ejecutar servidor:
  ```bash
  python tts_server.py
  ```
- [ ] Verificar que el servidor está corriendo: http://localhost:5000
- [ ] Editar `background.js` línea 142 (ver `INICIO_RAPIDO.md`)
- [ ] Recargar extensión en `edge://extensions/`
- [ ] Probar generación de audio TTS

#### Verificación
- [ ] Consola muestra: `[Subtítulos ES BG] Generando TTS con Edge...`
- [ ] Audio se genera correctamente
- [ ] No hay errores 404 o conexión rechazada
- [ ] Calidad de voz mejorada vs Web Speech API

### Opción C: Transcripción real con Whisper API

#### Requisitos
- [ ] Cuenta OpenAI: https://platform.openai.com/signup
- [ ] Saldo disponible (mínimo $5)
- [ ] API Key generada

#### Pasos
- [ ] Crear cuenta en OpenAI
- [ ] Agregar saldo: https://platform.openai.com/account/billing
- [ ] Generar API Key: https://platform.openai.com/account/api-keys
- [ ] Copiar API Key (comienza con `sk-`)
- [ ] Editar `background.js` línea 67
- [ ] Reemplazar:
  ```javascript
  const OPENAI_API_KEY = 'sk-TU_API_KEY_AQUI';
  ```
- [ ] Descomentar código de Whisper API (líneas 78-93)
- [ ] Recargar extensión

#### Verificación
- [ ] Generar subtítulos en un video real
- [ ] Esperar 1-2 minutos
- [ ] Subtítulos coinciden con el audio del video
- [ ] Consola muestra: `[Subtítulos ES BG] Transcripción exitosa`
- [ ] Verificar consumo en: https://platform.openai.com/account/usage

**Costo estimado**: $0.006 por minuto (~$0.36 por hora de video)

### Opción D: TTS Premium con Lokendo

#### Requisitos
- [ ] Cuenta Lokendo: https://lokendo.com
- [ ] Saldo disponible
- [ ] API Key de Lokendo

#### Pasos
- [ ] Seguir guía completa en `INTEGRACION_LOKENDO.md`
- [ ] Obtener API Key de Lokendo
- [ ] Configurar backend proxy (recomendado)
- [ ] Editar `background.js` con integración Lokendo
- [ ] Actualizar selector de voces en `popup.html`
- [ ] Recargar extensión

#### Verificación
- [ ] Selector de voces muestra voces Lokendo
- [ ] Audio TTS se genera con voz premium
- [ ] Calidad notablemente superior
- [ ] Verificar consumo en panel de Lokendo

**Costo estimado**: Desde $10/mes según uso

## 🧪 Testing Completo

### Test 1: Detección de videos

- [ ] YouTube: https://www.youtube.com
  - [ ] Detecta video en página principal
  - [ ] Detecta video en página de reproducción
  - [ ] Detecta videos embebidos
- [ ] Vimeo: https://vimeo.com
  - [ ] Detecta videos
- [ ] Sitio con video HTML5 directo
  - [ ] Detecta `<video>` tags

### Test 2: Generación de subtítulos

- [ ] Activar extensión en video
- [ ] Clic "Generar Subtítulos"
- [ ] Barra de progreso aparece
- [ ] Progreso va de 0% a 100%
- [ ] Mensaje final: "Subtítulos generados"
- [ ] Overlay de subtítulos aparece sobre el video
- [ ] Subtítulos se sincronizan con el tiempo del video

### Test 3: Generación de audio TTS

- [ ] Primero generar subtítulos
- [ ] Clic "Generar Audio TTS"
- [ ] Seleccionar voz del dropdown
- [ ] Ajustar velocidad si se desea
- [ ] Barra de progreso aparece
- [ ] Mensaje final: "Audio TTS aplicado"
- [ ] Video original se mutea
- [ ] Audio en español se reproduce sincronizado
- [ ] Pausar/reproducir funciona correctamente
- [ ] Seek (saltar en el video) sincroniza el audio

### Test 4: Configuración persistente

- [ ] Cambiar configuración:
  - [ ] Activar "Auto-subtítulos"
  - [ ] Activar "Auto-audio"
  - [ ] Cambiar voz
  - [ ] Cambiar velocidad
- [ ] Cerrar popup
- [ ] Abrir popup nuevamente
- [ ] Verificar que configuración se mantuvo

### Test 5: Múltiples páginas

- [ ] Activar en Página A
- [ ] Cambiar a Página B
- [ ] Activar en Página B
- [ ] Volver a Página A
- [ ] Verificar que sigue activo en A
- [ ] Subtítulos funcionan en ambas páginas

## 🐛 Troubleshooting

### Problema: Iconos no aparecen

**Verificar**:
- [ ] Carpeta `icons/` existe
- [ ] Los 3 archivos PNG existen
- [ ] Nombres exactos: `icon16.png`, `icon48.png`, `icon128.png`
- [ ] Archivos no están corruptos (abrirlos con visor de imágenes)

**Solución**:
- Regenerar iconos con `generar_iconos.html`
- Recargar extensión en `edge://extensions/`

### Problema: "Content script not loaded"

**Verificar**:
- [ ] La página cargó completamente
- [ ] No hay errores en consola de la página (F12)
- [ ] `content.js` está incluido en `manifest.json`

**Solución**:
- Recargar la página (F5)
- Activar extensión de nuevo

### Problema: No detecta videos

**Verificar**:
- [ ] El sitio usa `<video>` HTML5 o `<iframe>` de YouTube/Vimeo
- [ ] No hay bloqueo por CORS
- [ ] Consola muestra: `[Subtítulos ES] X video(s) detectado(s)`

**Solución**:
- Probar primero en YouTube
- Ver consola del navegador para errores
- Algunos sitios con DRM pueden bloquear

### Problema: Subtítulos no se sincronizan

**Verificar**:
- [ ] Estás usando modo simulación (timestamps genéricos)
- [ ] Whisper API configurada para timestamps reales

**Solución**:
- Configurar Whisper API para transcripción real con timestamps

### Problema: TTS no suena natural

**Verificar**:
- [ ] Estás usando Web Speech API del navegador

**Solución**:
- Configurar Edge TTS (gratis, mejor calidad)
- Configurar Lokendo (pago, máxima calidad)

### Problema: Error 401/403 en API

**Verificar**:
- [ ] API Key correcta
- [ ] No hay espacios antes/después de la API Key
- [ ] Saldo disponible en la cuenta
- [ ] API Key activa (no revocada)

**Solución**:
- Verificar API Key en panel de control
- Agregar saldo si es necesario
- Regenerar API Key si está revocada

## 📊 Métricas de Éxito

Al finalizar la instalación, deberías tener:

- ✅ Extensión cargada en Edge sin errores
- ✅ Icono visible en barra de herramientas
- ✅ Popup funcional con todos los controles
- ✅ Detección de videos funcionando
- ✅ Generación de subtítulos funcionando (simulación mínimo)
- ✅ Overlay de subtítulos aparece sobre el video
- ✅ Audio TTS funciona (Web Speech API mínimo)
- ✅ Configuración se guarda correctamente

### Instalación Básica Completa
- ✅ Todo lo anterior

### Instalación Avanzada Completa
- ✅ Todo lo anterior +
- ✅ Edge TTS configurado y funcionando
- ✅ Whisper API transcribiendo audio real
- ✅ (Opcional) Lokendo API con voces premium

## 🎓 Próximos Pasos

Una vez completada la instalación:

1. **Usar la extensión**
   - [ ] Ver videos en YouTube en español
   - [ ] Probar con cursos online en inglés
   - [ ] Experimentar con diferentes voces

2. **Optimizar**
   - [ ] Ajustar velocidad de TTS a tu preferencia
   - [ ] Probar diferentes voces
   - [ ] Configurar APIs para mejor calidad

3. **Compartir**
   - [ ] Mostrar a amigos/colegas
   - [ ] Compartir en redes sociales
   - [ ] Contribuir al proyecto

## 📞 Soporte

Si algo no funciona:

1. **Revisa esta checklist** completa
2. **Consulta `README.md`** para documentación detallada
3. **Lee `INICIO_RAPIDO.md`** para soluciones rápidas
4. **Revisa la consola del navegador** (F12) para errores específicos
5. **Abre un issue** en el repositorio del proyecto

---

**¡Felicidades por completar la instalación! 🎉**

Ahora puedes disfrutar de videos con subtítulos y audio en español de alta calidad.

**¡Disfruta! 🎬🇪🇸**
