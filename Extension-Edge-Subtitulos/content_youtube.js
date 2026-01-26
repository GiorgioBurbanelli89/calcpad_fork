// content_youtube.js - Detector ESPECIALIZADO para YouTube
// Basado en técnicas de Video DownloadHelper pero implementación propia

(function() {
    'use strict';

    console.log('[Video Detector - YouTube] Script cargado');

    let detectedVideos = new Set();

    // ==================== INTERCEPTAR API INTERNA DE YOUTUBE ====================

    function interceptYouTubePlayer() {
        // YouTube usa ytInitialPlayerResponse para cargar datos del video
        let ytInitialPlayerResponse = null;

        // Buscar en window.ytInitialPlayerResponse
        if (window.ytInitialPlayerResponse) {
            ytInitialPlayerResponse = window.ytInitialPlayerResponse;
            console.log('[Video Detector - YouTube] ytInitialPlayerResponse encontrado');
            extractVideoInfo(ytInitialPlayerResponse);
        }

        // Observar cambios en el DOM para detectar cuando se carga el player
        const observer = new MutationObserver(() => {
            if (window.ytInitialPlayerResponse && window.ytInitialPlayerResponse !== ytInitialPlayerResponse) {
                ytInitialPlayerResponse = window.ytInitialPlayerResponse;
                console.log('[Video Detector - YouTube] ytInitialPlayerResponse actualizado');
                extractVideoInfo(ytInitialPlayerResponse);
            }
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    // ==================== EXTRAER INFORMACIÓN DEL VIDEO ====================

    function extractVideoInfo(playerResponse) {
        try {
            if (!playerResponse.streamingData) {
                console.log('[Video Detector - YouTube] Sin streamingData');
                return;
            }

            const streamingData = playerResponse.streamingData;
            const videoDetails = playerResponse.videoDetails;

            // Extraer formatos disponibles
            let formats = [];

            if (streamingData.formats) {
                formats = formats.concat(streamingData.formats);
            }

            if (streamingData.adaptiveFormats) {
                formats = formats.concat(streamingData.adaptiveFormats);
            }

            console.log(`[Video Detector - YouTube] ${formats.length} formatos encontrados`);

            // Procesar cada formato
            formats.forEach(format => {
                if (format.url && !detectedVideos.has(format.url)) {
                    detectedVideos.add(format.url);

                    const videoData = {
                        url: format.url,
                        source: 'youtube-api',
                        quality: format.qualityLabel || format.quality || 'unknown',
                        fps: format.fps || 30,
                        width: format.width || 0,
                        height: format.height || 0,
                        mimeType: format.mimeType || 'video/mp4',
                        bitrate: format.bitrate || 0,
                        videoTitle: videoDetails?.title || 'YouTube Video',
                        videoId: videoDetails?.videoId || '',
                        timestamp: Date.now()
                    };

                    notifyVideoFound(videoData);

                    console.log(`[Video Detector - YouTube] Video detectado: ${videoData.quality} (${videoData.width}x${videoData.height})`);
                }
            });

            // Extraer manifest HLS si existe
            if (streamingData.hlsManifestUrl && !detectedVideos.has(streamingData.hlsManifestUrl)) {
                detectedVideos.add(streamingData.hlsManifestUrl);

                notifyVideoFound({
                    url: streamingData.hlsManifestUrl,
                    source: 'youtube-hls',
                    streamType: 'HLS',
                    videoTitle: videoDetails?.title || 'YouTube Video',
                    videoId: videoDetails?.videoId || '',
                    timestamp: Date.now()
                });

                console.log('[Video Detector - YouTube] HLS manifest detectado');
            }

            // Extraer manifest DASH si existe
            if (streamingData.dashManifestUrl && !detectedVideos.has(streamingData.dashManifestUrl)) {
                detectedVideos.add(streamingData.dashManifestUrl);

                notifyVideoFound({
                    url: streamingData.dashManifestUrl,
                    source: 'youtube-dash',
                    streamType: 'DASH',
                    videoTitle: videoDetails?.title || 'YouTube Video',
                    videoId: videoDetails?.videoId || '',
                    timestamp: Date.now()
                });

                console.log('[Video Detector - YouTube] DASH manifest detectado');
            }

        } catch (error) {
            console.error('[Video Detector - YouTube] Error extrayendo info:', error);
        }
    }

    // ==================== INTERCEPTAR PETICIONES FETCH ====================

    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];

        if (typeof url === 'string') {
            // Detectar peticiones de video de YouTube
            if (url.includes('googlevideo.com') ||
                url.includes('youtube.com/api/timedtext') ||
                url.includes('youtube.com/get_video_info')) {

                console.log('[Video Detector - YouTube] Petición detectada via fetch:', url);

                if (!detectedVideos.has(url)) {
                    detectedVideos.add(url);

                    notifyVideoFound({
                        url: url,
                        source: 'youtube-fetch',
                        timestamp: Date.now()
                    });
                }
            }
        }

        return originalFetch.apply(this, args);
    };

    // ==================== DETECTAR ELEMENTO <VIDEO> ====================

    function detectVideoElement() {
        const videos = document.querySelectorAll('video');

        videos.forEach(video => {
            let src = video.src;

            if (src && !src.startsWith('blob:') && !detectedVideos.has(src)) {
                detectedVideos.add(src);

                notifyVideoFound({
                    url: src,
                    source: 'youtube-video-element',
                    width: video.videoWidth || 0,
                    height: video.videoHeight || 0,
                    duration: video.duration || 0,
                    timestamp: Date.now()
                });

                console.log('[Video Detector - YouTube] Elemento <video> detectado:', src);
            }
        });
    }

    // ==================== NOTIFICAR AL BACKGROUND ====================

    function notifyVideoFound(videoData) {
        chrome.runtime.sendMessage({
            action: 'video-detected-from-dom',
            video: videoData
        }).catch(err => {
            console.error('[Video Detector - YouTube] Error enviando mensaje:', err);
        });
    }

    // ==================== INICIALIZACIÓN ====================

    function init() {
        console.log('[Video Detector - YouTube] Inicializando...');

        // Esperar a que YouTube cargue
        const checkInterval = setInterval(() => {
            if (window.ytInitialPlayerResponse) {
                clearInterval(checkInterval);
                interceptYouTubePlayer();
            }
        }, 500);

        // Timeout después de 10 segundos
        setTimeout(() => {
            clearInterval(checkInterval);
            if (!window.ytInitialPlayerResponse) {
                console.log('[Video Detector - YouTube] ytInitialPlayerResponse no encontrado, usando fallback');
            }
        }, 10000);

        // Detectar elementos <video> periódicamente
        setInterval(detectVideoElement, 3000);

        // Detectar al navegar (YouTube SPA)
        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                console.log('[Video Detector - YouTube] Navegación detectada:', url);
                setTimeout(() => {
                    if (window.ytInitialPlayerResponse) {
                        extractVideoInfo(window.ytInitialPlayerResponse);
                    }
                }, 2000);
            }
        }).observe(document.body, { childList: true, subtree: true });
    }

    // Iniciar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
