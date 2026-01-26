# 🚀 Inicio Rápido - Extensión de Subtítulos en Español

Esta guía te ayudará a tener la extensión funcionando en **menos de 5 minutos**.

## ⚡ Instalación Express

### 1. Crear los iconos (30 segundos)

Abre el archivo `generar_iconos.html` en tu navegador Chrome/Edge y los iconos se descargarán automáticamente.

O copia este código en un archivo HTML y ábrelo:

```html
<!DOCTYPE html>
<html>
<head><title>Generar Iconos</title></head>
<body>
<h1>Generando iconos...</h1>
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

    // Emoji
    ctx.font = `${size * 0.7}px Arial`;
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
document.body.innerHTML = '<h1 style="color:green">✅ Iconos descargados!</h1><p>Mueve los archivos icon16.png, icon48.png e icon128.png a la carpeta icons/</p>';
</script>
</body>
</html>
```

Guarda los archivos `icon16.png`, `icon48.png` e `icon128.png` en la carpeta `icons/` dentro de `Extension-Edge-Subtitulos/`.

### 2. Cargar la extensión en Edge (1 minuto)

1. Abre Microsoft Edge
2. Escribe en la barra de direcciones: `edge://extensions/`
3. Activa el interruptor **"Modo de desarrollador"** (esquina inferior izquierda)
4. Haz clic en **"Cargar extensión desempaquetada"**
5. Selecciona la carpeta `Extension-Edge-Subtitulos`
6. ✅ ¡Listo! Verás el icono 🎬 en tu barra de herramientas

### 3. Prueba básica (2 minutos)

1. Ve a YouTube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
2. Haz clic en el icono 🎬 de la extensión
3. Clic en **"Activar en esta página"**
4. Espera a que detecte el video
5. Los subtítulos aparecerán automáticamente (en modo simulación)

**Nota**: En esta versión de desarrollo, la transcripción es simulada. Para usar transcripción real, necesitas configurar una API (ver más abajo).

## 🎯 Configuración Básica (Modo Desarrollo)

La extensión funciona en modo simulación sin necesidad de APIs. Para probarlo:

1. **Activa la extensión** en cualquier página con video
2. **Genera subtítulos** - verás texto de ejemplo
3. **Genera audio TTS** - usará Web Speech API del navegador (gratis)

**Limitaciones del modo simulación**:
- ❌ El texto de los subtítulos es genérico (no transcribe el audio real)
- ❌ El TTS usa voces del navegador (calidad básica)
- ✅ Funciona offline
- ✅ No requiere API keys
- ✅ Perfecto para probar la UI y funcionalidad básica

## 🔧 Configuración Avanzada (APIs Reales)

### Opción 1: Solo TTS (Más fácil)

Si solo quieres mejorar la calidad del audio TTS pero dejar la transcripción simulada:

**Usar Edge TTS (Gratis)**

1. Instala Python: https://www.python.org/downloads/
2. Instala edge-tts:
   ```bash
   pip install edge-tts flask flask-cors
   ```

3. Crea un archivo `tts_server.py`:
   ```python
   from flask import Flask, request, send_file
   from flask_cors import CORS
   import edge_tts
   import asyncio
   import os

   app = Flask(__name__)
   CORS(app)

   @app.route('/tts', methods=['POST'])
   def generate_tts():
       data = request.json
       text = data['text']
       voice = data.get('voice', 'es-ES-AlvaroNeural')
       speed = data.get('speed', 1.0)

       # Ajustar velocidad para edge-tts (formato: +X% o -X%)
       rate = f"+{int((speed - 1) * 100)}%" if speed > 1 else f"{int((speed - 1) * 100)}%"

       # Generar audio
       async def generate():
           communicate = edge_tts.Communicate(text, voice, rate=rate)
           await communicate.save("output.mp3")

       asyncio.run(generate())

       return send_file("output.mp3", mimetype="audio/mpeg")

   if __name__ == '__main__':
       app.run(port=5000)
   ```

4. Ejecuta el servidor:
   ```bash
   python tts_server.py
   ```

5. Edita `background.js` línea 142 y reemplaza con:
   ```javascript
   async function generateTTSAudio(text, voice = 'edge-es-es', speed = 1.0) {
       try {
           const voiceMap = {
               'edge-es-es': 'es-ES-AlvaroNeural',
               'edge-es-mx': 'es-MX-DaliaNeural',
               'edge-es-ar': 'es-AR-ElenaNeural'
           };

           const response = await fetch('http://localhost:5000/tts', {
               method: 'POST',
               headers: { 'Content-Type': 'application/json' },
               body: JSON.stringify({
                   text: text,
                   voice: voiceMap[voice] || 'es-ES-AlvaroNeural',
                   speed: speed
               })
           });

           const audioBlob = await response.blob();
           return audioBlob;
       } catch (e) {
           console.error('Error con Edge TTS:', e);
           return new Blob([], { type: 'audio/mp3' });
       }
   }
   ```

6. ✅ ¡Listo! Ahora tienes TTS de alta calidad gratis

### Opción 2: Transcripción + TTS (Completo)

