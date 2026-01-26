// background.js - Detector y Descargador de Videos HD
// Versión 2.3 - Con intercepción mejorada para HD

console.log('[Video Detector HD] Background service worker iniciado v2.3');

// Almacenamiento de videos detectados por pestaña
let detectedVideos = {};
let urlPatterns = new Map();

// ==================== PATRONES DE VIDEO AGRESIVOS ====================

const VIDEO_PATTERNS = [
    // Extensiones directas
    '*://*/*.mp4*',
    '*://*/*.webm*',
    '*://*/*.m3u8*',
    '*://*/*.mpd*',
    '*://*/*.flv*',
    '*://*/*.avi*',
    '*://*/*.mov*',
    '*://*/*.mkv*',
    '*://*/*.m4v*',
    '*://*/*.ts*',
    '*://*/*.m4s*',
    '*://*/*.f4v*',
    '*://*/*.ogv*',
    '*://*/*.3gp*',
    // HLS/DASH
    '*://*/*playlist*',
    '*://*/*manifest*',
    '*://*/*master.m3u8*',
    '*://*/*index.m3u8*',
    '*://*/*chunklist*',
    '*://*/*segment*',
    '*://*/*chunk*',
    '*://*/*frag*',
    // Plataformas conocidas
    '*://*.googlevideo.com/*',
    '*://*.youtube.com/videoplayback*',
    '*://*.vimeo.com/*',
    '*://*.vimeocdn.com/*',
    '*://*.brightcove*/*',
    '*://*.akamaihd.net/*',
    '*://*.cloudfront.net/*',
    '*://*.jwplayer.com/*',
    '*://*.mux.com/*',
    '*://*.wistia.com/*',
    '*://*.loom.com/*',
    // Palabras clave
    '*://*/*video*',
    '*://*/*stream*',
    '*://*/*media*',
    '*://*/*play*'
];

// Tipos de request a interceptar
const REQUEST_TYPES = ['xmlhttprequest', 'media', 'other', 'object', 'sub_frame'];

// Patrones para detectar calidad en URLs
const QUALITY_PATTERNS = {
    '4K': /4k|2160p|3840x2160|uhd/i,
    '1440p': /1440p|2560x1440|qhd/i,
    '1080p': /1080p|1920x1080|fullhd|full.?hd/i,
    '720p': /720p|1280x720|hd(?!d)/i,
    '480p': /480p|854x480|sd/i,
    '360p': /360p|640x360/i,
    '240p': /240p|426x240/i,
    '144p': /144p|256x144/i
};

// YouTube itag mapping completo
const YOUTUBE_ITAG_MAP = {
    // Video + Audio
    '22': '720p', '18': '360p', '37': '1080p', '38': '4K',
    // Video only DASH (MP4)
    '137': '1080p', '136': '720p', '135': '480p', '134': '360p',
    '133': '240p', '160': '144p',
    '298': '720p60', '299': '1080p60', '264': '1440p', '266': '2160p',
    // Video only DASH (WebM/VP9)
    '248': '1080p', '247': '720p', '244': '480p', '243': '360p',
    '242': '240p', '278': '144p', '271': '1440p', '313': '2160p',
    '315': '2160p60', '302': '720p60', '303': '1080p60',
    // AV1
    '394': '144p', '395': '240p', '396': '360p', '397': '480p',
    '398': '720p', '399': '1080p', '400': '1440p', '401': '2160p',
    '402': '4320p', '571': '4320p'
};

// ==================== INICIALIZACIÓN ====================

chrome.runtime.onInstalled.addListener(async () => {
    console.log('[Video Detector HD] Extensión instalada/actualizada v2.3');

    // Limpiar reglas anteriores de declarativeNetRequest
    try {
        const existingRules = await chrome.declarativeNetRequest.getDynamicRules();
        const ruleIds = existingRules.map(rule => rule.id);
        if (ruleIds.length > 0) {
            await chrome.declarativeNetRequest.updateDynamicRules({
                removeRuleIds: ruleIds
            });
        }
    } catch (e) {
        console.log('[Video Detector HD] declarativeNetRequest no disponible:', e.message);
    }

    console.log('[Video Detector HD] Extensión lista');
});

// ==================== INTERCEPTAR PETICIONES DE RED ====================

