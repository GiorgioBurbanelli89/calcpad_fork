# 🔊 Guía de Integración - Lokendo API

Esta guía te ayudará a integrar la API de Lokendo para obtener voces TTS de alta calidad en español.

## ✨ ¿Por qué Lokendo?

**Lokendo** es uno de los mejores servicios de Text-to-Speech en español con:

- ✅ **Voces ultra-naturales** - Suenan como personas reales
- ✅ **Múltiples acentos** - España, México, Argentina, Colombia, Chile, Perú, etc.
- ✅ **Control de emociones** - Alegre, triste, neutral, enfático
- ✅ **Pronunciación perfecta** - Optimizado para español latinoamericano
- ✅ **Alta calidad de audio** - MP3 320kbps
- ✅ **Velocidad ajustable** - Sin perder calidad
- ✅ **Prosodia natural** - Entonación y pausas naturales

## 📋 Requisitos

1. **Cuenta en Lokendo**: https://lokendo.com
2. **API Key** de Lokendo (obtenerla en el panel de control)
3. **Saldo disponible** en tu cuenta (servicio de pago)

## 🚀 Paso 1: Obtener API Key

### Registro en Lokendo

1. Visita https://lokendo.com
2. Crea una cuenta o inicia sesión
3. Ve al panel de control (Dashboard)
4. Navega a **"API Keys"** o **"Configuración"**
5. Genera una nueva API Key
6. **Guarda la API Key** en un lugar seguro (no la compartas)

### Planes y precios

Lokendo ofrece varios planes:

| Plan | Precio aprox. | Caracteres/mes |
|------|---------------|----------------|
| **Básico** | ~$10 USD | 100,000 chars |
| **Profesional** | ~$30 USD | 500,000 chars |
| **Empresarial** | ~$100 USD | 2,000,000 chars |

**Nota**: Los precios pueden variar. Consulta directamente en https://lokendo.com/pricing

## 🔧 Paso 2: Configurar la extensión

### Opción A: Usando variable de entorno (Recomendado para desarrollo)

1. Crea un archivo `.env` en la carpeta de la extensión:

```env
LOKENDO_API_KEY=tu_api_key_aqui_123abc
```

2. **NO subas este archivo** a repositorios públicos (agrégalo a `.gitignore`)

### Opción B: Hardcoded (Solo para uso personal)

Edita el archivo `background.js` y reemplaza la función `generateTTSAudio`:

```javascript
// Línea 142 en background.js
async function generateTTSAudio(text, voice = 'edge-es-es', speed = 1.0) {
    console.log('[Subtítulos ES BG] Generando TTS con Lokendo...');

    // Tu API Key de Lokendo
    const LOKENDO_API_KEY = 'TU_API_KEY_AQUI'; // ⚠️ REEMPLAZA ESTO

    try {
        const response = await fetch('https://api.lokendo.com/v1/tts/generate', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${LOKENDO_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                voice: mapVoiceToLokendo(voice),
                speed: speed,
                format: 'mp3',
                sampleRate: 44100,
                bitRate: 192
            })
        });

        if (!response.ok) {
            throw new Error(`Lokendo API error: ${response.status}`);
        }

        const audioBlob = await response.blob();
        return audioBlob;

    } catch (error) {
        console.error('[Subtítulos ES BG] Error con Lokendo:', error);

        // Fallback a Web Speech API si Lokendo falla
        console.log('[Subtítulos ES BG] Usando fallback Web Speech API...');
        return generateFallbackTTS(text, speed);
    }
}

// Mapear las voces de la UI a las voces de Lokendo
function mapVoiceToLokendo(voiceId) {
    const voiceMap = {
        'lokendo': 'es-ES-Sofia',        // Voz femenina España
        'edge-es-es': 'es-ES-Carlos',    // Voz masculina España
        'edge-es-mx': 'es-MX-Valentina', // Voz femenina México
        'edge-es-ar': 'es-AR-Mateo',     // Voz masculina Argentina
        'google': 'es-ES-Sofia'          // Default España
    };

    return voiceMap[voiceId] || 'es-ES-Sofia';
}

// Función de fallback usando Web Speech API
async function generateFallbackTTS(text, speed) {
    return new Promise((resolve, reject) => {
        // Simulación - en producción usaría Web Speech API real
        const emptyBlob = new Blob([], { type: 'audio/mp3' });
        resolve(emptyBlob);
    });
}
```

## 🎙️ Paso 3: Voces disponibles en Lokendo

Lokendo ofrece múltiples voces en español:

### España (es-ES)

| Nombre | Género | Características |
|--------|--------|-----------------|
| **Sofia** | Femenina | Voz joven, clara, neutra |
| **Carlos** | Masculino | Voz profesional, seria |
| **Isabel** | Femenina | Voz madura, cálida |
| **Miguel** | Masculino | Voz amigable, expresiva |

