# 🎬 Subtítulos y Audio en Español - Extensión para Microsoft Edge

Extensión de navegador que genera subtítulos en español automáticamente y reemplaza el audio de videos con voz TTS (Text-to-Speech) en español.

## 🌟 Características

- ✅ **Detección automática** de videos en YouTube, Vimeo, Dailymotion y otros sitios
- ✅ **Generación de subtítulos** en español usando transcripción de audio
- ✅ **Traducción automática** al español si el video está en otro idioma
- ✅ **Audio TTS en español** con voces naturales (Lokendo, Edge TTS, Google TTS)
- ✅ **Sincronización perfecta** de subtítulos con el video
- ✅ **Formato SRT** estándar para subtítulos
- ✅ **Múltiples voces** españolas (España, México, Argentina)
- ✅ **Control de velocidad** (0.75x - 1.25x)

## 📋 Requisitos

- Microsoft Edge (versión 88 o superior)
- Conexión a internet para servicios de transcripción y TTS

## 🚀 Instalación

### Método 1: Carga manual (Desarrollo)

1. **Descarga los archivos** de la extensión en una carpeta local

2. **Abre Microsoft Edge** y navega a:
   ```
   edge://extensions/
   ```

3. **Activa el "Modo de desarrollador"** (interruptor en la esquina inferior izquierda)

4. **Haz clic en "Cargar extensión desempaquetada"**

5. **Selecciona la carpeta** `Extension-Edge-Subtitulos`

6. La extensión aparecerá en tu barra de herramientas con el icono 🎬

### Método 2: Instalación desde Microsoft Edge Add-ons (Futuro)

Una vez publicada en la tienda oficial, podrás instalarla directamente desde:
```
https://microsoftedge.microsoft.com/addons/
```

## 📖 Uso

### Activación básica

1. **Navega a un sitio** con videos (YouTube, Vimeo, cursos online, etc.)

2. **Haz clic en el icono** de la extensión 🎬 en la barra de herramientas

3. **Clic en "Activar en esta página"**

4. La extensión detectará automáticamente los videos en la página

### Generar subtítulos

**Modo Automático** (Recomendado):
- Marca la opción ✅ "Generar subtítulos automáticamente"
- Los subtítulos se generarán al activar la extensión

**Modo Manual**:
1. Activa la extensión en la página
2. Clic en "📝 Generar Subtítulos"
3. Espera 1-2 minutos mientras se transcribe el audio
4. Los subtítulos aparecerán sincronizados con el video

### Generar audio TTS

1. Primero genera los subtítulos (paso anterior)
2. Selecciona la voz deseada en el menú desplegable:
   - **Lokendo API** (Premium, mejor calidad)
   - **Edge: Español (España)**
   - **Edge: Español (México)**
   - **Edge: Español (Argentina)**
   - **Google TTS**
3. Ajusta la velocidad si lo deseas (0.75x - 1.25x)
4. Clic en "🔊 Generar Audio TTS"
5. El audio original se silenciará y se reemplazará con la voz en español

## ⚙️ Configuración

### Opciones disponibles

| Opción | Descripción | Valores |
|--------|-------------|---------|
| **Auto-subtítulos** | Genera subtítulos al activar | ✅ Activado / ☐ Desactivado |
| **Auto-audio** | Genera TTS al activar | ✅ Activado / ☐ Desactivado |
| **Voz TTS** | Voz para Text-to-Speech | Lokendo, Edge (ES/MX/AR), Google |
| **Velocidad** | Velocidad de reproducción | 0.75x / 1.0x / 1.25x |

### Configuración guardada

Las preferencias se guardan automáticamente en el almacenamiento local del navegador y se mantienen entre sesiones.

## 🔌 Integración con APIs externas

La extensión está preparada para integrarse con servicios externos. Actualmente incluye **simulaciones** para desarrollo.

### Transcripción de audio

#### Opción 1: OpenAI Whisper API (Recomendado)

Edita `background.js` línea 78-93:

```javascript
const formData = new FormData();
formData.append('file', audioBlob, 'audio.webm');
formData.append('language', 'es');

const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer TU_API_KEY_AQUI'
    },
    body: formData
});

const result = await response.json();
return result.text;
```

**Costo**: ~$0.006 por minuto de audio