// Listener para peticiones completadas
chrome.webRequest.onCompleted.addListener(
    (details) => {
        processNetworkRequest(details);
    },
    {
        urls: ['<all_urls>'], // Interceptar TODO para no perder nada
        types: REQUEST_TYPES
    },
    ['responseHeaders']
);

// Listener adicional para headers de respuesta
chrome.webRequest.onHeadersReceived.addListener(
    (details) => {
        // Verificar Content-Type para videos
        const contentType = details.responseHeaders?.find(h =>
            h.name.toLowerCase() === 'content-type'
        )?.value?.toLowerCase() || '';

        if (contentType.includes('video') ||
            contentType.includes('mpegurl') ||
            contentType.includes('dash+xml') ||
            contentType.includes('x-flv') ||
            contentType.includes('octet-stream')) {

            processNetworkRequest(details, true);
        }
    },
    {
        urls: ['<all_urls>'],
        types: REQUEST_TYPES
    },
    ['responseHeaders']
);

function processNetworkRequest(details, fromContentType = false) {
    const url = details.url;
    const tabId = details.tabId;

    if (tabId < 0) return;

    // Verificar si es un video
    const isVideo = isVideoURL(url) || fromContentType;

    if (isVideo && !urlPatterns.has(url)) {
        urlPatterns.set(url, Date.now());

        // Obtener información de headers
        let contentLength = 0;
        let mimeType = 'unknown';

        if (details.responseHeaders) {
            const contentType = details.responseHeaders.find(h =>
                h.name.toLowerCase() === 'content-type'
            );
            const contentLengthHeader = details.responseHeaders.find(h =>
                h.name.toLowerCase() === 'content-length'
            );

            if (contentType) mimeType = contentType.value;
            if (contentLengthHeader) contentLength = parseInt(contentLengthHeader.value) || 0;
        }

        // Detectar calidad de la URL
        const quality = detectQualityFromURL(url);

        // Solo guardar si parece un video real (no segmentos pequeños)
        const isRealVideo = contentLength > 100000 || // > 100KB
                          url.match(/\.(mp4|webm|m3u8|mpd|mkv|avi|mov)/i) ||
                          mimeType.includes('video') ||
                          mimeType.includes('mpegurl');

        if (isRealVideo || fromContentType) {
            storeVideo(tabId, {
                url: url,
                source: 'network-intercept',
                mimeType: mimeType,
                size: contentLength,
                quality: quality,
                method: details.method,
                statusCode: details.statusCode,
                timestamp: Date.now()
            });

            console.log(`[Video Detector HD] Video detectado (${quality}):`, url.substring(0, 80));
        }
    }
}

// ==================== DETECTAR CALIDAD ====================

function detectQualityFromURL(url) {
    const lower = url.toLowerCase();

    // Buscar patrones de calidad directos
    for (const [quality, pattern] of Object.entries(QUALITY_PATTERNS)) {
        if (pattern.test(lower)) {
            return quality;
        }
    }

    // Buscar en parámetros de URL
    try {
        const urlObj = new URL(url);
        const params = urlObj.searchParams;

        // YouTube itag
        const itag = params.get('itag');
        if (itag && YOUTUBE_ITAG_MAP[itag]) {
            return YOUTUBE_ITAG_MAP[itag];
        }

        // Otros parámetros de calidad
        const qualityParams = ['quality', 'q', 'res', 'resolution', 'size', 'height'];
        for (const param of qualityParams) {
            const value = params.get(param);
            if (value) {
                for (const [quality, pattern] of Object.entries(QUALITY_PATTERNS)) {
                    if (pattern.test(value)) {
                        return quality;
                    }
                }
                // Valor numérico directo
                const numMatch = value.match(/(\d+)/);
                if (numMatch) {
                    const height = parseInt(numMatch[1]);
                    if (height >= 2160) return '4K';
                    if (height >= 1440) return '1440p';
                    if (height >= 1080) return '1080p';
                    if (height >= 720) return '720p';
                    if (height >= 480) return '480p';
                    if (height >= 360) return '360p';
                }
            }
        }

        // Buscar en el path
        const pathMatch = urlObj.pathname.match(/(\d{3,4})p/i);
        if (pathMatch) {
            const height = parseInt(pathMatch[1]);
            if (height >= 2160) return '4K';
            if (height >= 1440) return '1440p';
            if (height >= 1080) return '1080p';
            if (height >= 720) return '720p';
            if (height >= 480) return '480p';
            if (height >= 360) return '360p';
        }
    } catch (e) {}

    return 'HD'; // Asumir HD por defecto
}

