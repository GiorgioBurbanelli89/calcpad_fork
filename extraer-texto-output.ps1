# Extrae el texto plano visible del HTML del Output (como lo verías en pantalla)

param(
    [string]$HtmlFile
)

if (!$HtmlFile) {
    # Buscar el HTML más reciente
    $HtmlFile = Get-ChildItem "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\output_html_final_*.html" |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1 -ExpandProperty FullName
}

if (!$HtmlFile -or !(Test-Path $HtmlFile)) {
    Write-Host "[ERROR] No se encontró archivo HTML" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== TEXTO PLANO DEL OUTPUT (primeras 100 líneas) ===" -ForegroundColor Cyan
Write-Host "Archivo: $HtmlFile`n" -ForegroundColor Gray

# Leer HTML y extraer el body
$html = Get-Content $HtmlFile -Raw -Encoding UTF8

# Encontrar el body
if ($html -match '(?s)<body>(.+)</body>') {
    $bodyHtml = $matches[1]

    # Remover scripts y styles
    $bodyHtml = $bodyHtml -replace '(?s)<script[^>]*>.*?</script>', ''
    $bodyHtml = $bodyHtml -replace '(?s)<style[^>]*>.*?</style>', ''

    # Convertir tags HTML a texto plano simple
    $text = $bodyHtml

    # Remover tags pero preservar contenido
    $text = $text -replace '<br\s*/?>', "`n"
    $text = $text -replace '<hr\s*/?>', "`n" + ("-" * 80) + "`n"
    $text = $text -replace '<h[1-6][^>]*>', "`n### "
    $text = $text -replace '</h[1-6]>', " ###`n"
    $text = $text -replace '<p[^>]*>', ""
    $text = $text -replace '</p>', "`n"
    $text = $text -replace '<div[^>]*>', ""
    $text = $text -replace '</div>', "`n"
    $text = $text -replace '<span[^>]*>', ""
    $text = $text -replace '</span>', ""
    $text = $text -replace '<a[^>]*>', ""
    $text = $text -replace '</a>', ""
    $text = $text -replace '<var>', ""
    $text = $text -replace '</var>', ""
    $text = $text -replace '<sub>', "_"
    $text = $text -replace '</sub>', ""
    $text = $text -replace '<sup>', "^"
    $text = $text -replace '</sup>', ""
    $text = $text -replace '<b>', "**"
    $text = $text -replace '</b>', "**"
    $text = $text -replace '<i>', "*"
    $text = $text -replace '</i>', "*"
    $text = $text -replace '<table[^>]*>', "`n[TABLE]`n"
    $text = $text -replace '</table>', "`n[/TABLE]`n"
    $text = $text -replace '<tr[^>]*>', ""
    $text = $text -replace '</tr>', "`n"
    $text = $text -replace '<td[^>]*>', " | "
    $text = $text -replace '</td>', ""
    $text = $text -replace '<img[^>]*>', "[IMAGE]"

    # Remover cualquier otro tag que quede
    $text = $text -replace '<[^>]+>', ''

    # Decodificar entidades HTML
    $text = [System.Web.HttpUtility]::HtmlDecode($text)

    # Limpiar líneas vacías múltiples
    $text = $text -replace '(?m)^\s*$\n', "`n"
    $text = $text -replace '\n{3,}', "`n`n"

    # Mostrar primeras 100 líneas
    $lines = $text -split "`n"
    $lines | Select-Object -First 100 | ForEach-Object {
        if ($_ -match 'Error') {
            Write-Host $_ -ForegroundColor Red
        }
        elseif ($_ -match '^###') {
            Write-Host $_ -ForegroundColor Cyan
        }
        else {
            Write-Host $_
        }
    }

    Write-Host "`n`n=== TOTAL: $($lines.Count) líneas ===" -ForegroundColor Gray

} else {
    Write-Host "[ERROR] No se pudo encontrar el body en el HTML" -ForegroundColor Red
}