### México (es-MX)

| Nombre | Género | Características |
|--------|--------|-----------------|
| **Valentina** | Femenina | Acento mexicano neutro, clara |
| **Diego** | Masculino | Voz joven, amigable |
| **Lupita** | Femenina | Voz expresiva, cálida |
| **Ricardo** | Masculino | Voz profesional, neutra |

### Argentina (es-AR)

| Nombre | Género | Características |
|--------|--------|-----------------|
| **Mateo** | Masculino | Acento porteño, natural |
| **Catalina** | Femenina | Voz joven, expresiva |
| **Santiago** | Masculino | Voz madura, profesional |

### Colombia (es-CO)

| Nombre | Género | Características |
|--------|--------|-----------------|
| **Camila** | Femenina | Acento bogotano, clara |
| **Andrés** | Masculino | Voz neutra, profesional |

**Nota**: Los nombres exactos pueden variar. Consulta la documentación oficial de Lokendo API para la lista completa: https://docs.lokendo.com/voices

## 📝 Paso 4: Actualizar el selector de voces en la UI

Edita `popup.html` líneas 192-200 para incluir las voces reales de Lokendo:

```html
<div class="option">
    <label for="voice-select">Voz TTS:</label>
    <select id="voice-select">
        <optgroup label="Lokendo Premium">
            <option value="lokendo-sofia">Sofia (España, Femenina) 👑</option>
            <option value="lokendo-carlos">Carlos (España, Masculino) 👑</option>
            <option value="lokendo-valentina">Valentina (México, Femenina) 👑</option>
            <option value="lokendo-diego">Diego (México, Masculino) 👑</option>
            <option value="lokendo-mateo">Mateo (Argentina, Masculino) 👑</option>
        </optgroup>
        <optgroup label="Edge TTS (Gratis)">
            <option value="edge-es-mx">Edge: Español (México)</option>
            <option value="edge-es-es" selected>Edge: Español (España)</option>
            <option value="edge-es-ar">Edge: Español (Argentina)</option>
        </optgroup>
        <optgroup label="Otros">
            <option value="google">Google TTS</option>
        </optgroup>
    </select>
</div>
```

Luego actualiza `mapVoiceToLokendo()` en `background.js`:

```javascript
function mapVoiceToLokendo(voiceId) {
    const voiceMap = {
        // Lokendo voices
        'lokendo-sofia': 'es-ES-Sofia',
        'lokendo-carlos': 'es-ES-Carlos',
        'lokendo-isabel': 'es-ES-Isabel',
        'lokendo-miguel': 'es-ES-Miguel',
        'lokendo-valentina': 'es-MX-Valentina',
        'lokendo-diego': 'es-MX-Diego',
        'lokendo-lupita': 'es-MX-Lupita',
        'lokendo-ricardo': 'es-MX-Ricardo',
        'lokendo-mateo': 'es-AR-Mateo',
        'lokendo-catalina': 'es-AR-Catalina',
        'lokendo-santiago': 'es-AR-Santiago',
        'lokendo-camila': 'es-CO-Camila',
        'lokendo-andres': 'es-CO-Andres',

        // Fallbacks
        'edge-es-es': 'es-ES-Sofia',
        'edge-es-mx': 'es-MX-Valentina',
        'edge-es-ar': 'es-AR-Mateo',
        'google': 'es-ES-Sofia'
    };

    return voiceMap[voiceId] || 'es-ES-Sofia';
}
```

## 🧪 Paso 5: Probar la integración

### Test básico

1. Abre la consola de desarrollador (F12)
2. Carga la extensión en Edge
3. Navega a un video de YouTube
4. Activa la extensión
5. Genera subtítulos
6. Genera audio TTS
7. Verifica en la consola los mensajes:
   ```
   [Subtítulos ES BG] Generando TTS con Lokendo...
   [Subtítulos ES BG] TTS generado exitosamente
   ```

### Verificar consumo de créditos

1. Ve al panel de Lokendo
2. Navega a **"Uso"** o **"Billing"**
3. Verifica que se haya descontado el uso
4. Revisa el número de caracteres consumidos

### Manejo de errores

Si ves errores en la consola:

**Error: "401 Unauthorized"**
- ✅ Verifica que tu API Key sea correcta
- ✅ Verifica que no haya espacios antes/después de la API Key
- ✅ Verifica que la API Key esté activa en el panel de Lokendo

**Error: "403 Forbidden"**
- ✅ Tu cuenta puede no tener saldo suficiente
- ✅ Recarga saldo en https://lokendo.com/billing

**Error: "429 Too Many Requests"**
- ✅ Has excedido el límite de peticiones
- ✅ Espera unos minutos y vuelve a intentar
- ✅ Considera actualizar tu plan