// ==================== DETECTAR SI ES VIDEO ====================

function isVideoURL(url) {
    const lower = url.toLowerCase();

    // Extensiones de video
    const videoExtensions = [
        '.mp4', '.webm', '.m3u8', '.mpd', '.flv',
        '.avi', '.mov', '.mkv', '.m4v', '.ogv', '.ts',
        '.m4s', '.f4v', '.3gp', '.wmv'
    ];

    // Keywords que indican video
    const videoKeywords = [
        'video', 'stream', 'media', 'videoplayback',
        'manifest', 'playlist', 'chunk', 'segment',
        'googlevideo.com', 'vimeo', 'brightcove',
        'jwplayer', 'flowplayer', 'bitmovin',
        'mux.com', 'wistia', 'loom', 'akamai'
    ];

    // Patrones regex
    const streamPatterns = [
        /\.m3u8/i, /\.mpd/i, /manifest/i, /playlist/i,
        /chunklist/i, /segment[-_]?\d+/i, /chunk[-_]?\d+/i,
        /\/api\/manifest/i, /master\.m3u8/i, /index\.m3u8/i,
        /videoplayback\?/i, /itag=\d+/i, /\/v\d+\/video/i,
        /\.f\d+\.mp4/i, /range=\d+-\d+/i
    ];

    // Verificar extensiones
    if (videoExtensions.some(ext => lower.includes(ext))) return true;

    // Verificar keywords
    if (videoKeywords.some(keyword => lower.includes(keyword))) return true;

    // Verificar patrones regex
    if (streamPatterns.some(pattern => pattern.test(url))) return true;

    return false;
}

// ==================== DETECTAR TIPO DE STREAM ====================

function detectStreamType(url) {
    const lower = url.toLowerCase();

    if (lower.includes('.m3u8') || lower.includes('playlist')) return 'HLS';
    if (lower.includes('.mpd') || lower.includes('dash')) return 'DASH';
    if (lower.includes('.mp4')) return 'MP4';
    if (lower.includes('.webm')) return 'WebM';
    if (lower.includes('.mkv')) return 'MKV';
    if (lower.includes('.ts')) return 'MPEG-TS';
    if (lower.includes('.m4s')) return 'fMP4';
    if (lower.includes('googlevideo.com') || lower.includes('youtube')) return 'YouTube';
    if (lower.includes('vimeo')) return 'Vimeo';

    return 'Video';
}

// ==================== ALMACENAR VIDEOS ====================

function storeVideo(tabId, videoData) {
    if (!detectedVideos[tabId]) {
        detectedVideos[tabId] = [];
    }

    // Evitar duplicados
    const exists = detectedVideos[tabId].find(v => v.url === videoData.url);
    if (exists) {
        // Actualizar si tenemos mejor información
        if (videoData.size > exists.size) exists.size = videoData.size;
        if (videoData.quality !== 'HD' && exists.quality === 'HD') exists.quality = videoData.quality;
        if (videoData.pageUrl && !exists.pageUrl) exists.pageUrl = videoData.pageUrl;
        return;
    }

    videoData.streamType = detectStreamType(videoData.url);
    videoData.qualityScore = getQualityScore(videoData.quality);

    // Obtener la URL de la página si no está presente
    if (!videoData.pageUrl) {
        chrome.tabs.get(tabId, (tab) => {
            if (tab && tab.url) {
                videoData.pageUrl = tab.url;
            }
        });
    }

    detectedVideos[tabId].push(videoData);

    // Ordenar por calidad (mejor primero)
    detectedVideos[tabId].sort((a, b) => (b.qualityScore || 0) - (a.qualityScore || 0));

    console.log(`[Video Detector HD] Almacenado (${videoData.quality} - ${videoData.streamType}):`,
                videoData.url.substring(0, 60));

    updateBadge(tabId);

    // Notificar al popup si está abierto
    chrome.runtime.sendMessage({
        action: 'video-added',
        tabId: tabId,
        video: videoData
    }).catch(() => {});
}

