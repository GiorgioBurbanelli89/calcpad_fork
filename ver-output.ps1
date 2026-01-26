# Ver el Output renderizado como texto plano
Add-Type -AssemblyName System.Web

$html = Get-Content "C:\Users\j-b-j\AppData\Local\Temp\Calcpad\output_html_final_132722_038.html" -Raw

# Extraer body content
$body = [regex]::Match($html, '(?s)<body>(.+?)</body>').Groups[1].Value

# Remover scripts/styles
$body = [regex]::Replace($body, '(?s)<script.*?</script>', '')
$body = [regex]::Replace($body, '(?s)<style.*?</style>', '')

# Remover todos los tags HTML
$text = [regex]::Replace($body, '<[^>]+>', '')

# Decodificar HTML entities
$text = [System.Web.HttpUtility]::HtmlDecode($text)

# Mostrar primeras 50 líneas
$text -split "`n" | Select-Object -First 50 | Write-Host