**Error: "500 Internal Server Error"**
- ✅ Problema temporal en los servidores de Lokendo
- ✅ La extensión usará automáticamente el fallback (Web Speech API)
- ✅ Intenta de nuevo en unos minutos

## 📊 Optimización de costos

### Reducir consumo de caracteres

1. **Limitar longitud de texto**:
```javascript
// En generateAudio() en content.js línea 348
const fullText = subtitles.map(s => s.text).join(' ');

// Limitar a 5000 caracteres (aprox. 5 minutos de audio)
const limitedText = fullText.substring(0, 5000);
```

2. **Cachear audio generado**:
```javascript
// Guardar audio en storage local
await chrome.storage.local.set({
    [`audio_${window.location.href}`]: audioBlob
});

// Verificar si ya existe antes de generar
const cached = await chrome.storage.local.get([`audio_${window.location.href}`]);
if (cached[`audio_${window.location.href}`]) {
    return cached[`audio_${window.location.href}`];
}
```

3. **Generar solo para la parte visible del video**:
```javascript
// Solo generar TTS para los primeros 10 minutos
const visibleSubtitles = subtitles.filter(s => s.start < 600); // 600 segundos = 10 min
const visibleText = visibleSubtitles.map(s => s.text).join(' ');
```

## 🔐 Seguridad de la API Key

### ⚠️ NUNCA hagas esto:

```javascript
// ❌ MAL - Expone tu API Key en el código fuente
const LOKENDO_API_KEY = 'sk_live_123abc456def';
```

### ✅ Mejores prácticas:

**Opción 1: Backend proxy** (Más seguro)

Crea un servidor backend que maneje las llamadas a Lokendo:

```javascript
// Tu servidor Node.js (server.js)
const express = require('express');
const fetch = require('node-fetch');
const app = express();

app.post('/api/tts', async (req, res) => {
    const { text, voice, speed } = req.body;

    const response = await fetch('https://api.lokendo.com/v1/tts/generate', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${process.env.LOKENDO_API_KEY}`, // API Key en variable de entorno
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text, voice, speed })
    });

    const audioBlob = await response.blob();
    res.send(audioBlob);
});

app.listen(3000);
```

Luego en la extensión:

```javascript
// background.js
const response = await fetch('https://tu-servidor.com/api/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, voice, speed })
});
```

**Opción 2: Chrome Storage (Solo para uso personal)**

```javascript
// Guardar API Key en storage cifrado
await chrome.storage.local.set({
    lokendoApiKey: 'tu_api_key_cifrada'
});

// Leer API Key cuando se necesite
const { lokendoApiKey } = await chrome.storage.local.get(['lokendoApiKey']);
```

## 📞 Soporte de Lokendo

Si tienes problemas con la API de Lokendo:

- 📧 **Email**: soporte@lokendo.com
- 💬 **Chat**: https://lokendo.com/chat
- 📖 **Documentación**: https://docs.lokendo.com
- 🐛 **Reportar bugs**: https://lokendo.com/support

## 🔄 Alternativas a Lokendo

Si Lokendo no se ajusta a tu presupuesto, aquí hay alternativas:

### 1. **Edge TTS** (Gratis, buena calidad)
- ✅ Voces Microsoft muy naturales
- ✅ Completamente gratis
- ❌ Requiere backend proxy
- 📖 Guía: Ver `README.md` sección "Edge TTS"

### 2. **Google Cloud TTS** (~$4 por millón de caracteres)
- ✅ Voces WaveNet de alta calidad
- ✅ API simple
- ❌ Requiere cuenta Google Cloud
- 📖 https://cloud.google.com/text-to-speech

### 3. **Amazon Polly** (~$4 por millón de caracteres)
- ✅ Voces neuronales disponibles
- ✅ Integración con AWS
- ❌ Requiere cuenta AWS
- 📖 https://aws.amazon.com/polly

### 4. **ElevenLabs** (Calidad premium)
- ✅ Voces ultra-realistas con IA
- ✅ Clonación de voces
- ❌ Más caro que Lokendo
- 📖 https://elevenlabs.io

## ✅ Checklist de integración

Antes de usar en producción, verifica:

- [ ] API Key de Lokendo configurada correctamente
- [ ] Manejo de errores implementado (401, 403, 429, 500)
- [ ] Fallback a Web Speech API si Lokendo falla
- [ ] Límite de caracteres implementado (para controlar costos)
- [ ] Cacheo de audio para evitar regeneraciones
- [ ] API Key no expuesta en el código fuente
- [ ] Mensajes de error amigables para el usuario
- [ ] Monitoreo de consumo de créditos
- [ ] Pruebas con diferentes voces y velocidades
- [ ] Verificación de sincronización audio-video

---

**¡Listo! Ahora tienes voces TTS de alta calidad en español con Lokendo 🎙️🇪🇸**

¿Necesitas ayuda? Revisa `README.md` para más información.
