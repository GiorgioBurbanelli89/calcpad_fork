// Script para exportar cookies en formato Netscape (compatible con yt-dlp)
// Ejecutar en la consola del navegador (F12 -> Console)

(function() {
    const cookies = document.cookie.split(';').map(c => c.trim());
    const domain = window.location.hostname;
    const now = Math.floor(Date.now() / 1000) + 86400 * 365; // 1 año de expiración

    let output = '# Netscape HTTP Cookie File\n';
    output += '# https://curl.haxx.se/rfc/cookie_spec.html\n';
    output += '# This is a generated file! Do not edit.\n\n';

    cookies.forEach(cookie => {
        const [name, ...valueParts] = cookie.split('=');
        const value = valueParts.join('=');

        if (name && value) {
            // Format: domain, flag, path, secure, expiry, name, value
            output += `.${domain}\tTRUE\t/\tTRUE\t${now}\t${name.trim()}\t${value}\n`;
        }
    });

    // Crear y descargar archivo
    const blob = new Blob([output], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cookies.txt';
    a.click();
    URL.revokeObjectURL(url);

    console.log('Cookies exportadas! Archivo descargado como cookies.txt');
    console.log('Usa: python -m yt_dlp --cookies cookies.txt "URL"');
})();
