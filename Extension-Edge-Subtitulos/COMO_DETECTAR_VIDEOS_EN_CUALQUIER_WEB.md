# 🎥 Cómo Video DownloadHelper Detecta Videos en CUALQUIER Sitio Web

## Análisis técnico educativo de las técnicas de detección de medios

---

## 🎯 Resumen: Las 4 técnicas principales

Video DownloadHelper combina **4 métodos** para detectar videos en cualquier sitio:

1. **Interceptar peticiones HTTP** (webRequest API) - La más potente
2. **Buscar elementos `<video>` en el DOM** (Document Object Model)
3. **Detectar streams HLS/DASH** (protocolos de streaming)
4. **Scripts específicos para sitios populares** (YouTube, Vimeo, etc.)

---

## 📡 TÉCNICA 1: Interceptar Peticiones de Red (La más importante)

### Cómo funciona:

Video DownloadHelper usa el permiso `webRequest` para **escuchar TODAS las peticiones HTTP** que hace el navegador.

### Permisos necesarios (del manifest.json):

```json
{
  "permissions": [
    "webRequest",              // Escuchar peticiones HTTP
    "declarativeNetRequest"    // Modificar/bloquear peticiones
  ],
  "host_permissions": [
    "<all_urls>"              // Acceso a todos los sitios
  ]
}
```

### Código conceptual (cómo funciona):

```javascript
// Escuchar TODAS las peticiones HTTP del navegador
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    const url = details.url;

    // ¿Es un archivo de video?
    if (isVideoUrl(url)) {
      console.log("¡Video detectado!", url);
      saveVideoUrl(url, details);
    }
  },
  { urls: ["<all_urls>"] },  // En todos los sitios
  ["requestBody"]
);

// Función para detectar si una URL es un video
function isVideoUrl(url) {
  // Extensiones de video comunes
  const videoExtensions = [
    '.mp4', '.webm', '.m4v', '.avi', '.mov',
    '.flv', '.wmv', '.mkv', '.ts', '.m3u8'
  ];

  // ¿Termina en extensión de video?
  if (videoExtensions.some(ext => url.includes(ext))) {
    return true;
  }

  // ¿Es un stream HLS (Apple)?
  if (url.includes('.m3u8')) {
    return true;
  }

  // ¿Es un stream DASH (YouTube, Netflix)?
  if (url.includes('.mpd')) {
    return true;
  }

  // ¿Tiene parámetros de video?
  if (url.includes('video') || url.includes('stream')) {
    return true;
  }

  // Detectar por Content-Type (en onHeadersReceived)
  return false;
}
```

### Ejemplo real:

Cuando visitas una página con un video:

```
1. Navegador solicita: https://example.com/video.mp4
                       ↓
2. Video DownloadHelper intercepta la petición
                       ↓
3. Detecta ".mp4" en la URL
                       ↓
4. Guarda la URL del video
                       ↓
5. Muestra ícono activo y opción de descarga
```

---

## 🔍 TÉCNICA 2: Buscar Elementos `<video>` en el DOM

### Cómo funciona:

Inyecta scripts en páginas web que buscan **etiquetas HTML de video**.

### Código conceptual:

```javascript
// Content script inyectado en TODAS las páginas
(function detectVideoElements() {

  // Buscar todos los elementos <video>
  const videos = document.querySelectorAll('video');

  videos.forEach(video => {
    console.log("Video element found:", video);

    // Obtener la fuente del video
    let src = video.src;

    // Si no tiene src directo, buscar en <source>
    if (!src) {
      const source = video.querySelector('source');
      if (source) {
        src = source.src;
      }
    }

    // Si tiene src, reportar al background
    if (src) {
      chrome.runtime.sendMessage({
        action: 'video-detected',
        url: src,
        type: 'html5-video'
      });
    }

    // Monitorear cambios en el src (videos dinámicos)
    const observer = new MutationObserver(() => {
      if (video.src && video.src !== src) {
        src = video.src;
        chrome.runtime.sendMessage({
          action: 'video-detected',
          url: src,
          type: 'html5-video-dynamic'
        });
      }
    });

    observer.observe(video, {
      attributes: true,
      attributeFilter: ['src']
    });
  });

  // Observar el DOM por nuevos videos (páginas SPA)
  const domObserver = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (node.tagName === 'VIDEO') {
          // Nuevo video agregado dinámicamente
          detectVideoFromElement(node);
        }
      });
    });
  });

  domObserver.observe(document.body, {
    childList: true,
    subtree: true
  });

})();
```

