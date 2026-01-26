// popup_v2.js - UI para detector y descargador de videos

let currentTab = null;
let detectedVideos = [];

// ==================== INICIALIZACIÓN ====================

async function init() {
    // Obtener pestaña actual
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    currentTab = tab;

    // Actualizar status
    document.getElementById('status-text').textContent = `Activo en: ${new URL(tab.url).hostname}`;

    // Cargar videos detectados
    await loadVideos();

    // Cargar configuración
    await loadConfig();

    // Auto-refrescar cada 2 segundos
    setInterval(loadVideos, 2000);
}

// ==================== CARGAR VIDEOS DETECTADOS ====================

async function loadVideos() {
    try {
        const response = await chrome.runtime.sendMessage({
            action: 'getVideos',
            tabId: currentTab.id
        });

        detectedVideos = response.videos || [];

        renderVideoList();

    } catch (e) {
        console.error('Error cargando videos:', e);
    }
}

function renderVideoList() {
    const videoList = document.getElementById('video-list');
    const videoCount = document.getElementById('video-count');

    videoCount.textContent = detectedVideos.length;

    if (detectedVideos.length === 0) {
        videoList.innerHTML = `
            <div class="empty">
                No se han detectado videos aún.<br>
                <strong>Reproduce el video</strong> para detectarlo.<br>
                <small style="opacity:0.7">La detección ocurre cuando el video comienza a cargar.</small>
                <button class="button primary" style="margin-top:10px;width:100%" onclick="forceDetection()">
                    🔄 Forzar Detección
                </button>
            </div>
        `;
        return;
    }

    videoList.innerHTML = '';

    detectedVideos.forEach((video, index) => {
        const item = document.createElement('div');
        item.className = 'video-item';

        // Extraer nombre del archivo
        let filename = 'video';
        try {
            const url = new URL(video.url);
            filename = url.pathname.split('/').pop() || 'video';
            filename = filename.split('?')[0]; // Quitar query params
            if (filename.length > 40) filename = filename.substring(0, 37) + '...';
        } catch (e) {
            filename = video.url.substring(0, 40) + '...';
        }

        // Formatear tamaño
        const sizeText = video.size ? formatBytes(video.size) : '';

        // Determinar tipo
        let typeText = video.streamType || 'Video';

        // Calidad
        const qualityText = video.quality && video.quality !== 'unknown' ? video.quality : '';
        const qualityBadge = qualityText ? `<span class="badge quality-badge">${qualityText}</span>` : '';

        // Color del badge según calidad
        let qualityClass = '';
        if (qualityText.includes('1080') || qualityText.includes('4k') || qualityText.includes('1440')) {
            qualityClass = 'hd';
        }

        // Mostrar botón yt-dlp si es HLS o streaming
        const isStream = typeText === 'HLS' || typeText === 'DASH' || video.type === 'streaming' || video.type === 'hd-stream';
        const ytdlpBtn = isStream ?
            `<button class="button secondary" onclick="copyYtDlpCommand(${index})" title="Copiar comando yt-dlp">
                🎬 yt-dlp
            </button>` : '';

        item.innerHTML = `
            <a href="${video.url}" target="_blank" class="url" title="${video.url}">
                ${filename}
            </a>
            <div class="meta">
                ${qualityBadge}
                <span class="badge">${typeText}</span>
                ${sizeText ? `<span class="badge">${sizeText}</span>` : ''}
            </div>
            <div class="actions">
                <button class="button download ${qualityClass}" onclick="downloadVideo(${index})">
                    ⬇️ Descargar ${qualityText}
                </button>
                <button class="button secondary" onclick="copyUrl(${index})">
                    📋 URL
                </button>
                ${ytdlpBtn}
            </div>
        `;

        videoList.appendChild(item);
    });

    // Agregar botón para descargar mejor calidad si hay múltiples videos
    if (detectedVideos.length > 1) {
        const bestBtn = document.createElement('button');
        bestBtn.className = 'button primary';
        bestBtn.style.marginTop = '10px';
        bestBtn.style.width = '100%';
        bestBtn.innerHTML = '⭐ Descargar Mejor Calidad';
        bestBtn.onclick = downloadBestQuality;
        videoList.appendChild(bestBtn);
    }
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    if (!bytes) return 'N/A';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ==================== DESCARGAR VIDEO ====================

window.downloadVideo = async function(index) {
    const video = detectedVideos[index];

    if (!video) {
        alert('Video no encontrado');
        return;
    }

    try {
        const qualitySelect = document.getElementById('quality-select');
        const quality = qualitySelect?.value || 'highest';

        const response = await chrome.runtime.sendMessage({
            action: 'downloadVideo',
            video: video,
            quality: quality
        });

        if (response.success) {
            if (response.type === 'hls' || response.type === 'dash') {
                // Es un stream, mostrar información
                showStreamInfo(response);
            } else {
                alert('Descarga iniciada!\nRevisa tus descargas.');
            }
        } else {
            alert('Error al descargar:\n' + response.error);
        }

    } catch (e) {
        console.error('Error descargando:', e);
        alert('Error al iniciar descarga');
    }
}

async function showStreamInfo(streamData) {
    // Si hay comando yt-dlp, copiarlo automáticamente al portapapeles
    if (streamData.ytdlpCommand) {
        try {
            await navigator.clipboard.writeText(streamData.ytdlpCommand);
        } catch (e) {
            // Fallback para copiar
            const textarea = document.createElement('textarea');
            textarea.value = streamData.ytdlpCommand;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    let message = '';

    if (streamData.type === 'hls') {
        const segCount = streamData.segments?.length || 0;

        if (segCount === 0 && streamData.ytdlpCommand) {
            // Mensaje simplificado - el comando ya está copiado
            message = `✅ Stream HLS detectado!\n\n`;
            message += `📋 Comando COPIADO al portapapeles:\n\n`;
            message += `${streamData.ytdlpCommand}\n\n`;
            message += `👉 Abre PowerShell y pega con Ctrl+V`;
        } else if (segCount > 0) {
            message = `✅ Descarga en progreso...\n`;
            message += `Segmentos: ${segCount}`;
        } else {
            message = streamData.message || `Stream HLS detectado`;
        }
    } else if (streamData.type === 'dash') {
        message += `Manifest URL:\n${streamData.manifestUrl || streamData.url}\n\n`;
        message += '📥 Para descargar en HD, usa:\n';
        message += `yt-dlp --cookies-from-browser edge "${currentTab?.url || 'URL_DE_LA_PAGINA'}"`;
    }

    if (streamData.message) {
        message = streamData.message;
    }

    alert(message);
}

// ==================== DESCARGAR MEJOR CALIDAD ====================

window.downloadBestQuality = async function() {
    try {
        const qualitySelect = document.getElementById('quality-select');
        const quality = qualitySelect?.value || 'highest';

        const response = await chrome.runtime.sendMessage({
            action: 'downloadBestQuality',
            tabId: currentTab.id,
            quality: quality
        });

        if (response.success) {
            if (response.type === 'hls' || response.type === 'dash') {
                showStreamInfo(response);
            } else {
                alert('Descarga HD iniciada!\nRevisa tus descargas.');
            }
        } else {
            alert('Error: ' + (response.error || 'No se encontraron videos'));
        }
    } catch (e) {
        console.error('Error:', e);
        alert('Error al iniciar descarga');
    }
}

// ==================== COPIAR URL ====================

window.copyUrl = async function(index) {
    const video = detectedVideos[index];

    if (!video) return;

    try {
        await navigator.clipboard.writeText(video.url);
        alert('URL copiada al portapapeles');
    } catch (e) {
        // Fallback
        const textarea = document.createElement('textarea');
        textarea.value = video.url;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('URL copiada al portapapeles');
    }
}

// Copiar comando yt-dlp listo para usar
window.copyYtDlpCommand = async function(index) {
    const video = detectedVideos[index];
    const pageUrl = video?.pageUrl || currentTab?.url || '';

    // Preguntar qué método usar
    const method = confirm(
        '¿Cómo quieres descargar?\n\n' +
        'OK = Exportar cookies (recomendado)\n' +
        'Cancelar = Copiar comando (requiere cerrar Edge)'
    );

    if (method) {
        // Exportar cookies
        await exportCookiesAndDownload(pageUrl);
    } else {
        // Copiar comando
        const command = `python -m yt_dlp --cookies-from-browser edge "${pageUrl}"`;

        try {
            await navigator.clipboard.writeText(command);
            alert(
                'Comando copiado!\n\n' +
                'IMPORTANTE: Cierra Edge completamente antes de ejecutar.\n\n' +
                'Pega en PowerShell:\n' + command
            );
        } catch (e) {
            const textarea = document.createElement('textarea');
            textarea.value = command;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            alert('Comando copiado!\n\nCierra Edge y pega en PowerShell:\n' + command);
        }
    }
}

// Exportar cookies y generar comando (usando API de cookies de Chrome)
window.exportCookiesAndDownload = async function(pageUrl) {
    try {
        // Usar la API de background para obtener TODAS las cookies (no solo las del documento)
        const result = await chrome.runtime.sendMessage({
            action: 'exportAllCookies',
            url: pageUrl
        });

        if (result && result.success && result.cookies) {
            // Crear archivo de cookies
            const blob = new Blob([result.cookies], { type: 'text/plain' });
            const blobUrl = URL.createObjectURL(blob);

            // Descargar archivo
            await chrome.downloads.download({
                url: blobUrl,
                filename: 'video_cookies.txt',
                saveAs: false
            });

            // Copiar comando (compatible con PowerShell antiguo)
            const command = `cd ~\\Downloads; python -m yt_dlp --cookies video_cookies.txt "${pageUrl}"`;

            try {
                await navigator.clipboard.writeText(command);
            } catch (e) {}

            alert(
                `✅ Cookies exportadas (${result.count} cookies de ${result.domain})\n\n` +
                `Archivo: video_cookies.txt (en tu carpeta de Descargas)\n\n` +
                `Comando copiado al portapapeles:\n${command}\n\n` +
                `1. Abre PowerShell\n` +
                `2. Pega el comando (Ctrl+V)\n` +
                `3. Presiona Enter`
            );

            setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
        } else {
            throw new Error(result?.error || 'No se pudieron obtener las cookies');
        }

    } catch (error) {
        console.error('Error exportando cookies:', error);

        // Fallback: intentar con document.cookie
        try {
            const [fallbackResult] = await chrome.scripting.executeScript({
                target: { tabId: currentTab.id },
                func: () => {
                    const cookies = document.cookie.split(';').map(c => c.trim());
                    const domain = window.location.hostname;
                    const now = Math.floor(Date.now() / 1000) + 86400 * 365;

                    let output = '# Netscape HTTP Cookie File\n';
                    output += '# Generated by Video Detector HD (fallback)\n\n';

                    cookies.forEach(cookie => {
                        const [name, ...valueParts] = cookie.split('=');
                        const value = valueParts.join('=');
                        if (name && value) {
                            output += `.${domain}\tTRUE\t/\tTRUE\t${now}\t${name.trim()}\t${value}\n`;
                        }
                    });

                    return { cookies: output, count: cookies.length };
                }
            });

            if (fallbackResult?.result?.cookies) {
                const blob = new Blob([fallbackResult.result.cookies], { type: 'text/plain' });
                const blobUrl = URL.createObjectURL(blob);

                await chrome.downloads.download({
                    url: blobUrl,
                    filename: 'video_cookies.txt',
                    saveAs: false
                });

                const command = `cd ~\\Downloads; python -m yt_dlp --cookies video_cookies.txt "${pageUrl}"`;
                await navigator.clipboard.writeText(command).catch(() => {});

                alert(
                    `⚠️ Cookies parciales exportadas (${fallbackResult.result.count})\n\n` +
                    `Archivo: video_cookies.txt\n\n` +
                    `Comando:\n${command}\n\n` +
                    `Nota: Si falla, cierra Edge y usa:\npython -m yt_dlp --cookies-from-browser edge "${pageUrl}"`
                );

                setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
            } else {
                throw new Error('Fallback también falló');
            }

        } catch (fallbackError) {
            alert(
                `❌ Error al exportar cookies: ${error.message}\n\n` +
                `Alternativa: Cierra Edge completamente y ejecuta:\n\n` +
                `python -m yt_dlp --cookies-from-browser edge "${pageUrl}"`
            );
        }
    }
}

// ==================== LIMPIAR VIDEOS ====================

window.clearVideos = async function() {
    if (!confirm('¿Limpiar lista de videos detectados?')) return;

    try {
        await chrome.runtime.sendMessage({
            action: 'clearVideos',
            tabId: currentTab.id
        });

        detectedVideos = [];
        renderVideoList();

    } catch (e) {
        console.error('Error limpiando videos:', e);
    }
}

// ==================== EXTRAER TRANSCRIPT ====================

window.extractTranscript = async function() {
    const resultDiv = document.getElementById('transcript-result');
    const textPre = document.getElementById('transcript-text');

    try {
        // Mostrar indicador de carga
        resultDiv.style.display = 'block';
        textPre.textContent = '⏳ Extrayendo transcript...';

        // Enviar mensaje al content script para extraer transcript
        const response = await chrome.tabs.sendMessage(currentTab.id, {
            action: 'extractTranscript'
        });

        if (response && response.success) {
            // Mostrar el texto extraído
            textPre.textContent = response.text;

            // Copiar al portapapeles automáticamente
            try {
                await navigator.clipboard.writeText(response.text);
            } catch (e) {
                // Fallback
                const textarea = document.createElement('textarea');
                textarea.value = response.text;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
            }

            alert(
                `✅ Transcript extraído y COPIADO al portapapeles!\n\n` +
                `📊 ${response.lines} líneas, ${response.charCount} caracteres\n\n` +
                `Puedes pegarlo en Google Translate o cualquier traductor.`
            );

        } else {
            textPre.textContent = '❌ ' + (response?.error || 'No se pudo extraer el transcript');
            alert(
                `❌ ${response?.error || 'No se encontró transcript'}\n\n` +
                `Asegúrate de que:\n` +
                `1. El panel de transcript esté visible en la página\n` +
                `2. El video tenga transcript disponible`
            );
        }

    } catch (e) {
        console.error('Error extrayendo transcript:', e);
        textPre.textContent = '❌ Error: ' + e.message;
        resultDiv.style.display = 'block';
        alert(
            `❌ Error al extraer transcript\n\n` +
            `Asegúrate de que el panel de transcript esté visible en la página.`
        );
    }
}

// ==================== TRADUCIR TRANSCRIPT ====================

window.translateTranscript = async function() {
    const statusDiv = document.getElementById('translation-status');

    try {
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = '⏳ Traduciendo transcript al español...';

        // Enviar mensaje al content script para traducir
        const response = await chrome.tabs.sendMessage(currentTab.id, {
            action: 'translateTranscript'
        });

        if (response && response.success) {
            statusDiv.innerHTML = `✅ ¡Traducción completada!<br>📊 ${response.translated} líneas traducidas<br><br>El texto traducido aparece en <span style="color: #90EE90;">verde</span> en la página.`;
            statusDiv.style.background = 'rgba(76, 175, 80, 0.3)';
        } else {
            statusDiv.innerHTML = `❌ ${response?.error || 'No se pudo traducir'}<br><br>Asegúrate de que el panel de transcript esté visible.`;
            statusDiv.style.background = 'rgba(244, 67, 54, 0.3)';
        }

    } catch (e) {
        console.error('Error traduciendo:', e);
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = `❌ Error: ${e.message}<br><br>Asegúrate de que el panel de transcript esté visible en la página.`;
        statusDiv.style.background = 'rgba(244, 67, 54, 0.3)';
    }
}

// ==================== TTS SINCRONIZADO ====================

window.startSyncTTS = async function() {
    const statusDiv = document.getElementById('tts-status');
    const stopBtn = document.getElementById('stop-tts-btn');

    try {
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = '⏳ Iniciando TTS sincronizado...<br>Traduciendo transcript...';
        statusDiv.style.background = 'rgba(255, 152, 0, 0.3)';

        const response = await chrome.tabs.sendMessage(currentTab.id, {
            action: 'startSyncTTS',
            options: {
                ttsVolume: 0.8,
                videoVolume: 0.3,
                reduceOriginalVolume: true
            }
        });

        if (response && response.success) {
            statusDiv.innerHTML = `✅ ¡TTS Activo!<br>📊 ${response.entries} líneas cargadas<br><br>Controles de volumen en la página.`;
            statusDiv.style.background = 'rgba(76, 175, 80, 0.3)';
            stopBtn.style.display = 'block';
        } else {
            statusDiv.innerHTML = `❌ ${response?.error || 'No se pudo iniciar TTS'}<br><br>Asegúrate de que:<br>1. El panel de transcript esté abierto<br>2. El video esté visible`;
            statusDiv.style.background = 'rgba(244, 67, 54, 0.3)';
        }

    } catch (e) {
        console.error('Error iniciando TTS:', e);
        statusDiv.style.display = 'block';
        statusDiv.innerHTML = `❌ Error: ${e.message}<br><br>Asegúrate de que el transcript esté visible.`;
        statusDiv.style.background = 'rgba(244, 67, 54, 0.3)';
    }
}

window.stopSyncTTS = async function() {
    const statusDiv = document.getElementById('tts-status');
    const stopBtn = document.getElementById('stop-tts-btn');

    try {
        await chrome.tabs.sendMessage(currentTab.id, {
            action: 'stopSyncTTS'
        });

        statusDiv.innerHTML = '⏹️ TTS detenido';
        statusDiv.style.background = 'rgba(158, 158, 158, 0.3)';
        stopBtn.style.display = 'none';

    } catch (e) {
        console.error('Error deteniendo TTS:', e);
    }
}

// ==================== EXPORTAR PARA PYTHON ====================

window.exportForPython = async function() {
    const resultDiv = document.getElementById('python-export-result');
    const commandPre = document.getElementById('python-command');

    try {
        resultDiv.style.display = 'block';
        commandPre.textContent = '⏳ Extrayendo transcript...';

        // Extraer transcript
        const response = await chrome.tabs.sendMessage(currentTab.id, {
            action: 'extractTranscript'
        });

        if (!response || !response.success) {
            commandPre.textContent = '❌ ' + (response?.error || 'No se pudo extraer el transcript');
            return;
        }

        // Guardar transcript a archivo
        const transcriptText = response.text;
        const blob = new Blob([transcriptText], { type: 'text/plain' });

        // Descargar archivo de transcript
        const transcriptUrl = URL.createObjectURL(blob);
        await chrome.downloads.download({
            url: transcriptUrl,
            filename: 'transcript.txt',
            saveAs: false
        });

        // Obtener URL de la página actual
        const pageUrl = currentTab.url;

        // Exportar cookies
        let cookiesExported = false;
        try {
            const cookiesResponse = await chrome.runtime.sendMessage({
                action: 'exportAllCookies',
                url: pageUrl
            });

            if (cookiesResponse && cookiesResponse.success) {
                const cookiesBlob = new Blob([cookiesResponse.cookies], { type: 'text/plain' });
                const cookiesUrl = URL.createObjectURL(cookiesBlob);
                await chrome.downloads.download({
                    url: cookiesUrl,
                    filename: 'cookies.txt',
                    saveAs: false
                });
                cookiesExported = true;
            }
        } catch (e) {
            console.log('No se pudieron exportar cookies:', e);
        }

        // Generar comando Python
        const cookiesArg = cookiesExported ? ' --cookies cookies.txt' : '';
        const command = `# 1. Instalar dependencias (solo la primera vez):
pip install edge-tts yt-dlp pydub

# 2. Asegúrate de tener FFmpeg instalado

# 3. Ejecutar el script:
python video_translator.py "${pageUrl}"${cookiesArg} --transcript transcript.txt

# Opciones adicionales:
# --output video_español.mp4     # Nombre del archivo de salida
# --original-volume 0.3          # Volumen audio original (0.0-1.0)
# --spanish-volume 1.0           # Volumen audio español (0.0-1.0)
# --dual-audio                   # Crear video con 2 pistas de audio
# --voice es-MX-DaliaNeural      # Voz mexicana en lugar de española`;

        commandPre.textContent = command;

        // Copiar al portapapeles
        try {
            await navigator.clipboard.writeText(command);
        } catch (e) {
            // Fallback
        }

        alert(
            `✅ ¡Exportación completada!\n\n` +
            `Archivos descargados:\n` +
            `• transcript.txt\n` +
            (cookiesExported ? `• cookies.txt\n\n` : '\n') +
            `El comando Python ha sido copiado al portapapeles.\n\n` +
            `Copia el script video_translator.py a la carpeta de descargas y ejecuta el comando.`
        );

    } catch (e) {
        console.error('Error exportando:', e);
        commandPre.textContent = '❌ Error: ' + e.message;
    }
}

// ==================== GENERAR SUBTÍTULOS ====================

window.generateSubtitles = async function() {
    try {
        const response = await chrome.tabs.sendMessage(currentTab.id, {
            action: 'generateSubtitles'
        });

        if (response && response.success) {
            alert('Subtítulos generados correctamente');
        } else {
            alert('Error al generar subtítulos');
        }

    } catch (e) {
        console.error('Error:', e);
        alert('Error al generar subtítulos. Asegúrate de que haya videos en la página.');
    }
}

window.generateAudio = async function() {
    const voiceSelect = document.getElementById('voice-select');
    const speedSelect = document.getElementById('speed-select');

    try {
        const response = await chrome.tabs.sendMessage(currentTab.id, {
            action: 'generateAudio',
            voice: voiceSelect.value,
            speed: parseFloat(speedSelect.value)
        });

        if (response && response.success) {
            alert('Audio TTS generado correctamente');
        } else {
            alert('Error al generar audio. Primero genera los subtítulos.');
        }

    } catch (e) {
        console.error('Error:', e);
        alert('Error al generar audio');
    }
}

// ==================== CONFIGURACIÓN ====================

async function loadConfig() {
    const config = await chrome.storage.local.get([
        'autoSubtitle',
        'autoDetectVideos',
        'voice',
        'speed',
        'preferredQuality'
    ]);

    if (config.autoSubtitle !== undefined) {
        document.getElementById('auto-subtitle').checked = config.autoSubtitle;
    }

    if (config.autoDetectVideos !== undefined) {
        document.getElementById('auto-detect').checked = config.autoDetectVideos;
    }

    if (config.voice) {
        document.getElementById('voice-select').value = config.voice;
    }

    if (config.speed) {
        document.getElementById('speed-select').value = config.speed;
    }

    if (config.preferredQuality) {
        document.getElementById('quality-select').value = config.preferredQuality;
    }
}

window.saveConfig = async function() {
    await chrome.storage.local.set({
        autoSubtitle: document.getElementById('auto-subtitle').checked,
        autoDetectVideos: document.getElementById('auto-detect').checked,
        voice: document.getElementById('voice-select').value,
        speed: document.getElementById('speed-select').value,
        preferredQuality: document.getElementById('quality-select').value
    });
}

// Guardar configuración cuando cambie
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('auto-subtitle')?.addEventListener('change', window.saveConfig);
    document.getElementById('auto-detect')?.addEventListener('change', window.saveConfig);
    document.getElementById('voice-select')?.addEventListener('change', window.saveConfig);
    document.getElementById('speed-select')?.addEventListener('change', window.saveConfig);
    document.getElementById('quality-select')?.addEventListener('change', window.saveConfig);
});

// ==================== CAMBIAR TABS ====================

window.switchTab = function(tabName) {
    // Desactivar todos los tabs
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Activar tab seleccionado
    event.target.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

// ==================== FORZAR DETECCIÓN ====================

window.forceDetection = async function() {
    try {
        // Enviar mensaje al content script para re-escanear
        await chrome.tabs.sendMessage(currentTab.id, {
            action: 'forceDetection'
        }).catch(() => {});

        // También pedir al background que re-escanee
        await chrome.runtime.sendMessage({
            action: 'forceDetection',
            tabId: currentTab.id
        }).catch(() => {});

        // Esperar un poco y recargar la lista
        setTimeout(loadVideos, 1000);

        // Mostrar feedback
        const videoList = document.getElementById('video-list');
        videoList.innerHTML = `
            <div class="empty">
                🔍 Buscando videos...<br>
                <small>Esto puede tomar unos segundos.</small>
            </div>
        `;

    } catch (e) {
        console.error('Error en detección forzada:', e);
    }
}

// ==================== INICIAR ====================

init();
