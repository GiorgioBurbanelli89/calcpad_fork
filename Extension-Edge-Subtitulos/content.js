// content.js - Detector AGRESIVO de videos HD con intercepción de MediaSource
// Version 2.4 - Con traducción automática de transcripts

(function() {
    'use strict';

    console.log('[Video Detector HD] Content script cargado en:', window.location.href);

    let detectedVideosDOM = new Set();
    let capturedStreamUrls = new Map(); // Almacenar URLs de streams capturadas
    let detectionInterval = null;
    let translationCache = new Map(); // Cache de traducciones
    let translationObserver = null; // Observer para detectar cambios en transcript

    // ==================== TRADUCCIÓN AUTOMÁTICA PARA THAT OPEN PEOPLE ====================

    const isThatOpenPeople = window.location.hostname.includes('thatopen') ||
                             window.location.hostname.includes('people.thatopen') ||
                             window.location.hostname.includes('circle.so');

    console.log('[Traductor] Hostname:', window.location.hostname, '| Es That Open:', isThatOpenPeople);

    // Función para traducir texto usando Google Translate (gratis, sin API key)
    async function translateToSpanish(text) {
        if (!text || text.length < 3) return text;

        // Verificar cache
        const cacheKey = text.substring(0, 100);
        if (translationCache.has(cacheKey)) {
            return translationCache.get(cacheKey);
        }

        try {
            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q=${encodeURIComponent(text)}`;
            const response = await fetch(url);
            const data = await response.json();

            let translated = '';
            if (data && data[0]) {
                for (const part of data[0]) {
                    if (part[0]) translated += part[0];
                }
            }

            if (translated) {
                translationCache.set(cacheKey, translated);
                return translated;
            }
            return text;
        } catch (error) {
            console.error('[Traductor] Error:', error);
            return text;
        }
    }

    // Función AGRESIVA para traducir transcript - busca en TODA la página
    async function translateTranscriptElements() {
        console.log('[Traductor] Ejecutando traducción automática...');

        let translatedCount = 0;
        const englishPattern = /\b(the|and|to|of|a|in|that|is|was|for|on|are|with|they|be|at|one|have|this|from|by|not|but|what|all|were|when|we|there|can|an|your|which|their|will|each|about|how|if|up|out|them|then|she|many|some|would|make|like|into|has|look|two|more|go|see|no|way|could|my|than|been|call|who|its|now|find|long|down|day|did|get|come|made|may|part|okay|going|first|need|want|think|know|take|getting|started|building|create|web|page|using|module|master|course|lesson)\b/i;

        // Buscar TODOS los elementos que podrían tener texto de transcript
        const allElements = document.querySelectorAll('button div, button span, [class*="transcript"] div, [class*="transcript"] span, dialog div, dialog span');

        for (const el of allElements) {
            // Solo procesar elementos hoja (sin hijos con texto significativo)
            if (el.children.length > 0) {
                const childHasText = Array.from(el.children).some(c => c.textContent?.trim().length > 10);
                if (childHasText) continue;
            }

            const text = el.textContent?.trim();
            if (!text) continue;

            // Ignorar timestamps
            if (/^\d{1,2}:\d{2}(:\d{2})?$/.test(text)) continue;

            // Ignorar textos muy cortos o muy largos
            if (text.length < 8 || text.length > 500) continue;

            // Ignorar UI
            if (/^(transcript|hide|show|close|fullscreen|search|lecciones|lessons)/i.test(text)) continue;

            // Ya traducido?
            if (el.dataset.translated === 'true') continue;

            // Es inglés?
            if (englishPattern.test(text)) {
                try {
                    const translated = await translateToSpanish(text);
                    if (translated && translated !== text && translated.length > 3) {
                        el.textContent = translated;
                        el.dataset.translated = 'true';
                        el.style.color = '#90EE90';
                        translatedCount++;
                        console.log('[Traductor] Traducido:', text.substring(0, 30), '->', translated.substring(0, 30));
                    }
                } catch (e) {
                    console.error('[Traductor] Error en elemento:', e);
                }
            }
        }

        console.log('[Traductor] Total traducido:', translatedCount);
        return translatedCount;
    }

    // Observar cambios en el DOM - MUY AGRESIVO
    function startTranscriptObserver() {
        if (translationObserver) return;

        console.log('[Traductor] ★★★ INICIANDO OBSERVADOR AGRESIVO ★★★');

        // Traducir inmediatamente lo que haya
        translateTranscriptElements();

        // Traducir de nuevo después de 2 segundos (para contenido dinámico)
        setTimeout(translateTranscriptElements, 2000);
        setTimeout(translateTranscriptElements, 5000);
        setTimeout(translateTranscriptElements, 10000);

        // Observar CUALQUIER cambio en el DOM
        translationObserver = new MutationObserver((mutations) => {
            // Debounce para no ejecutar demasiado
            if (window._translateTimeout) clearTimeout(window._translateTimeout);
            window._translateTimeout = setTimeout(() => {
                translateTranscriptElements();
            }, 1000);
        });

        translationObserver.observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true
        });

        // También traducir cuando el usuario hace scroll (puede cargar más contenido)
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(translateTranscriptElements, 500);
        }, { passive: true });

        // Traducir cuando se hace click (puede abrir paneles)
        document.addEventListener('click', () => {
            setTimeout(translateTranscriptElements, 1000);
            setTimeout(translateTranscriptElements, 2000);
        });
    }

    // SIEMPRE iniciar en That Open People
    if (isThatOpenPeople) {
        console.log('[Traductor] ★★★ DETECTADO THAT OPEN PEOPLE - ACTIVANDO TRADUCCIÓN ★★★');

        // Iniciar inmediatamente si el DOM está listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', startTranscriptObserver);
        } else {
            startTranscriptObserver();
        }

        // Respaldo: iniciar de nuevo después de que la página cargue completamente
        window.addEventListener('load', () => {
            console.log('[Traductor] Página completamente cargada, ejecutando traducción...');
            setTimeout(translateTranscriptElements, 1000);
            setTimeout(translateTranscriptElements, 3000);
        });
    }

    // ==================== INTERCEPTAR MEDIASOURCE (CLAVE PARA HD) ====================

    // Esta es la clave para capturar videos HD de sitios como YouTube, Netflix, etc.
    // Interceptamos cuando el navegador añade segmentos de video al buffer

    const originalSourceBufferAppendBuffer = window.SourceBuffer?.prototype?.appendBuffer;
    const originalMediaSourceAddSourceBuffer = window.MediaSource?.prototype?.addSourceBuffer;

    // Almacenar información de MediaSource activos
    const mediaSourceMap = new WeakMap();
    let streamCounter = 0;

    if (window.MediaSource) {
        // Interceptar creación de SourceBuffer
        window.MediaSource.prototype.addSourceBuffer = function(mimeType) {
            const sourceBuffer = originalMediaSourceAddSourceBuffer.call(this, mimeType);

            console.log('[Video Detector HD] SourceBuffer creado:', mimeType);

            // Notificar que hay un stream activo
            if (mimeType.includes('video')) {
                const streamId = `stream-${++streamCounter}`;
                mediaSourceMap.set(sourceBuffer, {
                    mimeType: mimeType,
                    streamId: streamId,
                    chunks: 0,
                    totalSize: 0
                });

                notifyVideoFound({
                    url: window.location.href,
                    source: 'mediasource-stream',
                    type: 'hd-stream',
                    mimeType: mimeType,
                    streamId: streamId,
                    pageUrl: window.location.href,
                    note: 'Stream HD detectado. El video se está reproduciendo via MediaSource.',
                    timestamp: Date.now()
                });
            }

            return sourceBuffer;
        };
    }

    // ==================== INTERCEPTAR FETCH MEJORADO ====================

    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const request = args[0];
        let url = typeof request === 'string' ? request : request?.url || '';

        // Normalizar URL
        try {
            url = new URL(url, window.location.href).href;
        } catch(e) {}

        // Patrones de video más completos
        const videoPatterns = [
            /\.mp4/i, /\.webm/i, /\.m4v/i, /\.mkv/i, /\.avi/i, /\.mov/i,
            /\.m3u8/i, /\.mpd/i, /\.ts\b/i, /\.m4s/i,
            /video/i, /stream/i, /media/i, /manifest/i, /playlist/i,
            /segment/i, /chunk/i, /frag/i,
            /googlevideo/i, /videoplayback/i,
            /\.f\d+\.mp4/i, // YouTube format
            /itag=\d+/i, // YouTube
            /sq=\d+/i, // Quality parameter
            /range=/i, // Range request (video segments)
            /bytes=/i
        ];

        const isVideo = videoPatterns.some(pattern => pattern.test(url));

        if (isVideo) {
            console.log('[Video Detector HD] Fetch video detectado:', url.substring(0, 100));

            // Capturar la respuesta para analizar
            const response = await originalFetch.apply(this, args);

            // Clonar respuesta para no consumirla
            const clone = response.clone();

            // Obtener headers
            const contentType = response.headers.get('content-type') || '';
            const contentLength = response.headers.get('content-length') || '0';

            // Detectar calidad de la URL
            const quality = detectQualityFromUrl(url);

            if (!detectedVideosDOM.has(url) &&
                (contentType.includes('video') ||
                 contentType.includes('mpegurl') ||
                 contentType.includes('dash') ||
                 contentType.includes('octet-stream') ||
                 url.match(/\.(mp4|webm|m3u8|mpd|ts|m4s)/i))) {

                detectedVideosDOM.add(url);
                capturedStreamUrls.set(url, {
                    contentType: contentType,
                    size: parseInt(contentLength),
                    quality: quality,
                    timestamp: Date.now()
                });

                notifyVideoFound({
                    url: url,
                    source: 'fetch-intercept-hd',
                    mimeType: contentType,
                    size: parseInt(contentLength),
                    quality: quality,
                    pageUrl: window.location.href,
                    timestamp: Date.now()
                });

                console.log(`[Video Detector HD] Video HD capturado (${quality}):`, url.substring(0, 80));
            }

            return response;
        }

        return originalFetch.apply(this, args);
    };

    // ==================== INTERCEPTAR XMLHttpRequest MEJORADO ====================

    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
        this._videoDetectorUrl = url;
        this._videoDetectorMethod = method;
        return originalXHROpen.call(this, method, url, ...rest);
    };

    XMLHttpRequest.prototype.send = function(body) {
        const url = this._videoDetectorUrl;

        if (url) {
            const videoPatterns = [
                /\.mp4/i, /\.webm/i, /\.m4v/i, /\.m3u8/i, /\.mpd/i, /\.ts\b/i, /\.m4s/i,
                /video/i, /stream/i, /media/i, /manifest/i, /playlist/i,
                /segment/i, /chunk/i, /googlevideo/i, /videoplayback/i
            ];

            const isVideo = videoPatterns.some(pattern => pattern.test(url));

            if (isVideo && !detectedVideosDOM.has(url)) {
                const quality = detectQualityFromUrl(url);

                this.addEventListener('load', function() {
                    const contentType = this.getResponseHeader('content-type') || '';
                    const contentLength = this.getResponseHeader('content-length') || '0';

                    if (!detectedVideosDOM.has(url)) {
                        detectedVideosDOM.add(url);

                        notifyVideoFound({
                            url: url,
                            source: 'xhr-intercept-hd',
                            mimeType: contentType,
                            size: parseInt(contentLength),
                            quality: quality,
                            pageUrl: window.location.href,
                            timestamp: Date.now()
                        });

                        console.log(`[Video Detector HD] XHR video (${quality}):`, url.substring(0, 80));
                    }
                });
            }
        }

        return originalXHRSend.call(this, body);
    };

    // ==================== DETECTAR CALIDAD DE URL ====================

    function detectQualityFromUrl(url) {
        const lower = url.toLowerCase();

        // Patrones de calidad
        if (/4k|2160p|3840x2160|uhd/i.test(lower)) return '4K';
        if (/1440p|2560x1440|qhd/i.test(lower)) return '1440p';
        if (/1080p|1920x1080|fullhd|full.?hd/i.test(lower)) return '1080p';
        if (/720p|1280x720|hd(?!d)/i.test(lower)) return '720p';
        if (/480p|854x480|sd/i.test(lower)) return '480p';
        if (/360p|640x360/i.test(lower)) return '360p';
        if (/240p|426x240/i.test(lower)) return '240p';
        if (/144p|256x144/i.test(lower)) return '144p';

        // YouTube itag
        const itagMatch = url.match(/itag[=\/](\d+)/i);
        if (itagMatch) {
            const itag = itagMatch[1];
            const itagQuality = {
                '37': '1080p', '137': '1080p', '248': '1080p', '299': '1080p',
                '22': '720p', '136': '720p', '247': '720p', '298': '720p',
                '135': '480p', '244': '480p',
                '18': '360p', '134': '360p', '243': '360p',
                '133': '240p', '242': '240p',
                '160': '144p', '278': '144p',
                '264': '1440p', '271': '1440p',
                '266': '2160p', '313': '2160p', '315': '2160p'
            };
            if (itagQuality[itag]) return itagQuality[itag];
        }

        // Buscar "quality" o "res" en parámetros
        try {
            const urlObj = new URL(url);
            const quality = urlObj.searchParams.get('quality') ||
                           urlObj.searchParams.get('q') ||
                           urlObj.searchParams.get('res');
            if (quality) {
                if (/1080|full/i.test(quality)) return '1080p';
                if (/720|hd/i.test(quality)) return '720p';
                if (/480/i.test(quality)) return '480p';
                if (/360/i.test(quality)) return '360p';
            }
        } catch(e) {}

        return 'HD'; // Por defecto asumir HD si no podemos determinar
    }

    // ==================== DETECTAR VIDEOS EN EL DOM ====================

    function detectVideoElements() {
        // Buscar videos normales
        const videos = document.querySelectorAll('video');

        // También buscar videos en Shadow DOM (componentes como hls-video, etc.)
        const shadowVideos = [];
        document.querySelectorAll('*').forEach(el => {
            if (el.shadowRoot) {
                el.shadowRoot.querySelectorAll('video').forEach(v => {
                    // Añadir referencia al elemento padre para obtener src del m3u8
                    v._parentComponent = el;
                    shadowVideos.push(v);
                });
            }
        });

        // Detectar elementos hls-video directamente (That Open Company)
        document.querySelectorAll('hls-video').forEach(hlsEl => {
            const hlsSrc = hlsEl.getAttribute('src');
            if (hlsSrc && !detectedVideosDOM.has(hlsSrc)) {
                detectedVideosDOM.add(hlsSrc);

                // Obtener video del shadow para dimensiones
                let width = 1920, height = 1080, duration = 0;
                if (hlsEl.shadowRoot) {
                    const video = hlsEl.shadowRoot.querySelector('video');
                    if (video) {
                        width = video.videoWidth || 1920;
                        height = video.videoHeight || 1080;
                        duration = video.duration || 0;
                    }
                }

                const quality = height >= 1080 ? '1080p' : height >= 720 ? '720p' : `${height}p`;

                notifyVideoFound({
                    url: hlsSrc,
                    source: 'hls-video-component',
                    type: 'HLS',
                    streamType: 'HLS',
                    width: width,
                    height: height,
                    quality: quality,
                    duration: duration,
                    pageUrl: window.location.href,
                    timestamp: Date.now()
                });

                console.log(`[Video Detector HD] HLS Video ${quality} desde componente hls-video`);
            }
        });

        // Combinar videos normales y de shadow DOM
        const allVideos = [...videos, ...shadowVideos];

        allVideos.forEach(video => {
            // Obtener dimensiones reales del video
            const width = video.videoWidth || video.clientWidth || 0;
            const height = video.videoHeight || video.clientHeight || 0;

            // Determinar calidad por resolución
            let quality = 'unknown';
            if (height >= 2160) quality = '4K';
            else if (height >= 1440) quality = '1440p';
            else if (height >= 1080) quality = '1080p';
            else if (height >= 720) quality = '720p';
            else if (height >= 480) quality = '480p';
            else if (height >= 360) quality = '360p';
            else if (height > 0) quality = `${height}p`;

            // Buscar src
            let src = video.src || video.currentSrc;

            // Buscar en source elements
            if (!src) {
                const sources = video.querySelectorAll('source');
                for (const source of sources) {
                    if (source.src) {
                        src = source.src;
                        break;
                    }
                }
            }

            // Video con blob URL (streaming)
            if (src && src.startsWith('blob:')) {
                const blobKey = `blob-${width}x${height}-${Math.round(video.duration || 0)}`;

                if (!detectedVideosDOM.has(blobKey)) {
                    detectedVideosDOM.add(blobKey);

                    notifyVideoFound({
                        url: window.location.href,
                        blobUrl: src,
                        source: 'dom-video-blob',
                        type: 'hd-stream',
                        width: width,
                        height: height,
                        quality: quality,
                        duration: video.duration || 0,
                        pageUrl: window.location.href,
                        note: `Video ${quality} detectado. Usa la URL de la página para descargar.`,
                        timestamp: Date.now()
                    });

                    console.log(`[Video Detector HD] Video blob ${quality} (${width}x${height})`);
                }
            }
            // Video con URL directa
            else if (src && !src.startsWith('data:')) {
                try {
                    const absoluteUrl = new URL(src, window.location.href).href;

                    if (!detectedVideosDOM.has(absoluteUrl)) {
                        detectedVideosDOM.add(absoluteUrl);

                        notifyVideoFound({
                            url: absoluteUrl,
                            source: 'dom-video-element',
                            width: width,
                            height: height,
                            quality: quality || detectQualityFromUrl(absoluteUrl),
                            duration: video.duration || 0,
                            timestamp: Date.now()
                        });

                        console.log(`[Video Detector HD] Video ${quality}:`, absoluteUrl.substring(0, 80));
                    }
                } catch (e) {}
            }
        });
    }

    // ==================== DETECTAR IFRAMES CON PLAYERS ====================

    function detectIframeVideos() {
        const iframes = document.querySelectorAll('iframe');

        iframes.forEach(iframe => {
            const src = iframe.src || '';
            if (!src) return;

            const videoPlatforms = [
                'youtube.com/embed', 'youtu.be',
                'player.vimeo.com', 'vimeo.com/video',
                'wistia.com', 'wistia.net',
                'loom.com', 'vidyard.com',
                'brightcove', 'jwplayer', 'jwplatform',
                'dailymotion.com/embed', 'dai.ly',
                'facebook.com/plugins/video',
                'instagram.com',
                'tiktok.com/embed',
                'twitch.tv/embed',
                'streamable.com',
                'embed', 'player', 'video'
            ];

            const isVideoIframe = videoPlatforms.some(platform =>
                src.toLowerCase().includes(platform)
            );

            if (isVideoIframe && !detectedVideosDOM.has(src)) {
                detectedVideosDOM.add(src);

                // Intentar extraer ID de video
                let videoId = null;
                let platform = 'unknown';

                if (src.includes('youtube')) {
                    platform = 'YouTube';
                    const match = src.match(/embed\/([^?&]+)/);
                    if (match) videoId = match[1];
                } else if (src.includes('vimeo')) {
                    platform = 'Vimeo';
                    const match = src.match(/video\/(\d+)/);
                    if (match) videoId = match[1];
                }

                notifyVideoFound({
                    url: src,
                    source: 'iframe-embed',
                    type: 'embedded-player',
                    platform: platform,
                    videoId: videoId,
                    pageUrl: window.location.href,
                    note: `Video embebido de ${platform}. Usa la URL del iframe para descargar.`,
                    timestamp: Date.now()
                });

                console.log(`[Video Detector HD] Iframe ${platform}:`, src.substring(0, 80));
            }
        });
    }

    // ==================== BUSCAR URLS DE VIDEO EN SCRIPTS ====================

    function scanPageForVideoUrls() {
        // Buscar en scripts inline
        const scripts = document.querySelectorAll('script:not([src])');

        const videoUrlPatterns = [
            /"(https?:\/\/[^"]+\.(?:mp4|webm|m3u8|mpd)[^"]*)"/gi,
            /'(https?:\/\/[^']+\.(?:mp4|webm|m3u8|mpd)[^']*)'/gi,
            /src['":\s]*['"](https?:\/\/[^'"]+(?:video|stream|media)[^'"]*)['"]/gi,
            /url['":\s]*['"](https?:\/\/[^'"]+\.(?:mp4|webm|m3u8)[^'"]*)['"]/gi,
            /manifest['":\s]*['"](https?:\/\/[^'"]+)['"]/gi
        ];

        scripts.forEach(script => {
            const content = script.textContent || '';

            videoUrlPatterns.forEach(pattern => {
                let match;
                while ((match = pattern.exec(content)) !== null) {
                    const url = match[1];

                    if (url && !detectedVideosDOM.has(url) &&
                        !url.includes('analytics') &&
                        !url.includes('tracking')) {

                        detectedVideosDOM.add(url);

                        notifyVideoFound({
                            url: url,
                            source: 'script-scan',
                            quality: detectQualityFromUrl(url),
                            pageUrl: window.location.href,
                            timestamp: Date.now()
                        });

                        console.log('[Video Detector HD] URL en script:', url.substring(0, 80));
                    }
                }
            });
        });

        // Buscar en atributos data-*
        const elementsWithData = document.querySelectorAll('[data-video-url], [data-src], [data-video], [data-stream]');
        elementsWithData.forEach(el => {
            const attrs = ['data-video-url', 'data-src', 'data-video', 'data-stream',
                          'data-video-src', 'data-hls', 'data-dash', 'data-manifest'];

            attrs.forEach(attr => {
                const value = el.getAttribute(attr);
                if (value && value.startsWith('http') && !detectedVideosDOM.has(value)) {
                    detectedVideosDOM.add(value);

                    notifyVideoFound({
                        url: value,
                        source: 'data-attribute',
                        quality: detectQualityFromUrl(value),
                        timestamp: Date.now()
                    });
                }
            });
        });
    }

    // ==================== NOTIFICAR VIDEO AL BACKGROUND ====================

    function notifyVideoFound(videoData) {
        try {
            chrome.runtime.sendMessage({
                action: 'video-detected-from-dom',
                video: videoData
            }).catch(() => {});
        } catch (err) {
            // Extension context invalidated, ignorar
        }
    }

    // ==================== OBSERVADOR DE MUTACIONES ====================

    function observeDOM() {
        const observer = new MutationObserver((mutations) => {
            let shouldCheck = false;

            for (const mutation of mutations) {
                for (const node of mutation.addedNodes) {
                    if (node.nodeType === 1) { // ELEMENT_NODE
                        if (node.tagName === 'VIDEO' ||
                            node.tagName === 'IFRAME' ||
                            node.querySelector?.('video, iframe')) {
                            shouldCheck = true;
                            break;
                        }
                    }
                }
                if (shouldCheck) break;
            }

            if (shouldCheck) {
                setTimeout(() => {
                    detectVideoElements();
                    detectIframeVideos();
                }, 500);
            }
        });

        observer.observe(document.documentElement, {
            childList: true,
            subtree: true
        });
    }

    // ==================== DETECCIÓN PERIÓDICA ====================

    function startPeriodicDetection() {
        // Detectar cada 2 segundos
        detectionInterval = setInterval(() => {
            detectVideoElements();
            detectIframeVideos();
        }, 2000);

        // Escanear scripts menos frecuentemente
        setInterval(scanPageForVideoUrls, 5000);
    }

    // ==================== INICIALIZACIÓN ====================

    function init() {
        console.log('[Video Detector HD] Inicializando detección agresiva...');

        // Ejecutar detección inicial
        const runDetection = () => {
            detectVideoElements();
            detectIframeVideos();
            scanPageForVideoUrls();
        };

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(runDetection, 1000);
            });
        } else {
            setTimeout(runDetection, 500);
        }

        // Observar cambios en el DOM
        if (document.body) {
            observeDOM();
        } else {
            document.addEventListener('DOMContentLoaded', observeDOM);
        }

        // Iniciar detección periódica
        startPeriodicDetection();

        // Detectar al hacer scroll
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(detectVideoElements, 300);
        }, { passive: true });

        // Detectar cuando la ventana gana foco
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                setTimeout(runDetection, 500);
            }
        });

        // Detectar cuando el video comienza a reproducirse
        document.addEventListener('play', (e) => {
            if (e.target.tagName === 'VIDEO') {
                setTimeout(detectVideoElements, 100);
            }
        }, true);

        console.log('[Video Detector HD] Sistema de detección HD activado');
    }

    // Limpiar al cerrar
    window.addEventListener('beforeunload', () => {
        if (detectionInterval) {
            clearInterval(detectionInterval);
        }
    });

    // ==================== LISTENER PARA MENSAJES ====================

    // ==================== EXTRAER TRANSCRIPT ====================

    function extractTranscript() {
        console.log('[Video Detector HD] Extrayendo transcript...');

        let transcriptText = [];
        let transcriptFound = false;
        const timestampRegex = /^\d{1,2}:\d{2}(:\d{2})?$/;

        // MÉTODO 0 (MÁS PRIORITARIO): Parsear texto concatenado con timestamps
        // Formato: "00:02Texto aquí00:05Más texto00:08Otro texto"
        // Buscar contenedor que tenga muchos timestamps en su textContent
        const allContainers = document.querySelectorAll('main, div, section, article');
        for (const container of allContainers) {
            const fullText = container.textContent || '';
            const timestampMatches = fullText.match(/\d{2}:\d{2}/g);

            // Si tiene más de 5 timestamps, probablemente es el contenedor de transcript
            if (timestampMatches && timestampMatches.length >= 5) {
                console.log('[Video Detector HD] MÉTODO 0: Contenedor con', timestampMatches.length, 'timestamps');

                // Parsear el texto concatenado
                // Regex que captura: timestamp seguido de texto hasta el siguiente timestamp
                const parseRegex = /(\d{2}:\d{2})([^]*?)(?=\d{2}:\d{2}|$)/g;
                let entries = [];
                let match;

                while ((match = parseRegex.exec(fullText)) !== null) {
                    const timestamp = match[1];
                    let text = match[2].trim();

                    // Limpiar texto de elementos de UI
                    text = text
                        .replace(/^(Ocultar la transcripci[oó]n|Hide transcript|Transcripci[oó]n|Transcript)/gi, '')
                        .replace(/^(Show transcript|Mostrar transcript)/gi, '')
                        .replace(/^(Toggle fullscreen|Close|Cerrar)/gi, '')
                        .trim();

                    // Solo agregar si tiene contenido útil
                    if (text.length > 3 && text.length < 500) {
                        entries.push({ time: timestamp, text: text });
                    }
                }

                if (entries.length >= 5) {
                    transcriptFound = true;
                    transcriptText = entries.map(e => `[${e.time}] ${e.text}`);
                    console.log('[Video Detector HD] MÉTODO 0 (regex): Extraídas', entries.length, 'entradas');
                    break;
                }
            }
        }

        // MÉTODO 1: Estructura de That Open People
        // Buscar botones que contengan exactamente un timestamp y texto
        // Estructura: button > [div/span con timestamp] + [div/span con texto]
        if (!transcriptFound) {
        const allButtons = document.querySelectorAll('button');
        let buttonEntries = [];

        for (const button of allButtons) {
            const children = button.querySelectorAll('div, span, p');
            if (children.length >= 2) {
                // Buscar timestamp y texto en los hijos directos o nietos
                let timestamp = null;
                let text = null;

                for (const child of children) {
                    const content = child.textContent?.trim();
                    if (!content) continue;

                    // Es un timestamp?
                    if (timestampRegex.test(content) && !timestamp) {
                        timestamp = content;
                    }
                    // Es texto (no timestamp, no muy corto, no UI)?
                    else if (!timestampRegex.test(content) &&
                             content.length > 5 &&
                             content.length < 500 &&
                             !content.toLowerCase().includes('transcript') &&
                             !content.toLowerCase().includes('hide') &&
                             !content.toLowerCase().includes('show') &&
                             !content.toLowerCase().includes('fullscreen') &&
                             !content.toLowerCase().includes('close')) {
                        // Solo tomar el texto si es un elemento hoja (sin hijos con texto)
                        const hasChildText = Array.from(child.children).some(c =>
                            c.textContent?.trim().length > 5 && c.textContent?.trim() !== content
                        );
                        if (!hasChildText && !text) {
                            text = content;
                        }
                    }
                }

                if (timestamp && text) {
                    buttonEntries.push({ time: timestamp, text: text });
                }
            }
        }

        if (buttonEntries.length > 3) {
            transcriptFound = true;
            transcriptText = buttonEntries.map(e => `[${e.time}] ${e.text}`);
            console.log('[Video Detector HD] MÉTODO 1 (botones): Extraídas', buttonEntries.length, 'entradas');
        }
        } // Fin MÉTODO 1

        // MÉTODO 2: Buscar por "Hide transcript" / "Show transcript" y subir al contenedor
        if (!transcriptFound) {
            const transcriptToggle = Array.from(document.querySelectorAll('a, button, span, div')).find(el => {
                const text = el.textContent?.toLowerCase() || '';
                return (text.includes('hide transcript') || text.includes('ocultar') ||
                        text.includes('show transcript') || text.includes('mostrar transcript')) &&
                       text.length < 50;
            });

            if (transcriptToggle) {
                console.log('[Video Detector HD] Encontrado toggle de transcript:', transcriptToggle.textContent);

                // Buscar el contenedor padre que tenga el transcript completo
                let container = transcriptToggle.parentElement;

                // Subir en el DOM hasta encontrar un contenedor con múltiples timestamps
                for (let i = 0; i < 10 && container; i++) {
                    const elements = container.querySelectorAll('div, span, p');
                    let timestampCount = 0;

                    for (const el of elements) {
                        if (timestampRegex.test(el.textContent?.trim() || '')) {
                            timestampCount++;
                        }
                    }

                    if (timestampCount >= 5) {
                        console.log('[Video Detector HD] Contenedor encontrado con', timestampCount, 'timestamps');
                        break;
                    }
                    container = container.parentElement;
                }

                if (container) {
                    // Extraer timestamps y textos de elementos hoja
                    const allElements = Array.from(container.querySelectorAll('div, span, p'));

                    let currentTime = null;
                    let entries = [];

                    for (const el of allElements) {
                        const text = el.textContent?.trim();
                        if (!text) continue;

                        // Solo procesar elementos hoja (sin hijos de texto)
                        const isLeaf = el.children.length === 0 ||
                                       !Array.from(el.children).some(c => c.textContent?.trim().length > 2);

                        if (!isLeaf) continue;

                        // Ignorar elementos de UI
                        if (text.toLowerCase().includes('transcript') && text.length < 30) continue;
                        if (text.toLowerCase().includes('hide') && text.length < 20) continue;
                        if (text.toLowerCase().includes('show') && text.length < 20) continue;
                        if (text.toLowerCase().includes('fullscreen')) continue;
                        if (text.toLowerCase().includes('close') && text.length < 10) continue;

                        // Es un timestamp?
                        if (timestampRegex.test(text)) {
                            currentTime = text;
                        }
                        // Es texto de subtítulo?
                        else if (currentTime && text.length > 5 && text.length < 500) {
                            entries.push({ time: currentTime, text: text });
                            currentTime = null;
                        }
                    }

                    if (entries.length > 3) {
                        transcriptFound = true;
                        transcriptText = entries.map(e => `[${e.time}] ${e.text}`);
                        console.log('[Video Detector HD] MÉTODO 2 (toggle): Extraídas', entries.length, 'entradas');
                    }
                }
            }
        }

        // MÉTODO 3: Buscar selectores comunes de transcripts
        if (!transcriptFound) {
            const transcriptSelectors = [
                '.transcript', '.transcript-text', '.transcript-body',
                '[class*="transcript"]', '[data-transcript]',
                '.captions', '.captions-text', '.caption-text',
                '[class*="caption"]',
                'ytd-transcript-segment-renderer',
                '.ytd-transcript-body-renderer',
                '.subtitle', '.subtitles', '[class*="subtitle"]',
                '.cc-text', '.closed-caption',
                '[class*="cue"]'
            ];

            for (const selector of transcriptSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    if (elements.length > 0) {
                        elements.forEach(el => {
                            const text = el.textContent?.trim();
                            if (text && text.length > 5) {
                                transcriptText.push(text);
                                transcriptFound = true;
                            }
                        });
                        if (transcriptFound) {
                            console.log('[Video Detector HD] MÉTODO 3 (selector):', selector);
                            break;
                        }
                    }
                } catch(e) {}
            }
        }

        // MÉTODO 4: Buscar patrones de timestamp consecutivos en toda la página
        if (!transcriptFound) {
            const allElements = document.querySelectorAll('div, span, p');
            let currentSection = null;
            let sections = [];

            allElements.forEach(el => {
                const text = el.textContent?.trim();
                if (!text) return;

                // Solo elementos hoja
                if (el.children.length > 0) return;

                if (timestampRegex.test(text)) {
                    if (currentSection && currentSection.text) {
                        sections.push(currentSection);
                    }
                    currentSection = { time: text, text: '' };
                }
                else if (currentSection && text.length > 10 && text.length < 500) {
                    const isUI = el.closest('nav, header, footer, [role="navigation"]');
                    if (!isUI && !currentSection.text) {
                        currentSection.text = text;
                    }
                }
            });

            if (currentSection && currentSection.text) {
                sections.push(currentSection);
            }

            if (sections.length > 3) {
                transcriptFound = true;
                transcriptText = sections.map(s => `[${s.time}] ${s.text}`);
                console.log('[Video Detector HD] MÉTODO 4 (patrones): Extraídas', sections.length, 'entradas');
            }
        }

        // MÉTODO 5: Extraer solo texto sin timestamps (último recurso)
        if (!transcriptFound) {
            // Buscar un contenedor que parezca tener mucho texto de transcript
            const containers = document.querySelectorAll('div, section, article');
            for (const container of containers) {
                const text = container.textContent || '';
                // Si contiene muchos timestamps, probablemente es el contenedor de transcript
                const timestampMatches = text.match(/\d{1,2}:\d{2}/g);
                if (timestampMatches && timestampMatches.length > 10) {
                    // Extraer texto de elementos hoja dentro del contenedor
                    const leaves = container.querySelectorAll('div, span, p');
                    let texts = [];

                    for (const leaf of leaves) {
                        if (leaf.children.length === 0) {
                            const t = leaf.textContent?.trim();
                            if (t && t.length > 5 && !timestampRegex.test(t)) {
                                texts.push(t);
                            }
                        }
                    }

                    if (texts.length > 10) {
                        transcriptFound = true;
                        transcriptText = texts;
                        console.log('[Video Detector HD] MÉTODO 5 (texto): Extraídas', texts.length, 'líneas');
                        break;
                    }
                }
            }
        }

        if (transcriptFound && transcriptText.length > 0) {
            // Limpiar duplicados y texto vacío
            transcriptText = [...new Set(transcriptText)].filter(t => t.trim().length > 0);

            const fullText = transcriptText.join('\n');
            console.log('[Video Detector HD] Transcript extraído:', fullText.substring(0, 200) + '...');
            return {
                success: true,
                text: fullText,
                lines: transcriptText.length,
                charCount: fullText.length
            };
        }

        return {
            success: false,
            error: 'No se encontró transcript en la página. Asegúrate de que el panel de transcript esté visible (haz clic en "Show transcript" primero).'
        };
    }

    // ==================== TTS SINCRONIZADO - FUNCIONES ====================

    // Variables globales para TTS
    window._ttsActive = false;
    window._ttsEntries = [];
    window._ttsCurrentIndex = 0;
    window._ttsSpeaking = false;
    window._ttsVideo = null;

    // Extraer transcript con timestamps en segundos
    function extractTranscriptWithTimestamps() {
        console.log('[TTS Sync] Extrayendo transcript con timestamps...');

        const entries = [];
        const buttons = document.querySelectorAll('button');

        for (const btn of buttons) {
            const text = btn.textContent || '';
            // Buscar botones que empiecen con timestamp
            const match = text.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?/);

            if (match) {
                const minutes = parseInt(match[1]);
                const seconds = parseInt(match[2]);
                const hours = match[3] ? parseInt(match[1]) : 0;

                let timeInSeconds;
                if (match[3]) {
                    // Formato HH:MM:SS
                    timeInSeconds = hours * 3600 + minutes * 60 + seconds;
                } else {
                    // Formato MM:SS
                    timeInSeconds = minutes * 60 + seconds;
                }

                // Extraer el texto (todo después del timestamp)
                const textContent = text.replace(/^\d{1,2}:\d{2}(:\d{2})?\s*/, '').trim();

                if (textContent.length > 3 && textContent.length < 500) {
                    entries.push({
                        time: timeInSeconds,
                        text: textContent,
                        timestamp: match[0]
                    });
                }
            }
        }

        // Ordenar por tiempo
        entries.sort((a, b) => a.time - b.time);

        console.log('[TTS Sync] Extraídas', entries.length, 'entradas');

        if (entries.length === 0) {
            return {
                success: false,
                error: 'No se encontró transcript. Asegúrate de que el panel de transcript esté abierto.'
            };
        }

        return {
            success: true,
            entries: entries
        };
    }

    // Traducir texto para TTS
    async function translateForTTS(text) {
        // Usar cache si existe
        if (translationCache.has(text)) {
            return translationCache.get(text);
        }

        try {
            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q=${encodeURIComponent(text)}`;
            const response = await fetch(url);
            const data = await response.json();

            let translated = '';
            if (data && data[0]) {
                for (const part of data[0]) {
                    if (part[0]) translated += part[0];
                }
            }

            if (translated) {
                translationCache.set(text, translated);
                return translated;
            }
            return text;
        } catch (e) {
            console.error('[TTS Sync] Error traduciendo:', e);
            return text;
        }
    }

    // Hablar texto usando Web Speech API
    function speakText(text, onEnd) {
        return new Promise((resolve) => {
            if (!window.speechSynthesis) {
                console.error('[TTS Sync] speechSynthesis no disponible');
                resolve();
                return;
            }

            // Cancelar cualquier speech anterior
            window.speechSynthesis.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'es-ES';
            utterance.rate = 1.1; // Un poco más rápido para sincronizar mejor
            utterance.pitch = 1;
            utterance.volume = window._ttsVolume || 0.8;

            // Buscar una voz en español
            const voices = window.speechSynthesis.getVoices();
            const spanishVoice = voices.find(v =>
                v.lang.startsWith('es') && (v.name.includes('Microsoft') || v.name.includes('Google') || v.name.includes('Helena') || v.name.includes('Laura'))
            ) || voices.find(v => v.lang.startsWith('es'));

            if (spanishVoice) {
                utterance.voice = spanishVoice;
            }

            utterance.onend = () => {
                window._ttsSpeaking = false;
                if (onEnd) onEnd();
                resolve();
            };

            utterance.onerror = (e) => {
                console.error('[TTS Sync] Error en speech:', e);
                window._ttsSpeaking = false;
                resolve();
            };

            window._ttsSpeaking = true;
            window.speechSynthesis.speak(utterance);
        });
    }

    // Iniciar TTS sincronizado
    async function initSyncTTS(video, entries, options = {}) {
        console.log('[TTS Sync] Inicializando con', entries.length, 'entradas');

        // Detener cualquier TTS anterior
        stopSyncTTS();

        window._ttsActive = true;
        window._ttsVideo = video;
        window._ttsVolume = options.ttsVolume || 0.8;

        // Pre-traducir todas las entradas
        console.log('[TTS Sync] Pre-traduciendo entradas...');
        const translatedEntries = [];

        for (const entry of entries) {
            const translated = await translateForTTS(entry.text);
            translatedEntries.push({
                ...entry,
                translated: translated
            });
        }

        window._ttsEntries = translatedEntries;
        window._ttsCurrentIndex = 0;

        // Reducir volumen del video original
        if (options.reduceOriginalVolume !== false) {
            video.volume = options.videoVolume || 0.3;
        }

        // Mostrar control flotante
        showTTSControls(video);

        // Escuchar eventos del video
        video.addEventListener('timeupdate', handleVideoTimeUpdate);
        video.addEventListener('play', handleVideoPlay);
        video.addEventListener('pause', handleVideoPause);
        video.addEventListener('seeked', handleVideoSeeked);

        console.log('[TTS Sync] Sistema TTS iniciado correctamente');

        // Si el video ya está reproduciéndose, iniciar TTS
        if (!video.paused) {
            handleVideoPlay();
        }
    }

    // Manejar actualización de tiempo del video
    function handleVideoTimeUpdate() {
        if (!window._ttsActive || !window._ttsVideo) return;

        const currentTime = window._ttsVideo.currentTime;

        // Buscar la entrada que corresponde al tiempo actual
        for (let i = window._ttsCurrentIndex; i < window._ttsEntries.length; i++) {
            const entry = window._ttsEntries[i];

            // Si llegamos al tiempo de esta entrada y no estamos hablando
            if (currentTime >= entry.time && currentTime < entry.time + 3 && !window._ttsSpeaking) {
                // Verificar que no hayamos pasado mucho tiempo
                if (currentTime - entry.time < 1.5) {
                    console.log('[TTS Sync] Reproduciendo:', entry.timestamp, entry.translated.substring(0, 30));
                    window._ttsCurrentIndex = i + 1;
                    speakText(entry.translated);
                    break;
                }
            }
        }
    }

    function handleVideoPlay() {
        console.log('[TTS Sync] Video reproduciendo');
        // Reanudar TTS si estaba pausado
        if (window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
        }
    }

    function handleVideoPause() {
        console.log('[TTS Sync] Video pausado');
        // Pausar TTS
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.pause();
        }
    }

    function handleVideoSeeked() {
        console.log('[TTS Sync] Video seek a:', window._ttsVideo?.currentTime);
        // Cancelar speech actual
        window.speechSynthesis.cancel();
        window._ttsSpeaking = false;

        // Encontrar el índice correcto para el nuevo tiempo
        if (window._ttsVideo && window._ttsEntries) {
            const currentTime = window._ttsVideo.currentTime;
            window._ttsCurrentIndex = window._ttsEntries.findIndex(e => e.time > currentTime);
            if (window._ttsCurrentIndex === -1) {
                window._ttsCurrentIndex = window._ttsEntries.length;
            }
        }
    }

    // Detener TTS
    function stopSyncTTS() {
        console.log('[TTS Sync] Deteniendo TTS');

        window._ttsActive = false;
        window.speechSynthesis?.cancel();

        if (window._ttsVideo) {
            window._ttsVideo.removeEventListener('timeupdate', handleVideoTimeUpdate);
            window._ttsVideo.removeEventListener('play', handleVideoPlay);
            window._ttsVideo.removeEventListener('pause', handleVideoPause);
            window._ttsVideo.removeEventListener('seeked', handleVideoSeeked);
            window._ttsVideo.volume = 1; // Restaurar volumen
            window._ttsVideo = null;
        }

        // Remover controles
        const controls = document.getElementById('tts-sync-controls');
        if (controls) controls.remove();
    }

    // Mostrar controles flotantes
    function showTTSControls(video) {
        // Remover controles existentes
        const existing = document.getElementById('tts-sync-controls');
        if (existing) existing.remove();

        const controls = document.createElement('div');
        controls.id = 'tts-sync-controls';
        controls.innerHTML = `
            <style>
                #tts-sync-controls {
                    position: fixed;
                    bottom: 100px;
                    right: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 15px;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                    z-index: 999999;
                    font-family: 'Segoe UI', sans-serif;
                    color: white;
                    min-width: 200px;
                }
                #tts-sync-controls h4 {
                    margin: 0 0 10px 0;
                    font-size: 14px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                #tts-sync-controls .control-row {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin: 8px 0;
                    font-size: 12px;
                }
                #tts-sync-controls input[type="range"] {
                    flex: 1;
                    height: 6px;
                    -webkit-appearance: none;
                    background: rgba(255,255,255,0.3);
                    border-radius: 3px;
                }
                #tts-sync-controls input[type="range"]::-webkit-slider-thumb {
                    -webkit-appearance: none;
                    width: 14px;
                    height: 14px;
                    background: white;
                    border-radius: 50%;
                    cursor: pointer;
                }
                #tts-sync-controls button {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    padding: 8px 12px;
                    border-radius: 6px;
                    color: white;
                    cursor: pointer;
                    font-size: 12px;
                    margin-top: 10px;
                    width: 100%;
                }
                #tts-sync-controls button:hover {
                    background: rgba(255,255,255,0.3);
                }
                #tts-sync-controls .close-btn {
                    position: absolute;
                    top: 5px;
                    right: 8px;
                    background: none;
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 0;
                    width: auto;
                    margin: 0;
                }
            </style>
            <button class="close-btn" onclick="document.getElementById('tts-sync-controls').remove(); stopSyncTTS();">×</button>
            <h4>🔊 TTS Español Activo</h4>
            <div class="control-row">
                <span>🎤 TTS:</span>
                <input type="range" id="tts-volume" min="0" max="1" step="0.1" value="${window._ttsVolume || 0.8}">
                <span id="tts-vol-label">${Math.round((window._ttsVolume || 0.8) * 100)}%</span>
            </div>
            <div class="control-row">
                <span>🎬 Video:</span>
                <input type="range" id="video-volume" min="0" max="1" step="0.1" value="${video.volume}">
                <span id="video-vol-label">${Math.round(video.volume * 100)}%</span>
            </div>
            <button onclick="stopSyncTTS()">⏹️ Detener TTS</button>
        `;

        document.body.appendChild(controls);

        // Event listeners para los sliders
        document.getElementById('tts-volume').addEventListener('input', (e) => {
            window._ttsVolume = parseFloat(e.target.value);
            document.getElementById('tts-vol-label').textContent = Math.round(window._ttsVolume * 100) + '%';
        });

        document.getElementById('video-volume').addEventListener('input', (e) => {
            video.volume = parseFloat(e.target.value);
            document.getElementById('video-vol-label').textContent = Math.round(video.volume * 100) + '%';
        });
    }

    // ==================== LISTENER PARA MENSAJES ====================

    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'extractTranscript') {
            console.log('[Video Detector HD] Solicitud de extracción de transcript');
            const result = extractTranscript();
            sendResponse(result);
            return true;
        }

        if (message.action === 'translateTranscript') {
            console.log('[Video Detector HD] Solicitud de traducción de transcript');

            // Ejecutar traducción asíncrona
            (async () => {
                try {
                    let translatedCount = 0;

                    // Buscar todos los botones del transcript
                    const transcriptButtons = document.querySelectorAll('button');

                    for (const button of transcriptButtons) {
                        const children = button.querySelectorAll('div, span, p');

                        for (const child of children) {
                            const text = child.textContent?.trim();
                            if (!text) continue;

                            // Ignorar timestamps
                            if (/^\d{1,2}:\d{2}(:\d{2})?$/.test(text)) continue;

                            // Ignorar UI y textos muy cortos/largos
                            if (text.length < 5 || text.length > 500) continue;
                            if (text.toLowerCase().includes('transcript')) continue;
                            if (text.toLowerCase().includes('hide') || text.toLowerCase().includes('show')) continue;
                            if (text.toLowerCase().includes('fullscreen') || text.toLowerCase().includes('close')) continue;

                            // Ya traducido?
                            if (child.dataset.translated === 'true') continue;

                            // Parece inglés?
                            const englishWords = /\b(the|and|to|of|a|in|that|is|was|for|on|are|with|they|be|at|one|have|this|from|by|not|but|what|all|were|when|we|there|can|an|your|which|their|will|each|about|how|if|up|out|them|then|she|many|some|would|make|like|into|has|look|two|more|go|see|no|way|could|my|than|been|call|who|its|now|find|long|down|day|did|get|come|made|may|part|okay|going|first)\b/i;

                            if (englishWords.test(text)) {
                                const translated = await translateToSpanish(text);
                                if (translated && translated !== text) {
                                    child.textContent = translated;
                                    child.dataset.translated = 'true';
                                    child.style.color = '#90EE90';
                                    translatedCount++;
                                }
                            }
                        }
                    }

                    sendResponse({
                        success: true,
                        translated: translatedCount
                    });
                } catch (error) {
                    console.error('[Traductor] Error:', error);
                    sendResponse({
                        success: false,
                        error: error.message
                    });
                }
            })();

            return true; // Indica respuesta asíncrona
        }

        // ==================== TTS SINCRONIZADO ====================
        if (message.action === 'startSyncTTS') {
            console.log('[TTS Sync] Iniciando TTS sincronizado...');

            (async () => {
                try {
                    // Extraer transcript con timestamps
                    const transcriptData = extractTranscriptWithTimestamps();

                    if (!transcriptData.success) {
                        sendResponse({ success: false, error: transcriptData.error });
                        return;
                    }

                    // Encontrar el video
                    const video = document.querySelector('video');
                    if (!video) {
                        sendResponse({ success: false, error: 'No se encontró video en la página' });
                        return;
                    }

                    // Iniciar sistema TTS sincronizado
                    initSyncTTS(video, transcriptData.entries, message.options || {});

                    sendResponse({
                        success: true,
                        entries: transcriptData.entries.length,
                        message: `TTS iniciado con ${transcriptData.entries.length} líneas`
                    });
                } catch (error) {
                    console.error('[TTS Sync] Error:', error);
                    sendResponse({ success: false, error: error.message });
                }
            })();

            return true;
        }

        if (message.action === 'stopSyncTTS') {
            stopSyncTTS();
            sendResponse({ success: true });
            return true;
        }

        if (message.action === 'setTTSVolume') {
            if (window._ttsGain) {
                window._ttsGain.gain.value = message.volume;
            }
            sendResponse({ success: true });
            return true;
        }

        if (message.action === 'setVideoVolume') {
            const video = document.querySelector('video');
            if (video) {
                video.volume = message.volume;
            }
            sendResponse({ success: true });
            return true;
        }

        if (message.action === 'forceDetection') {
            console.log('[Video Detector HD] Forzando detección...');

            // Ejecutar todas las detecciones
            detectVideoElements();
            detectIframeVideos();
            scanPageForVideoUrls();

            // Buscar videos de forma más agresiva
            const videos = document.querySelectorAll('video');
            videos.forEach(video => {
                // Forzar que el video dispare eventos
                if (video.paused && video.src) {
                    console.log('[Video Detector HD] Video encontrado:', video.src);
                }

                // Verificar currentSrc
                if (video.currentSrc) {
                    console.log('[Video Detector HD] CurrentSrc:', video.currentSrc);
                }

                // Verificar mediaSource
                const src = video.src || video.currentSrc;
                if (src && src.startsWith('blob:')) {
                    const width = video.videoWidth || video.clientWidth;
                    const height = video.videoHeight || video.clientHeight;

                    let quality = 'HD';
                    if (height >= 2160) quality = '4K';
                    else if (height >= 1440) quality = '1440p';
                    else if (height >= 1080) quality = '1080p';
                    else if (height >= 720) quality = '720p';
                    else if (height > 0) quality = `${height}p`;

                    notifyVideoFound({
                        url: window.location.href,
                        blobUrl: src,
                        source: 'force-detect',
                        type: 'streaming',
                        width: width,
                        height: height,
                        quality: quality,
                        duration: video.duration || 0,
                        pageUrl: window.location.href,
                        note: `Video ${quality}. Usa yt-dlp con la URL de la página para descargar.`,
                        timestamp: Date.now()
                    });
                }
            });

            sendResponse({ success: true, videosFound: videos.length });
        }

        return true;
    });

    // INICIAR
    init();

})();
