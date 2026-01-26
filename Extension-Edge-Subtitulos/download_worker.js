// download_worker.js - Worker para descargar streams HLS/DASH

let downloadProgress = {};

// Escuchar mensajes del background
self.onmessage = async function(e) {
    const { action, data, downloadId } = e.data;

    if (action === 'downloadHLS') {
        try {
            const result = await downloadHLSStream(data.url, data.headers, downloadId);
            self.postMessage({ action: 'complete', downloadId, result });
        } catch (error) {
            self.postMessage({ action: 'error', downloadId, error: error.message });
        }
    } else if (action === 'downloadSegments') {
        try {
            const result = await downloadSegments(data.segments, data.headers, downloadId);
            self.postMessage({ action: 'complete', downloadId, result });
        } catch (error) {
            self.postMessage({ action: 'error', downloadId, error: error.message });
        }
    }
};

// Descargar stream HLS
async function downloadHLSStream(masterUrl, headers = {}, downloadId) {
    console.log('[Worker] Descargando HLS:', masterUrl);

    // Obtener el playlist master
    const masterContent = await fetchWithHeaders(masterUrl, headers);

    // Parsear el playlist
    const playlists = parseM3U8(masterContent, masterUrl);

    if (playlists.length === 0) {
        throw new Error('No se encontraron playlists en el m3u8');
    }

    // Seleccionar la mejor calidad (última en la lista generalmente es la mejor)
    const bestPlaylist = playlists[playlists.length - 1];

    console.log('[Worker] Playlist seleccionado:', bestPlaylist);

    // Si es un playlist de segmentos directamente
    if (bestPlaylist.segments && bestPlaylist.segments.length > 0) {
        return await downloadSegments(bestPlaylist.segments, headers, downloadId);
    }

    // Si es un master playlist, obtener el playlist de segmentos
    const segmentPlaylistContent = await fetchWithHeaders(bestPlaylist.url, headers);
    const segmentPlaylist = parseM3U8(segmentPlaylistContent, bestPlaylist.url);

    if (segmentPlaylist.length > 0 && segmentPlaylist[0].segments) {
        return await downloadSegments(segmentPlaylist[0].segments, headers, downloadId);
    }

    throw new Error('No se pudieron extraer los segmentos del stream');
}

// Parsear M3U8
function parseM3U8(content, baseUrl) {
    const lines = content.split('\n').map(l => l.trim()).filter(l => l);
    const playlists = [];
    let currentPlaylist = null;
    let segments = [];

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        if (line.startsWith('#EXT-X-STREAM-INF')) {
            // Es un master playlist
            const attrs = parseAttributes(line);
            const nextLine = lines[i + 1];

            if (nextLine && !nextLine.startsWith('#')) {
                playlists.push({
                    url: resolveUrl(nextLine, baseUrl),
                    bandwidth: parseInt(attrs.BANDWIDTH) || 0,
                    resolution: attrs.RESOLUTION || 'unknown',
                    codecs: attrs.CODECS || ''
                });
                i++;
            }
        } else if (line.startsWith('#EXTINF')) {
            // Es un segmento
            const duration = parseFloat(line.split(':')[1]) || 0;
            const nextLine = lines[i + 1];

            if (nextLine && !nextLine.startsWith('#')) {
                segments.push({
                    url: resolveUrl(nextLine, baseUrl),
                    duration: duration
                });
                i++;
            }
        }
    }

    // Si encontramos segmentos directamente (no es master playlist)
    if (segments.length > 0) {
        playlists.push({ segments: segments });
    }

    return playlists;
}

// Parsear atributos de una línea M3U8
function parseAttributes(line) {
    const attrs = {};
    const match = line.match(/:(.+)$/);

    if (match) {
        const attrString = match[1];
        const regex = /([A-Z-]+)=("[^"]*"|[^,]*)/g;
        let m;

        while ((m = regex.exec(attrString)) !== null) {
            attrs[m[1]] = m[2].replace(/"/g, '');
        }
    }

    return attrs;
}

// Resolver URL relativa
function resolveUrl(url, baseUrl) {
    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }

    try {
        return new URL(url, baseUrl).href;
    } catch (e) {
        // Fallback: concatenar
        const base = baseUrl.substring(0, baseUrl.lastIndexOf('/') + 1);
        return base + url;
    }
}

// Descargar segmentos y combinarlos
async function downloadSegments(segments, headers, downloadId) {
    console.log(`[Worker] Descargando ${segments.length} segmentos...`);

    const chunks = [];
    let downloaded = 0;
    const total = segments.length;

    for (const segment of segments) {
        try {
            const response = await fetch(segment.url, {
                headers: headers,
                credentials: 'include'
            });

            if (!response.ok) {
                console.warn(`[Worker] Error descargando segmento: ${response.status}`);
                continue;
            }

            const arrayBuffer = await response.arrayBuffer();
            chunks.push(new Uint8Array(arrayBuffer));

            downloaded++;

            // Reportar progreso
            self.postMessage({
                action: 'progress',
                downloadId,
                progress: {
                    downloaded,
                    total,
                    percent: Math.round((downloaded / total) * 100)
                }
            });

        } catch (error) {
            console.warn(`[Worker] Error en segmento:`, error);
        }
    }

    if (chunks.length === 0) {
        throw new Error('No se pudo descargar ningún segmento');
    }

    // Combinar todos los chunks en un solo buffer
    const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const combined = new Uint8Array(totalLength);
    let offset = 0;

    for (const chunk of chunks) {
        combined.set(chunk, offset);
        offset += chunk.length;
    }

    console.log(`[Worker] Descarga completa: ${formatBytes(totalLength)}`);

    return {
        data: combined.buffer,
        size: totalLength,
        segments: downloaded,
        type: 'video/mp2t' // MPEG-TS típico de HLS
    };
}

// Fetch con headers personalizados
async function fetchWithHeaders(url, headers = {}) {
    const response = await fetch(url, {
        headers: {
            ...headers,
            'Accept': '*/*'
        },
        credentials: 'include'
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.text();
}

// Formatear bytes
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

console.log('[Download Worker] Iniciado');
