#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de iconos para la extensión de Subtítulos en Español
Crea iconos PNG de 16x16, 48x48 y 128x128 píxeles
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    """Crea un icono con degradado y emoji"""

    # Crear imagen con canal alpha
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Crear degradado de fondo (morado)
    for y in range(size):
        # Interpolación de color de #667eea a #764ba2
        ratio = y / size
        r = int(102 + (118 - 102) * ratio)
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)

        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Agregar texto/símbolo en el centro
    # Como no podemos usar emoji directamente, usamos texto
    font_size = int(size * 0.5)

    try:
        # Intentar usar una fuente del sistema
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("segoeui.ttf", font_size)
        except:
            # Fuente por defecto si no encuentra otras
            font = ImageFont.load_default()

    # Dibujar "SUB" o símbolo de video
    text = "🎬"

    # Intentar renderizar emoji, si falla usar texto
    try:
        # Para emojis necesitamos seguiemoji font
        emoji_font = ImageFont.truetype("seguiemj.ttf", font_size)
        bbox = draw.textbbox((0, 0), text, font=emoji_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=emoji_font)
    except:
        # Fallback: usar texto simple
        text = "ES"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]

        # Sombra del texto
        draw.text((x+1, y+1), text, fill=(0, 0, 0, 100), font=font)
        # Texto principal
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    return img

def main():
    """Genera los 3 iconos necesarios"""

    # Configurar salida UTF-8 en Windows
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    # Crear carpeta icons si no existe
    icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    sizes = [16, 48, 128]

    print("Generando iconos para la extension...")
    print()

    for size in sizes:
        filename = os.path.join(icons_dir, f'icon{size}.png')

        print(f"Creando icon{size}.png...", end=' ')

        img = create_icon(size)
        img.save(filename, 'PNG')

        # Verificar que se creó
        if os.path.exists(filename):
            file_size = os.path.getsize(filename)
            print(f"OK ({file_size} bytes)")
        else:
            print("ERROR")

    print()
    print("Iconos generados exitosamente!")
    print(f"Ubicacion: {icons_dir}")
    print()
    print("Archivos creados:")
    for size in sizes:
        filename = f'icon{size}.png'
        filepath = os.path.join(icons_dir, filename)
        if os.path.exists(filepath):
            print(f"  [OK] {filename}")
        else:
            print(f"  [ERROR] {filename} - NO ENCONTRADO")

    print()
    print("Proximos pasos:")
    print("1. Abre Microsoft Edge")
    print("2. Ve a: edge://extensions/")
    print("3. Activa 'Modo de desarrollador'")
    print("4. Clic en 'Cargar extension desempaquetada'")
    print("5. Selecciona la carpeta: Extension-Edge-Subtitulos")
    print()
    print("Listo para usar!")

if __name__ == '__main__':
    main()