### Ejemplo:

```html
<!-- Página web típica -->
<video id="my-video" controls>
  <source src="https://example.com/movie.mp4" type="video/mp4">
  <source src="https://example.com/movie.webm" type="video/webm">
</video>
```

El content script detecta automáticamente:
- ✅ El elemento `<video>`
- ✅ Las URLs de las fuentes (`movie.mp4`, `movie.webm`)
- ✅ Cambios dinámicos (si el video cambia de src)

---

## 📺 TÉCNICA 3: Detectar Streams HLS y DASH

### ¿Qué son HLS y DASH?

- **HLS (HTTP Live Streaming)** - Formato de Apple, usado en iOS, Twitch
- **DASH (Dynamic Adaptive Streaming)** - Usado por YouTube, Netflix

Estos NO son archivos de video únicos, sino **playlists** que apuntan a fragmentos de video.

### Detección de HLS (.m3u8):

```javascript
// Detectar playlists HLS
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    const url = details.url;

    // ¿Es una playlist HLS?
    if (url.endsWith('.m3u8') || url.includes('m3u8')) {
      console.log("HLS stream detected:", url);

      // Descargar y parsear el archivo .m3u8
      fetch(url)
        .then(response => response.text())
        .then(playlist => {
          // El .m3u8 contiene URLs de los fragmentos
          const segments = parseM3U8(playlist);

          chrome.runtime.sendMessage({
            action: 'hls-stream-detected',
            masterUrl: url,
            segments: segments
          });
        });
    }
  },
  { urls: ["<all_urls>"] }
);

// Parser simple de M3U8
function parseM3U8(content) {
  const lines = content.split('\n');
  const segments = [];

  lines.forEach(line => {
    // Las URLs de fragmentos no empiezan con #
    if (!line.startsWith('#') && line.trim()) {
      segments.push(line.trim());
    }
  });

  return segments;
}
```

### Ejemplo de archivo .m3u8:

```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment0.ts
#EXTINF:10.0,
segment1.ts
#EXTINF:10.0,
segment2.ts
#EXT-X-ENDLIST
```

La extensión:
1. Detecta la URL del `.m3u8`
2. Descarga el archivo
3. Parsea las URLs de los fragmentos (`.ts`)
4. Puede descargar todos los fragmentos y unirlos con FFmpeg

---

## 🎬 TÉCNICA 4: Scripts Específicos para Sitios Populares

### Por qué se necesita:

Algunos sitios usan técnicas especiales que requieren código personalizado:
- **YouTube**: Usa DASH cifrado y API interna
- **Vimeo**: Autenticación por tokens
- **Facebook**: Videos fragmentados con protección

### Ejemplo: Detector para YouTube

Según el manifest.json, inyecta `injected/youtube.js` en `*.youtube.com`:

```javascript
// injected/youtube.js (conceptual)
(function detectYouTubeVideo() {

  // YouTube almacena datos del video en window.ytInitialPlayerResponse
  function getVideoInfo() {
    if (window.ytInitialPlayerResponse) {
      const playerData = window.ytInitialPlayerResponse;

      // Extraer formatos disponibles
      const formats = playerData.streamingData?.formats || [];
      const adaptiveFormats = playerData.streamingData?.adaptiveFormats || [];

      const allFormats = [...formats, ...adaptiveFormats];

      // Enviar al background
      chrome.runtime.sendMessage({
        action: 'youtube-video-detected',
        videoId: playerData.videoDetails.videoId,
        title: playerData.videoDetails.title,
        formats: allFormats.map(f => ({
          url: f.url,
          quality: f.qualityLabel,
          mimeType: f.mimeType,
          bitrate: f.bitrate
        }))
      });
    }
  }

  // Ejecutar al cargar la página
  getVideoInfo();

  // Monitorear navegación SPA de YouTube
  let lastUrl = location.href;
  new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      setTimeout(getVideoInfo, 1000); // Esperar a que cargue
    }
  }).observe(document, { subtree: true, childList: true });

})();
```

---

## 🧩 Cómo se Combinan las 4 Técnicas

```
Usuario visita: https://example.com/watch?v=abc123
                        ↓
┌───────────────────────────────────────────────────────┐
│  TÉCNICA 1: Interceptar peticiones HTTP              │
│  ✓ Detecta: video.mp4, stream.m3u8                   │
└───────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────┐
│  TÉCNICA 2: Buscar elementos <video> en DOM          │
│  ✓ Detecta: <video src="...">                        │
└───────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────┐
│  TÉCNICA 3: Parsear streams HLS/DASH                 │
│  ✓ Descarga .m3u8 y extrae fragmentos                │
└───────────────────────────────────────────────────────┘
                        ↓
┌───────────────────────────────────────────────────────┐
│  TÉCNICA 4: Script específico del sitio              │
│  ✓ YouTube: Extrae de ytInitialPlayerResponse        │
│  ✓ Vimeo: Usa API interna                            │
└───────────────────────────────────────────────────────┘
                        ↓
            ¡Video(s) detectado(s)!
```

---

## 💻 Cómo Implementarlo en Tu Extensión

### Paso 1: Agregar permisos al manifest.json

```json
{
  "manifest_version": 3,
  "name": "Mi Detector de Videos",
  "permissions": [
    "webRequest",
    "declarativeNetRequest",
    "storage"
  ],
  "host_permissions": [
    "<all_urls>"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "run_at": "document_end"
  }]
}
```

### Paso 2: background.js - Interceptar peticiones

```javascript
// Tipos MIME de video
const VIDEO_MIME_TYPES = [
  'video/mp4',
  'video/webm',
  'video/ogg',
  'video/quicktime',
  'application/x-mpegURL', // HLS
  'application/vnd.apple.mpegurl', // HLS
  'application/dash+xml' // DASH
];

// Extensiones de video
const VIDEO_EXTENSIONS = [
  '.mp4', '.webm', '.m4v', '.avi', '.mov',
  '.flv', '.wmv', '.mkv', '.m3u8', '.mpd', '.ts'
];

// Almacenar videos detectados
let detectedVideos = {};

// Interceptar peticiones
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    const url = details.url;

    // Verificar si es video por extensión
    const isVideoByExtension = VIDEO_EXTENSIONS.some(ext =>
      url.toLowerCase().includes(ext)
    );

    if (isVideoByExtension) {
      storeVideo(details.tabId, url, 'extension');
    }
  },
  { urls: ["<all_urls>"] }
);

// Interceptar headers para verificar Content-Type
chrome.webRequest.onHeadersReceived.addListener(
  function(details) {
    const headers = details.responseHeaders;
    const contentType = headers.find(h =>
      h.name.toLowerCase() === 'content-type'
    );

    if (contentType) {
      const isVideo = VIDEO_MIME_TYPES.some(mime =>
        contentType.value.includes(mime)
      );

      if (isVideo) {
        storeVideo(details.tabId, details.url, 'mime-type');
      }
    }
  },
  { urls: ["<all_urls>"] },
  ["responseHeaders"]
);

function storeVideo(tabId, url, source) {
  if (!detectedVideos[tabId]) {
    detectedVideos[tabId] = [];
  }

  // Evitar duplicados
  if (!detectedVideos[tabId].find(v => v.url === url)) {
    detectedVideos[tabId].push({
      url: url,
      source: source,
      timestamp: Date.now()
    });

    console.log(`Video detected [${source}]:`, url);

    // Actualizar ícono de la extensión
    updateIcon(tabId);
  }
}

function updateIcon(tabId) {
  const count = detectedVideos[tabId]?.length || 0;

  if (count > 0) {
    chrome.action.setBadgeText({
      tabId: tabId,
      text: count.toString()
    });
    chrome.action.setBadgeBackgroundColor({
      tabId: tabId,
      color: '#4CAF50'
    });
  }
}
```