#### Opción 2: AssemblyAI

```javascript
const response = await fetch('https://api.assemblyai.com/v2/transcript', {
    method: 'POST',
    headers: {
        'authorization': 'TU_API_KEY_AQUI',
        'content-type': 'application/json'
    },
    body: JSON.stringify({
        audio_url: audioUrl,
        language_code: 'es'
    })
});
```

**Costo**: $0.00025 por segundo (~$0.015 por minuto)

#### Opción 3: Google Speech-to-Text

```javascript
const response = await fetch('https://speech.googleapis.com/v1/speech:recognize?key=TU_API_KEY', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        config: {
            encoding: 'WEBM_OPUS',
            sampleRateHertz: 48000,
            languageCode: 'es-ES'
        },
        audio: {
            content: audioBase64
        }
    })
});
```

**Costo**: $0.006 por 15 segundos (~$0.024 por minuto)

### Text-to-Speech (TTS)

#### Opción 1: Lokendo API (Premium - Mejor calidad)

Edita `background.js` línea 154-169:

```javascript
const response = await fetch('https://api.lokendo.com/v1/tts', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer TU_API_KEY_LOKENDO',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        text: text,
        voice: voice, // 'es-ES-Male', 'es-MX-Female', etc.
        speed: speed,
        format: 'mp3'
    })
});

const audioBlob = await response.blob();
return audioBlob;
```

**Características Lokendo**:
- ✅ Voces muy naturales y expresivas
- ✅ Múltiples acentos (España, México, Argentina, Colombia, etc.)
- ✅ Control de tono, velocidad y emociones
- ✅ Formato MP3 de alta calidad
- 💰 Servicio de pago (contactar para precios)

#### Opción 2: Edge TTS (Gratis)

Requiere un backend proxy ya que Edge TTS no tiene API pública directa. Puedes usar:

**Backend Python con edge-tts**:

```bash
pip install edge-tts
```

```python
# server.py
from flask import Flask, request, send_file
import edge_tts
import asyncio

app = Flask(__name__)

@app.route('/tts', methods=['POST'])
async def generate_tts():
    data = request.json
    text = data['text']
    voice = data.get('voice', 'es-ES-AlvaroNeural')

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("output.mp3")

    return send_file("output.mp3", mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(port=5000)
```

Luego en `background.js`:

```javascript
const response = await fetch('http://localhost:5000/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: text,
        voice: 'es-ES-AlvaroNeural', // o 'es-MX-DaliaNeural', etc.
        speed: speed
    })
});

const audioBlob = await response.blob();
return audioBlob;
```

**Voces Edge disponibles**:
- 🇪🇸 `es-ES-AlvaroNeural` (Masculina, España)
- 🇪🇸 `es-ES-ElviraNeural` (Femenina, España)
- 🇲🇽 `es-MX-DaliaNeural` (Femenina, México)
- 🇲🇽 `es-MX-JorgeNeural` (Masculina, México)
- 🇦🇷 `es-AR-ElenaNeural` (Femenina, Argentina)
- 🇦🇷 `es-AR-TomasNeural` (Masculina, Argentina)

#### Opción 3: Google Cloud TTS

```javascript
const response = await fetch('https://texttospeech.googleapis.com/v1/text:synthesize?key=TU_API_KEY', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        input: { text: text },
        voice: {
            languageCode: 'es-ES',
            name: 'es-ES-Standard-A',
            ssmlGender: 'FEMALE'
        },
        audioConfig: {
            audioEncoding: 'MP3',
            speakingRate: speed
        }
    })
});

const result = await response.json();
const audioBlob = base64ToBlob(result.audioContent);
return audioBlob;
```

**Costo**: $4 por 1 millón de caracteres (~$0.004 por 1000 palabras)

### Traducción

La extensión usa **LibreTranslate** (API gratuita) por defecto. Ya está configurado en `background.js` línea 118-138.

**Alternativa - Google Translate API**:

```javascript
const response = await fetch('https://translation.googleapis.com/language/translate/v2?key=TU_API_KEY', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        q: text,
        target: 'es',
        format: 'text'
    })
});

const result = await response.json();
return result.data.translations[0].translatedText;
```

## 📁 Estructura de archivos