Para transcripción real del audio del video, necesitas una API de transcripción.

**Opción más fácil: OpenAI Whisper API**

1. Crea una cuenta en OpenAI: https://platform.openai.com/signup
2. Agrega saldo (mínimo $5): https://platform.openai.com/account/billing
3. Genera una API Key: https://platform.openai.com/account/api-keys
4. Copia tu API Key (empieza con `sk-`)

5. Edita `background.js` línea 67 y reemplaza:
   ```javascript
   async function transcribeWithExternalAPI(audioBlob, language = 'es') {
       const OPENAI_API_KEY = 'sk-TU_API_KEY_AQUI'; // ⚠️ REEMPLAZA ESTO

       const formData = new FormData();
       formData.append('file', audioBlob, 'audio.webm');
       formData.append('model', 'whisper-1');
       formData.append('language', 'es');

       try {
           const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
               method: 'POST',
               headers: {
                   'Authorization': `Bearer ${OPENAI_API_KEY}`
               },
               body: formData
           });

           const result = await response.json();

           // Dividir en segmentos de 5 segundos
           const words = result.text.split(' ');
           const timestamps = [];
           const wordsPerSegment = 10;

           for (let i = 0; i < words.length; i += wordsPerSegment) {
               const segment = words.slice(i, i + wordsPerSegment).join(' ');
               timestamps.push({
                   start: (i / wordsPerSegment) * 5,
                   end: ((i + wordsPerSegment) / wordsPerSegment) * 5,
                   text: segment
               });
           }

           return {
               text: result.text,
               timestamps: timestamps
           };
       } catch (e) {
           console.error('Error con Whisper API:', e);
           throw e;
       }
   }
   ```

6. Recarga la extensión en `edge://extensions/`
7. ✅ ¡Ahora transcribe audio real!

**Costo**: ~$0.006 por minuto de audio (muy económico)

### Opción 3: Todo Premium (Lokendo)

Para la mejor calidad de TTS con voces ultra-naturales:

1. Sigue la guía completa en `INTEGRACION_LOKENDO.md`
2. Obtén una API Key de Lokendo: https://lokendo.com
3. Configura el backend proxy para seguridad
4. ✅ Voces premium de calidad profesional

**Costo**: Desde ~$10/mes según uso

## 🎓 Casos de uso

### Caso 1: Ver cursos en inglés en español
1. Ve a Udemy, Coursera, edX, etc.
2. Activa la extensión
3. El curso se transcribirá y traducirá al español
4. Audio en español con voces naturales

### Caso 2: YouTube en español
1. Videos en inglés, francés, alemán, etc.
2. Subtítulos automáticos en español
3. Audio doblado al español

### Caso 3: Reuniones grabadas
1. Grabaciones de Zoom, Meet, Teams
2. Transcripción automática
3. Audio en español para mayor comprensión

## ❓ FAQ Rápido

**P: ¿Funciona offline?**
R: En modo simulación sí. Para transcripción/TTS real necesitas internet.

**P: ¿Es gratis?**
R: El código de la extensión es gratis. Las APIs tienen costos:
- Edge TTS: Gratis
- Whisper API: ~$0.006/minuto
- Lokendo: Desde $10/mes

**P: ¿Funciona en Netflix/Prime Video?**
R: Puede tener limitaciones por DRM. Funciona mejor en YouTube, Vimeo, cursos.

**P: ¿Qué navegadores soporta?**
R: Microsoft Edge, Google Chrome (con ajustes menores al manifest)

**P: ¿Guarda mis datos?**
R: Solo localmente en tu navegador. Nada se envía a servidores externos (excepto las APIs que configures).

## 🐛 Problemas comunes

**"Content script not loaded"**
→ Recarga la página (F5) y activa de nuevo

**"No se encontraron videos"**
→ El sitio puede usar un reproductor personalizado. Prueba en YouTube primero.

**Los subtítulos no se sincronizan**
→ La transcripción simulada no tiene timestamps reales. Usa Whisper API para timestamps precisos.

**El audio TTS no suena natural**
→ Estás usando Web Speech API del navegador. Configura Edge TTS o Lokendo para mejor calidad.

**Error 401/403 en la API**
→ Verifica tu API Key y saldo disponible

## 📚 Próximos pasos

Una vez que la extensión funcione:

1. **Lee `README.md`** para documentación completa
2. **Lee `INTEGRACION_LOKENDO.md`** si quieres voces premium
3. **Personaliza** las voces y velocidades según tu preferencia
4. **Comparte** la extensión con amigos que necesiten subtítulos en español

## 💡 Consejos

- ✅ Usa Edge TTS para mejor calidad gratuita
- ✅ Whisper API es muy económico (~$0.36 por hora de video)
- ✅ Cachea los subtítulos para no regenerar
- ✅ Prueba diferentes voces para encontrar tu favorita
- ✅ Ajusta la velocidad según tu velocidad de lectura

---

**¡Disfruta viendo videos en español! 🎬🇪🇸**

¿Necesitas ayuda? Consulta `README.md` o abre un issue en el repositorio.