function getQualityScore(quality) {
    const scores = {
        '4K': 100, '2160p': 100, '2160p60': 105,
        '1440p': 90, '1440p60': 95,
        '1080p': 80, '1080p60': 85,
        '720p': 70, '720p60': 75,
        '480p': 50,
        '360p': 30,
        '240p': 20,
        '144p': 10,
        'HD': 60, // Asumir algo medio si no sabemos
        'unknown': 0
    };
    return scores[quality] || 60;
}

// ==================== ACTUALIZAR BADGE ====================

function updateBadge(tabId) {
    const count = detectedVideos[tabId]?.length || 0;

    if (count > 0) {
        const bestQuality = detectedVideos[tabId][0]?.quality || '';
        const badgeText = count.toString();

        // Color según calidad
        let color = '#4CAF50'; // Verde por defecto
        if (bestQuality.includes('4K') || bestQuality.includes('2160')) {
            color = '#9C27B0'; // Morado para 4K
        } else if (bestQuality.includes('1080')) {
            color = '#2196F3'; // Azul para 1080p
        } else if (bestQuality.includes('720')) {
            color = '#4CAF50'; // Verde para 720p
        }

        chrome.action.setBadgeText({ tabId: tabId, text: badgeText });
        chrome.action.setBadgeBackgroundColor({ tabId: tabId, color: color });
    } else {
        chrome.action.setBadgeText({ tabId: tabId, text: '' });
    }
}

// ==================== DESCARGAR VIDEO ====================

async function downloadVideo(videoData, preferredQuality = 'highest') {
    console.log('[Video Detector HD] Descargando:', videoData.url.substring(0, 60));

    try {
        // Para streams HLS
        if (videoData.streamType === 'HLS' || videoData.url.includes('.m3u8')) {
            return await downloadHLSStream(videoData);
        }

        // Para DASH
        if (videoData.streamType === 'DASH' || videoData.url.includes('.mpd')) {
            // DASH es más complejo, sugerir alternativa
            return {
                success: true,
                type: 'dash',
                url: videoData.url,
                message: `Stream DASH detectado.\n\nPara descargar en máxima calidad, usa:\nyt-dlp "${videoData.pageUrl || videoData.url}"`
            };
        }

        // Descarga directa para MP4/WebM
        const filename = generateFilename(videoData);

        const downloadId = await chrome.downloads.download({
            url: videoData.url,
            filename: `videos/${filename}`,
            saveAs: true,
            conflictAction: 'uniquify'
        });

        console.log('[Video Detector HD] Descarga iniciada ID:', downloadId);

        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: 'Descarga HD iniciada',
            message: `${filename} (${videoData.quality})`
        });

        return { success: true, downloadId: downloadId };

    } catch (error) {
        console.error('[Video Detector HD] Error descargando:', error);

        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: 'Error de descarga',
            message: error.message
        });

        return { success: false, error: error.message };
    }
}

// ==================== DESCARGAR STREAM HLS ====================