```
Extension-Edge-Subtitulos/
├── manifest.json          # Configuración de la extensión
├── popup.html             # Interfaz del popup
├── popup.js               # Lógica del popup
├── content.js             # Script inyectado en páginas
├── background.js          # Service worker (tareas en segundo plano)
├── styles.css             # Estilos para subtítulos
├── icons/                 # Iconos de la extensión
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md             # Este archivo
```

## 🎨 Crear iconos

Los iconos no están incluidos. Puedes crearlos con cualquier herramienta de diseño:

### Opción 1: Online (Rápido)

1. Ve a https://www.canva.com o https://www.figma.com
2. Crea un diseño cuadrado con el emoji 🎬 o texto "SUB ES"
3. Exporta en 3 tamaños: 16x16, 48x48, 128x128 píxeles
4. Guarda como PNG en la carpeta `icons/`

### Opción 2: Con código (Automático)

Crea un archivo HTML y ábrelo en el navegador:

```html
<!DOCTYPE html>
<html>
<body>
<canvas id="canvas"></canvas>
<script>
const sizes = [16, 48, 128];
sizes.forEach(size => {
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    // Fondo degradado
    const gradient = ctx.createLinearGradient(0, 0, size, size);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, size, size);

    // Emoji o texto
    ctx.fillStyle = 'white';
    ctx.font = `${size * 0.6}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🎬', size/2, size/2);

    // Descargar
    canvas.toBlob(blob => {
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `icon${size}.png`;
        a.click();
    });
});
</script>
</body>
</html>
```

## 🐛 Solución de problemas

### La extensión no detecta videos

- **Causa**: El video puede estar en un iframe con restricciones
- **Solución**: Intenta en la página principal del video, no en páginas embebidas

### Los subtítulos no se sincronizan

- **Causa**: El servicio de transcripción no devolvió timestamps precisos
- **Solución**: Usa Whisper API que proporciona timestamps palabra por palabra

### El audio TTS no se reproduce

- **Causa**: El navegador bloqueó el audio automático
- **Solución**: Dale play manualmente al video después de generar el TTS

### Error "Content script not loaded"

- **Causa**: La extensión se activó antes de que la página cargara completamente
- **Solución**: Recarga la página (F5) y vuelve a activar la extensión

### Caracteres corruptos en subtítulos

- **Causa**: Problema de codificación UTF-8
- **Solución**: Ya está solucionado en la versión actual

## 🔒 Privacidad y seguridad

- ✅ Los datos de audio **NO se almacenan** permanentemente
- ✅ Las transcripciones se guardan **localmente** en el navegador
- ✅ No se recopila información personal
- ✅ Las APIs externas pueden tener sus propias políticas de privacidad
- ⚠️ Revisa los términos de servicio de las APIs que uses (Whisper, Lokendo, etc.)

## 📝 Limitaciones actuales

- 🔄 La transcripción puede tardar 1-2 minutos para videos largos
- 🔄 La calidad depende del servicio de transcripción usado
- 🔄 Algunos sitios con protección DRM pueden no permitir captura de audio
- 🔄 La versión actual usa simulaciones - requiere configurar APIs reales

## 🚀 Próximas funciones

- [ ] Descarga de subtítulos en formato .srt
- [ ] Editor de subtítulos en tiempo real
- [ ] Soporte para múltiples idiomas (no solo español)
- [ ] Detección automática del idioma del video
- [ ] Exportación de audio TTS como archivo MP3
- [ ] Personalización de estilos de subtítulos
- [ ] Sincronización con cuentas en la nube

## 🤝 Contribuir

Si deseas contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu función (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -m 'Agregar nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto. Puedes usarlo, modificarlo y distribuirlo libremente.

## 💡 Créditos

- **Desarrollado por**: [Tu Nombre]
- **Transcripción**: OpenAI Whisper API, AssemblyAI
- **TTS**: Lokendo, Microsoft Edge TTS, Google Cloud TTS
- **Traducción**: LibreTranslate
- **Iconos**: [Tu fuente de iconos]

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:

- 📧 Email: [tu-email@ejemplo.com]
- 🐛 Issues: [URL del repositorio]/issues
- 💬 Discusiones: [URL del repositorio]/discussions

---

**¡Disfruta viendo videos en español! 🎬🇪🇸**
