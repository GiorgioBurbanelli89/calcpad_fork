// analizar_sitio.js - ANALIZADOR DE VIDEOS EN CUALQUIER SITIO
// Copia este código en la CONSOLA del navegador (F12) estando en la página

(function() {
    console.log('========================================');
    console.log('  ANALIZADOR DE VIDEOS - INICIADO');
    console.log('========================================');

    let resultados = {
        videos: [],
        iframes: [],
        sources: [],
        scripts: [],
        redes: []
    };

    // ==================== 1. BUSCAR ELEMENTOS <VIDEO> ====================

    console.log('\n1. Buscando elementos <video>...');
    const videos = document.querySelectorAll('video');
    console.log(`   Encontrados: ${videos.length}`);

    videos.forEach((video, index) => {
        console.log(`\n   Video #${index + 1}:`);
        console.log(`   - src: ${video.src || 'ninguno'}`);
        console.log(`   - currentSrc: ${video.currentSrc || 'ninguno'}`);
        console.log(`   - dimensiones: ${video.videoWidth}x${video.videoHeight}`);
        console.log(`   - duración: ${video.duration || 'desconocida'}s`);

        // Buscar <source> dentro
        const sources = video.querySelectorAll('source');
        if (sources.length > 0) {
            console.log(`   - <source> tags: ${sources.length}`);
            sources.forEach((source, idx) => {
                console.log(`     ${idx + 1}. ${source.src} (${source.type || 'sin tipo'})`);
                resultados.sources.push({
                    src: source.src,
                    type: source.type
                });
            });
        }

        resultados.videos.push({
            src: video.src || video.currentSrc,
            width: video.videoWidth,
            height: video.videoHeight,
            duration: video.duration
        });
    });

    // ==================== 2. BUSCAR IFRAMES ====================

    console.log('\n2. Buscando iframes (videos embebidos)...');
    const iframes = document.querySelectorAll('iframe');
    console.log(`   Encontrados: ${iframes.length}`);

    iframes.forEach((iframe, index) => {
        const src = iframe.src;
        console.log(`\n   Iframe #${index + 1}:`);
        console.log(`   - src: ${src}`);

        // Detectar tipo
        if (src.includes('youtube.com') || src.includes('youtu.be')) {
            console.log(`   - TIPO: YouTube`);
            const videoId = src.match(/embed\/([^?]+)/)?.[1];
            console.log(`   - Video ID: ${videoId}`);
        } else if (src.includes('vimeo.com')) {
            console.log(`   - TIPO: Vimeo`);
        } else if (src.includes('facebook.com')) {
            console.log(`   - TIPO: Facebook`);
        } else if (src.includes('dailymotion.com')) {
            console.log(`   - TIPO: Dailymotion`);
        } else if (src.includes('wistia.com')) {
            console.log(`   - TIPO: Wistia`);
        } else {
            console.log(`   - TIPO: Desconocido`);
        }

        resultados.iframes.push({
            src: src,
            width: iframe.width,
            height: iframe.height
        });
    });

    // ==================== 3. BUSCAR EN ATRIBUTOS ====================

    console.log('\n3. Buscando atributos data-* con URLs de video...');

    const selectors = [
        '[data-src*="mp4"]',
        '[data-src*="webm"]',
        '[data-src*="m3u8"]',
        '[data-video-url]',
        '[data-video-src]',
        '[data-video-id]',
        '[data-stream-url]'
    ];

    selectors.forEach(selector => {
        try {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                console.log(`\n   Selector: ${selector}`);
                console.log(`   Encontrados: ${elements.length}`);

                elements.forEach((el, idx) => {
                    const attrs = [...el.attributes]
                        .filter(attr => attr.name.includes('video') || attr.name.includes('src') || attr.name.includes('stream'))
                        .map(attr => `${attr.name}="${attr.value}"`);

                    console.log(`   ${idx + 1}. ${attrs.join(', ')}`);
                });
            }
        } catch (e) {
            // Selector inválido
        }
    });

    // ==================== 4. BUSCAR SCRIPTS DE VIDEO ====================

    console.log('\n4. Buscando scripts de librerías de video...');

    const scripts = document.querySelectorAll('script[src]');
    const videoLibs = {
        'video.js': 'Video.js (player HTML5)',
        'jwplayer': 'JW Player',
        'plyr': 'Plyr',
        'hls.js': 'HLS.js (streaming)',
        'dash.js': 'Dash.js (MPEG-DASH)',
        'shaka-player': 'Shaka Player (Google)',
        'videojs': 'Video.js',
        'flowplayer': 'Flowplayer',
        'brightcove': 'Brightcove',
        'kaltura': 'Kaltura',
        'wistia': 'Wistia',
        'vimeo': 'Vimeo Player'
    };

    scripts.forEach(script => {
        const src = script.src.toLowerCase();
        for (const [key, name] of Object.entries(videoLibs)) {
            if (src.includes(key)) {
                console.log(`   ✓ Detectado: ${name}`);
                console.log(`     URL: ${script.src}`);
                resultados.scripts.push({ name, src: script.src });
            }
        }
    });

    // ==================== 5. INTERCEPTAR PETICIONES DE RED ====================

    console.log('\n5. Configurando interceptor de red...');
    console.log('   (Las peticiones se mostrarán cuando se hagan)');

    // Interceptar fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        if (typeof url === 'string') {
            const videoExtensions = ['.mp4', '.webm', '.m3u8', '.mpd', '.flv', '.avi', '.mov'];
            const isVideo = videoExtensions.some(ext => url.toLowerCase().includes(ext));

            if (isVideo) {
                console.log(`\n   🌐 FETCH detectado: ${url}`);
                resultados.redes.push({ method: 'fetch', url });
            }
        }
        return originalFetch.apply(this, args);
    };

    // Interceptar XMLHttpRequest
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
        if (typeof url === 'string') {
            const videoExtensions = ['.mp4', '.webm', '.m3u8', '.mpd', '.flv', '.avi', '.mov'];
            const videoKeywords = ['video', 'stream', 'media', 'manifest'];

            const isVideo = videoExtensions.some(ext => url.toLowerCase().includes(ext)) ||
                           videoKeywords.some(keyword => url.toLowerCase().includes(keyword));

            if (isVideo) {
                console.log(`\n   🌐 XHR detectado: ${url}`);
                resultados.redes.push({ method: 'xhr', url });
            }
        }
        return originalOpen.call(this, method, url, ...rest);
    };

    // ==================== 6. RESUMEN FINAL ====================

    setTimeout(() => {
        console.log('\n========================================');
        console.log('  RESUMEN DEL ANÁLISIS');
        console.log('========================================');

        console.log(`\n✓ Elementos <video>: ${resultados.videos.length}`);
        console.log(`✓ Iframes (embebidos): ${resultados.iframes.length}`);
        console.log(`✓ Tags <source>: ${resultados.sources.length}`);
        console.log(`✓ Librerías detectadas: ${resultados.scripts.length}`);

        console.log('\n--- TECNOLOGÍA DETECTADA ---');

        if (resultados.videos.length > 0) {
            console.log('✓ Usa elementos <video> HTML5 nativos');
        }

        if (resultados.iframes.length > 0) {
            console.log('✓ Usa iframes embebidos (YouTube, Vimeo, etc.)');
        }

        if (resultados.scripts.length > 0) {
            console.log('✓ Librerías de video:');
            resultados.scripts.forEach(script => {
                console.log(`  - ${script.name}`);
            });
        } else {
            console.log('✗ No se detectaron librerías conocidas');
        }

        console.log('\n--- URLS DE VIDEO ---');
        const allUrls = [
            ...resultados.videos.map(v => v.src).filter(Boolean),
            ...resultados.sources.map(s => s.src).filter(Boolean),
            ...resultados.iframes.map(i => i.src).filter(Boolean),
            ...resultados.redes.map(r => r.url)
        ];

        if (allUrls.length > 0) {
            allUrls.forEach((url, idx) => {
                console.log(`${idx + 1}. ${url}`);
            });
        } else {
            console.log('✗ No se encontraron URLs directas');
            console.log('  (Puede usar streaming encriptado o cargar dinámicamente)');
        }

        console.log('\n========================================');
        console.log('PRÓXIMOS PASOS:');
        console.log('1. Reproduce el video si no está reproduciendo');
        console.log('2. Observa la consola para peticiones de red');
        console.log('3. Ve a la pestaña "Network" en DevTools');
        console.log('4. Filtra por "media" o ".mp4"');
        console.log('========================================');

        // Guardar en variable global para acceso
        window.analisisVideo = resultados;
        console.log('\n💾 Resultados guardados en: window.analisisVideo');

    }, 2000);

})();