async function downloadHLSStream(videoData) {
    console.log('[Video Detector HD] Descargando HLS:', videoData.url.substring(0, 60));

    try {
        // Obtener el playlist con headers completos
        const response = await fetch(videoData.url, {
            credentials: 'include',
            headers: {
                'Accept': '*/*',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Origin': new URL(videoData.url).origin,
                'Referer': videoData.pageUrl || videoData.url
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const content = await response.text();
        console.log('[Video Detector HD] Contenido M3U8:', content.substring(0, 500));

        // Usar la URL completa como base (incluyendo query params para tokens)
        const urlObj = new URL(videoData.url);
        const baseUrl = videoData.url.substring(0, videoData.url.lastIndexOf('/') + 1);
        const queryParams = urlObj.search; // Preservar tokens de autenticación

        // Parsear M3U8 pasando la URL original para tokens
        const playlist = parseM3U8(content, baseUrl, videoData.url);

        // Si tiene variantes, obtener la mejor
        if (playlist.variants && playlist.variants.length > 0) {
            const bestVariant = playlist.variants[playlist.variants.length - 1];
            console.log('[Video Detector HD] Mejor variante:', bestVariant.resolution, bestVariant.bandwidth);

            // Obtener playlist de segmentos con headers de auth
            const variantResponse = await fetch(bestVariant.url, {
                credentials: 'include',
                headers: {
                    'Accept': '*/*',
                    'Origin': new URL(videoData.url).origin,
                    'Referer': videoData.pageUrl || videoData.url
                }
            });

            if (!variantResponse.ok) {
                console.error('[Video Detector HD] Error obteniendo variante:', variantResponse.status);
                throw new Error(`Error HTTP ${variantResponse.status} al obtener variante`);
            }

            const variantContent = await variantResponse.text();
            console.log('[Video Detector HD] Variante contenido:', variantContent.substring(0, 300));

            const variantBase = bestVariant.url.substring(0, bestVariant.url.lastIndexOf('/') + 1);
            const segmentPlaylist = parseM3U8(variantContent, variantBase, bestVariant.url);

            if (segmentPlaylist.segments && segmentPlaylist.segments.length > 0) {
                return await downloadSegments(segmentPlaylist.segments, videoData, bestVariant.resolution);
            }
        }

        // Si tiene segmentos directamente (no es master playlist)
        if (playlist.segments && playlist.segments.length > 0) {
            console.log('[Video Detector HD] Descargando', playlist.segments.length, 'segmentos directamente');
            return await downloadSegments(playlist.segments, videoData);
        }

        // Si no pudimos parsear, dar URL directa del HLS para yt-dlp
        const hlsUrl = videoData.url;
        const ytdlpCommand = `python -m yt_dlp "${hlsUrl}"`;
        return {
            success: true,
            type: 'hls',
            masterUrl: hlsUrl,
            segments: [],
            ytdlpCommand: ytdlpCommand,
            message: `Stream HLS detectado.\n\nComando copiado al portapapeles:\n${ytdlpCommand}`
        };

    } catch (error) {
        console.error('[Video Detector HD] Error HLS:', error);

        // Dar URL directa del HLS
        const hlsUrl = videoData.url;
        const ytdlpCommand = `python -m yt_dlp "${hlsUrl}"`;
        return {
            success: true,
            type: 'hls',
            masterUrl: hlsUrl,
            segments: [],
            error: error.message,
            ytdlpCommand: ytdlpCommand,
            message: `Stream HLS detectado.\n\nComando copiado al portapapeles:\n${ytdlpCommand}`
        };
    }
}

// Parsear M3U8 - Mejorado para preservar tokens de autenticación
function parseM3U8(content, baseUrl, originalUrl = '') {
    const lines = content.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('##'));
    const result = { variants: [], segments: [], keys: [] };

    // Extraer query params del URL original para tokens de autenticación
    let authParams = '';
    try {
        const urlObj = new URL(originalUrl || baseUrl);
        authParams = urlObj.search;
    } catch (e) {}

    console.log('[Video Detector HD] Parseando M3U8, líneas:', lines.length);

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Variantes de calidad (master playlist)
        if (line.startsWith('#EXT-X-STREAM-INF')) {
            const attrs = parseM3U8Attributes(line);
            let nextLine = lines[i + 1];

            if (nextLine && !nextLine.startsWith('#')) {
                // Agregar tokens de auth si la URL no los tiene
                let variantUrl = resolveUrl(nextLine, baseUrl);
                if (authParams && !variantUrl.includes('token') && !variantUrl.includes('?')) {
                    variantUrl += authParams;
                }

                result.variants.push({
                    url: variantUrl,
                    bandwidth: parseInt(attrs.BANDWIDTH) || 0,
                    resolution: attrs.RESOLUTION || 'unknown',
                    codecs: attrs.CODECS || ''
                });
                i++;
            }
        }

        // Segmentos de video
        if (line.startsWith('#EXTINF')) {
            const durationMatch = line.match(/#EXTINF:([\d.]+)/);
            const duration = durationMatch ? parseFloat(durationMatch[1]) : 0;
            let nextLine = lines[i + 1];

            if (nextLine && !nextLine.startsWith('#')) {
                let segmentUrl = resolveUrl(nextLine, baseUrl);

                // Agregar tokens de auth si la URL no los tiene
                if (authParams && !segmentUrl.includes('token') && !segmentUrl.includes('bcdn_token')) {
                    // Solo agregar si el segmento no tiene sus propios params
                    if (!segmentUrl.includes('?')) {
                        segmentUrl += authParams;
                    }
                }

                result.segments.push({
                    url: segmentUrl,
                    duration: duration
                });
                i++;
            }
        }

        // Capturar keys de encriptación
        if (line.startsWith('#EXT-X-KEY')) {
            const attrs = parseM3U8Attributes(line);
            if (attrs.URI) {
                result.keys.push({
                    method: attrs.METHOD || 'AES-128',
                    uri: resolveUrl(attrs.URI.replace(/"/g, ''), baseUrl),
                    iv: attrs.IV
                });
            }
        }

        // Capturar media alternativo (audio, subtítulos)
        if (line.startsWith('#EXT-X-MEDIA')) {
            const attrs = parseM3U8Attributes(line);
            if (attrs.URI && attrs.TYPE === 'AUDIO') {
                result.audioTrack = resolveUrl(attrs.URI.replace(/"/g, ''), baseUrl);
            }
        }
    }

    // Ordenar variantes por bandwidth (mejor calidad al final)
    result.variants.sort((a, b) => a.bandwidth - b.bandwidth);

    console.log('[Video Detector HD] M3U8 parseado:', {
        variantes: result.variants.length,
        segmentos: result.segments.length,
        keys: result.keys.length
    });

    return result;
}

function parseM3U8Attributes(line) {
    const attrs = {};
    const match = line.match(/:(.+)$/);

    if (match) {
        const regex = /([A-Z0-9-]+)=("[^"]*"|[^,]*)/g;
        let m;
        while ((m = regex.exec(match[1])) !== null) {
            attrs[m[1]] = m[2].replace(/"/g, '');
        }
    }

    return attrs;
}

function resolveUrl(url, baseUrl) {
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }
    try {
        return new URL(url, baseUrl).href;
    } catch (e) {
        return baseUrl + url;
    }
}

// Descargar segmentos
async function downloadSegments(segments, videoData, resolution = '') {
    console.log(`[Video Detector HD] Descargando ${segments.length} segmentos...`);

    chrome.notifications.create('download-progress', {
        type: 'progress',
        iconUrl: 'icons/icon128.png',
        title: 'Descargando video HD',
        message: `0/${segments.length} segmentos`,
        progress: 0
    });

    const chunks = [];
    let downloaded = 0;

    for (const segment of segments) {
        try {
            const response = await fetch(segment.url, { credentials: 'include' });

            if (response.ok) {
                const arrayBuffer = await response.arrayBuffer();
                chunks.push(new Uint8Array(arrayBuffer));
                downloaded++;

                // Actualizar progreso
                const progress = Math.round((downloaded / segments.length) * 100);
                chrome.notifications.update('download-progress', {
                    message: `${downloaded}/${segments.length} segmentos`,
                    progress: progress
                });
            }
        } catch (e) {
            console.warn('[Video Detector HD] Error en segmento:', e.message);
        }
    }

    if (chunks.length === 0) {
        chrome.notifications.clear('download-progress');
        throw new Error('No se pudieron descargar segmentos');
    }

    // Combinar chunks
    const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const combined = new Uint8Array(totalLength);
    let offset = 0;

    for (const chunk of chunks) {
        combined.set(chunk, offset);
        offset += chunk.length;
    }

    console.log(`[Video Detector HD] Combinado: ${formatBytes(totalLength)}`);

    // Crear blob y descargar
    const blob = new Blob([combined], { type: 'video/mp2t' });
    const blobUrl = URL.createObjectURL(blob);

    const quality = resolution || videoData.quality || 'HD';
    const filename = `video_${quality}_${Date.now()}.ts`;

    const downloadId = await chrome.downloads.download({
        url: blobUrl,
        filename: `videos/${filename}`,
        saveAs: true
    });

    // Limpiar
    setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
    chrome.notifications.clear('download-progress');

    chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: 'Descarga completada',
        message: `${filename} (${formatBytes(totalLength)})`
    });

    return { success: true, downloadId, size: totalLength, segments: downloaded };
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function generateFilename(videoData) {
    try {
        const url = new URL(videoData.url);
        let filename = url.pathname.split('/').pop();
        filename = filename.split('?')[0];

        if (!filename || !filename.includes('.') || filename.length < 3) {
            const ext = getExtensionFromType(videoData.streamType);
            const quality = videoData.quality || 'HD';
            filename = `video_${quality}_${Date.now()}${ext}`;
        }

        // Agregar calidad si no la tiene
        if (videoData.quality && !filename.toLowerCase().includes(videoData.quality.toLowerCase())) {
            const ext = filename.substring(filename.lastIndexOf('.'));
            const name = filename.substring(0, filename.lastIndexOf('.'));
            filename = `${name}_${videoData.quality}${ext}`;
        }

        // Sanitizar
        filename = filename.replace(/[<>:"/\\|?*]/g, '_');
        if (filename.length > 100) {
            const ext = filename.substring(filename.lastIndexOf('.'));
            filename = filename.substring(0, 95) + ext;
        }

        return filename;
    } catch (e) {
        return `video_${Date.now()}.mp4`;
    }
}

function getExtensionFromType(streamType) {
    const extensions = {
        'MP4': '.mp4', 'YouTube': '.mp4', 'Vimeo': '.mp4',
        'WebM': '.webm', 'MKV': '.mkv',
        'HLS': '.ts', 'DASH': '.mp4',
        'MPEG-TS': '.ts', 'fMP4': '.mp4'
    };
    return extensions[streamType] || '.mp4';
}

// ==================== OBTENER MEJOR CALIDAD ====================

function getBestQualityVideo(tabId, preferredQuality = 'highest') {
    const videos = detectedVideos[tabId] || [];

    if (videos.length === 0) return null;

    if (preferredQuality === 'highest') {
        return videos[0]; // Ya ordenados por calidad
    }

    // Buscar calidad específica
    const targetScore = getQualityScore(preferredQuality);

    let best = videos[0];
    let bestDiff = Math.abs((best.qualityScore || 0) - targetScore);

    for (const video of videos) {
        const diff = Math.abs((video.qualityScore || 0) - targetScore);
        if (diff < bestDiff) {
            best = video;
            bestDiff = diff;
        }
    }

    return best;
}

// ==================== MENSAJES ====================

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('[Video Detector HD] Mensaje:', message.action);

    switch (message.action) {
        case 'getVideos':
            const videos = detectedVideos[message.tabId] || [];
            sendResponse({ videos: videos });
            break;

        case 'exportAllCookies':
            // Exportar todas las cookies del dominio usando la API de Chrome
            exportCookiesForDomain(message.url)
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        case 'video-detected-from-dom':
            if (sender.tab?.id) {
                const quality = message.video.quality || detectQualityFromURL(message.video.url || '');
                message.video.quality = quality;
                storeVideo(sender.tab.id, message.video);
            }
            sendResponse({ success: true });
            break;

        case 'downloadVideo':
            downloadVideo(message.video, message.quality || 'highest')
                .then(result => sendResponse(result))
                .catch(error => sendResponse({ success: false, error: error.message }));
            return true;

        case 'downloadBestQuality':
            const best = getBestQualityVideo(message.tabId, message.quality || 'highest');
            if (best) {
                downloadVideo(best, message.quality || 'highest')
                    .then(result => sendResponse(result))
                    .catch(error => sendResponse({ success: false, error: error.message }));
            } else {
                sendResponse({ success: false, error: 'No se encontraron videos' });
            }
            return true;

        case 'clearVideos':
            detectedVideos[message.tabId] = [];
            updateBadge(message.tabId);
            sendResponse({ success: true });
            break;

        case 'getPageVideoUrl':
            chrome.tabs.get(message.tabId, (tab) => {
                sendResponse({ pageUrl: tab?.url });
            });
            return true;

        case 'forceDetection':
            // Forzar re-escaneo de la pestaña
            chrome.scripting.executeScript({
                target: { tabId: message.tabId },
                func: () => {
                    // Trigger re-detection
                    document.querySelectorAll('video').forEach(v => {
                        if (v.src || v.currentSrc) {
                            console.log('[Video Detector HD] Video encontrado:', v.src || v.currentSrc);
                        }
                    });
                }
            }).catch(console.error);
            sendResponse({ success: true });
            break;

        default:
            sendResponse({ success: false, error: 'Acción no reconocida' });
    }
});

// ==================== LIMPIAR AL CERRAR PESTAÑAS ====================

chrome.tabs.onRemoved.addListener((tabId) => {
    delete detectedVideos[tabId];
});

// Limpiar cache periódicamente
setInterval(() => {
    const now = Date.now();
    const maxAge = 10 * 60 * 1000; // 10 minutos

    for (const [url, timestamp] of urlPatterns.entries()) {
        if (now - timestamp > maxAge) {
            urlPatterns.delete(url);
        }
    }
}, 5 * 60 * 1000);

// ==================== EXPORTAR COOKIES ====================

async function exportCookiesForDomain(url) {
    try {
        const urlObj = new URL(url);
        const domain = urlObj.hostname;

        // Lista de dominios a exportar (el principal + relacionados comunes)
        const domainsToExport = new Set();

        // Agregar dominio principal y sus variantes
        domainsToExport.add(domain);
        const baseDomain = domain.split('.').slice(-2).join('.');
        domainsToExport.add(baseDomain);
        domainsToExport.add('.' + baseDomain);

        // Dominios comunes de autenticación y CDN
        const relatedDomains = [
            'circle.so', '.circle.so',
            'cdn-media.circle.so',
            'thatopen.com', '.thatopen.com',
            'auth0.com', '.auth0.com',
            'cloudflare.com', '.cloudflare.com'
        ];

        // Si es un subdominio, agregar el dominio padre
        const parts = domain.split('.');
        if (parts.length > 2) {
            domainsToExport.add(parts.slice(-2).join('.'));
            domainsToExport.add('.' + parts.slice(-2).join('.'));
        }

        relatedDomains.forEach(d => domainsToExport.add(d));

        console.log('[Video Detector HD] Buscando cookies en dominios:', Array.from(domainsToExport));

        // Obtener cookies de todos los dominios
        const allCookies = [];
        const seenCookies = new Set();

        for (const d of domainsToExport) {
            try {
                const cookies = await chrome.cookies.getAll({ domain: d });
                cookies.forEach(cookie => {
                    const key = `${cookie.domain}|${cookie.name}|${cookie.path}`;
                    if (!seenCookies.has(key)) {
                        seenCookies.add(key);
                        allCookies.push(cookie);
                    }
                });
            } catch (e) {
                // Ignorar errores de dominios específicos
            }
        }

        // También obtener TODAS las cookies si hay pocas
        if (allCookies.length < 20) {
            try {
                const allBrowserCookies = await chrome.cookies.getAll({});
                allBrowserCookies.forEach(cookie => {
                    // Incluir cookies que podrían ser relevantes
                    if (cookie.domain.includes('circle') ||
                        cookie.domain.includes('thatopen') ||
                        cookie.domain.includes(baseDomain) ||
                        cookie.name.includes('session') ||
                        cookie.name.includes('auth') ||
                        cookie.name.includes('token') ||
                        cookie.name.includes('user') ||
                        cookie.name.includes('csrf') ||
                        cookie.name.includes('_')) {

                        const key = `${cookie.domain}|${cookie.name}|${cookie.path}`;
                        if (!seenCookies.has(key)) {
                            seenCookies.add(key);
                            allCookies.push(cookie);
                        }
                    }
                });
            } catch (e) {}
        }

        // Convertir a formato Netscape
        let output = '# Netscape HTTP Cookie File\n';
        output += '# Generated by Video Detector HD Extension\n';
        output += '# This file can be used with yt-dlp: yt-dlp --cookies cookies.txt URL\n\n';

        allCookies.forEach(cookie => {
            const cookieDomain = cookie.domain.startsWith('.') ? cookie.domain : '.' + cookie.domain;
            const flag = cookie.domain.startsWith('.') ? 'TRUE' : 'FALSE';
            const path = cookie.path || '/';
            const secure = cookie.secure ? 'TRUE' : 'FALSE';
            const expiry = cookie.expirationDate ? Math.floor(cookie.expirationDate) : Math.floor(Date.now() / 1000) + 86400 * 365;
            const name = cookie.name;
            const value = cookie.value;

            output += `${cookieDomain}\t${flag}\t${path}\t${secure}\t${expiry}\t${name}\t${value}\n`;
        });

        console.log(`[Video Detector HD] Exportadas ${allCookies.length} cookies para ${domain} y dominios relacionados`);

        return {
            success: true,
            cookies: output,
            count: allCookies.length,
            domain: domain
        };

    } catch (error) {
        console.error('[Video Detector HD] Error exportando cookies:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

console.log('[Video Detector HD] Sistema de detección HD v2.3 activado');