### Paso 3: content.js - Buscar en el DOM

```javascript
(function() {
  'use strict';

  // Detectar elementos <video>
  function detectVideoElements() {
    const videos = document.querySelectorAll('video');

    videos.forEach(video => {
      const src = video.src || video.querySelector('source')?.src;

      if (src) {
        chrome.runtime.sendMessage({
          action: 'video-detected',
          url: src,
          type: 'html5-video'
        });
      }
    });
  }

  // Ejecutar al cargar
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', detectVideoElements);
  } else {
    detectVideoElements();
  }

  // Observar nuevos videos
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      mutation.addedNodes.forEach(node => {
        if (node.tagName === 'VIDEO') {
          const src = node.src || node.querySelector('source')?.src;
          if (src) {
            chrome.runtime.sendMessage({
              action: 'video-detected',
              url: src,
              type: 'html5-video-dynamic'
            });
          }
        }
      });
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

})();
```

---

## 🎓 Conceptos Clave para Aprender

### 1. **webRequest API**
- Permite interceptar TODAS las peticiones HTTP
- Es la técnica más potente
- Requiere permiso `<all_urls>`

### 2. **Content Scripts**
- JavaScript inyectado en páginas web
- Puede acceder al DOM (elementos HTML)
- Se ejecuta en contexto aislado

### 3. **Tipos de streams**
- **Descarga progresiva**: Un solo archivo `.mp4`
- **HLS**: Playlist `.m3u8` con fragmentos `.ts`
- **DASH**: Manifest `.mpd` con fragmentos

### 4. **MIME Types**
- `video/mp4` - Video MP4
- `video/webm` - Video WebM
- `application/x-mpegURL` - Stream HLS

---

## 📊 Comparación de Técnicas

| Técnica | Ventajas | Desventajas |
|---------|----------|-------------|
| **webRequest** | Detecta TODO, incluso videos ocultos | Requiere permisos amplios |
| **DOM parsing** | Simple, funciona en HTML estándar | No detecta streams |
| **HLS/DASH** | Funciona con streaming | Requiere parser |
| **Scripts específicos** | Máxima compatibilidad | Mantenimiento por sitio |

---

## ✅ Resumen Final

Video DownloadHelper detecta videos combinando:

1. **Escuchar peticiones HTTP** → Detecta archivos `.mp4`, `.m3u8`, etc.
2. **Buscar `<video>` en HTML** → Detecta reproductores HTML5
3. **Parsear playlists HLS/DASH** → Detecta streaming
4. **Scripts por sitio** → YouTube, Vimeo, Facebook

**La clave**: Usar `webRequest` para interceptar TODO el tráfico HTTP y filtrar por:
- Extensiones de archivo (`.mp4`, `.webm`)
- Content-Type headers (`video/*`)
- Patrones en URLs (`/video/`, `/stream/`)

---

## 🚀 Próximos Pasos

¿Quieres implementar esto en tu extensión de subtítulos?

Podemos agregar:
- ✅ Detección automática de videos (sin activar manualmente)
- ✅ Soporte para streams HLS/DASH
- ✅ Funcionar en sitios sin `<video>` tags
- ✅ Detección en sitios de cursos, Vimeo, etc.

¿Te interesa?
