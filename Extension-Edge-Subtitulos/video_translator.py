#!/usr/bin/env python3
"""
Video Translator - Descarga videos y genera audio en español sincronizado
Mezcla el audio original (bajo volumen) con TTS en español

Uso:
    python video_translator.py <URL_VIDEO> [--cookies cookies.txt]
    python video_translator.py --transcript transcript.txt --video video.mp4

Requisitos:
    pip install edge-tts yt-dlp pydub
    FFmpeg instalado en el sistema
"""

import asyncio
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Intentar importar dependencias
try:
    import edge_tts
except ImportError:
    print("Instalando edge-tts...")
    subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"], check=True)
    import edge_tts

try:
    from pydub import AudioSegment
except ImportError:
    print("Instalando pydub...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pydub"], check=True)
    from pydub import AudioSegment


def parse_timestamp(ts: str) -> float:
    """Convierte timestamp MM:SS o HH:MM:SS a segundos"""
    parts = ts.strip().split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0


def parse_transcript(text: str) -> list:
    """
    Parsea transcript en formato:
    [00:02] Texto aquí
    [00:05] Más texto

    O formato:
    00:02
    Texto aquí
    00:05
    Más texto
    """
    entries = []

    # Formato [MM:SS] Texto
    pattern1 = r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.+)'
    matches = re.findall(pattern1, text)

    if matches:
        for ts, txt in matches:
            entries.append({
                'time': parse_timestamp(ts),
                'timestamp': ts,
                'text': txt.strip()
            })
    else:
        # Formato alternativo: timestamp en una línea, texto en la siguiente
        lines = text.strip().split('\n')
        current_time = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Es un timestamp?
            ts_match = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)$', line)
            if ts_match:
                current_time = ts_match.group(1)
            elif current_time and len(line) > 3:
                entries.append({
                    'time': parse_timestamp(current_time),
                    'timestamp': current_time,
                    'text': line
                })
                current_time = None

    # Ordenar por tiempo
    entries.sort(key=lambda x: x['time'])
    return entries


async def translate_text(text: str) -> str:
    """Traduce texto de inglés a español usando Google Translate (gratis)"""
    import urllib.request
    import urllib.parse

    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q={urllib.parse.quote(text)}"

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        translated = ''
        if data and data[0]:
            for part in data[0]:
                if part[0]:
                    translated += part[0]

        return translated if translated else text
    except Exception as e:
        print(f"  Error traduciendo: {e}")
        return text


async def generate_tts_audio(text: str, output_path: str, voice: str = "es-ES-ElviraNeural"):
    """Genera audio TTS usando Edge TTS (calidad Microsoft)"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def create_translated_audio(entries: list, output_path: str, total_duration: float = None):
    """
    Crea un archivo de audio con todas las traducciones sincronizadas
    """
    print(f"\n📝 Procesando {len(entries)} entradas de transcript...")

    # Crear directorio temporal para los archivos de audio
    temp_dir = tempfile.mkdtemp(prefix="video_translator_")
    audio_files = []

    try:
        # Generar audio para cada entrada
        for i, entry in enumerate(entries):
            print(f"  [{entry['timestamp']}] Traduciendo y generando audio ({i+1}/{len(entries)})...")

            # Traducir texto
            translated = await translate_text(entry['text'])
            print(f"    Original: {entry['text'][:50]}...")
            print(f"    Traducido: {translated[:50]}...")

            # Generar audio TTS
            audio_path = os.path.join(temp_dir, f"segment_{i:04d}.mp3")
            await generate_tts_audio(translated, audio_path)

            audio_files.append({
                'path': audio_path,
                'time': entry['time'],
                'text': translated
            })

        # Combinar todos los audios en uno solo con tiempos correctos
        print("\n🔧 Combinando audios...")

        # Determinar duración total
        if total_duration is None:
            # Estimar basado en el último timestamp + 10 segundos
            total_duration = entries[-1]['time'] + 10 if entries else 60

        # Crear audio base silencioso
        total_ms = int(total_duration * 1000)
        combined = AudioSegment.silent(duration=total_ms)

        # Superponer cada segmento de audio en su tiempo correspondiente
        for af in audio_files:
            try:
                segment = AudioSegment.from_mp3(af['path'])
                position_ms = int(af['time'] * 1000)

                # Asegurar que no exceda la duración total
                if position_ms < total_ms:
                    combined = combined.overlay(segment, position=position_ms)
            except Exception as e:
                print(f"  Error procesando segmento: {e}")

        # Exportar audio combinado
        print(f"\n💾 Guardando audio traducido en: {output_path}")
        combined.export(output_path, format="mp3", bitrate="192k")

        return True

    finally:
        # Limpiar archivos temporales
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def download_video(url: str, output_path: str, cookies_file: str = None) -> dict:
    """Descarga video usando yt-dlp"""
    print(f"\n📥 Descargando video desde: {url[:60]}...")

    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-f", "best[ext=mp4]/best",
        "-o", output_path,
        "--no-playlist",
        "--print-json"
    ]

    if cookies_file and os.path.exists(cookies_file):
        cmd.extend(["--cookies", cookies_file])

    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error descargando: {result.stderr}")
        return None

    # Parsear info del video
    try:
        info = json.loads(result.stdout.split('\n')[0])
        return info
    except:
        return {'duration': None}


def get_video_duration(video_path: str) -> float:
    """Obtiene la duración del video usando ffprobe"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return None


def mix_audio_with_video(video_path: str, spanish_audio_path: str, output_path: str,
                         original_volume: float = 0.3, spanish_volume: float = 1.0):
    """
    Mezcla el audio español con el video original

    Args:
        video_path: Ruta al video original
        spanish_audio_path: Ruta al audio en español
        output_path: Ruta de salida
        original_volume: Volumen del audio original (0.0 - 1.0)
        spanish_volume: Volumen del audio español (0.0 - 1.0)
    """
    print(f"\n🎬 Mezclando audio con video...")
    print(f"   Volumen original: {int(original_volume * 100)}%")
    print(f"   Volumen español: {int(spanish_volume * 100)}%")

    # Usar FFmpeg para mezclar
    # -filter_complex: mezcla los dos audios
    # [0:a] es el audio del video original
    # [1:a] es el audio en español

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", spanish_audio_path,
        "-filter_complex",
        f"[0:a]volume={original_volume}[a0];[1:a]volume={spanish_volume}[a1];[a0][a1]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]

    print(f"   Ejecutando FFmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error en FFmpeg: {result.stderr}")
        return False

    print(f"\n✅ Video con audio español guardado en: {output_path}")
    return True


def create_dual_audio_video(video_path: str, spanish_audio_path: str, output_path: str):
    """
    Crea un video con dos pistas de audio:
    - Pista 1: Audio original
    - Pista 2: Audio en español

    El usuario puede cambiar entre pistas en su reproductor.
    """
    print(f"\n🎬 Creando video con doble pista de audio...")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", spanish_audio_path,
        "-map", "0:v",
        "-map", "0:a",
        "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-metadata:s:a:0", "language=eng",
        "-metadata:s:a:0", "title=Original",
        "-metadata:s:a:1", "language=spa",
        "-metadata:s:a:1", "title=Español (TTS)",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False

    print(f"\n✅ Video con doble audio guardado en: {output_path}")
    print("   Pista 1: Audio original (inglés)")
    print("   Pista 2: Audio español (TTS)")
    return True


async def main():
    parser = argparse.ArgumentParser(
        description="Traduce videos agregando audio en español",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Descargar video y agregar audio español
  python video_translator.py "https://example.com/video" --transcript transcript.txt

  # Usar video ya descargado
  python video_translator.py --video video.mp4 --transcript transcript.txt

  # Con cookies para sitios que requieren login
  python video_translator.py "https://example.com/video" --cookies cookies.txt --transcript transcript.txt

  # Crear video con doble pista de audio
  python video_translator.py --video video.mp4 --transcript transcript.txt --dual-audio
        """
    )

    parser.add_argument("url", nargs="?", help="URL del video a descargar")
    parser.add_argument("--video", "-v", help="Ruta a video ya descargado")
    parser.add_argument("--transcript", "-t", required=True, help="Archivo con el transcript")
    parser.add_argument("--cookies", "-c", help="Archivo de cookies para yt-dlp")
    parser.add_argument("--output", "-o", help="Nombre del archivo de salida")
    parser.add_argument("--original-volume", type=float, default=0.3,
                        help="Volumen del audio original (0.0-1.0, default: 0.3)")
    parser.add_argument("--spanish-volume", type=float, default=1.0,
                        help="Volumen del audio español (0.0-1.0, default: 1.0)")
    parser.add_argument("--dual-audio", action="store_true",
                        help="Crear video con dos pistas de audio separadas")
    parser.add_argument("--voice", default="es-ES-ElviraNeural",
                        help="Voz de Edge TTS (default: es-ES-ElviraNeural)")

    args = parser.parse_args()

    # Validar argumentos
    if not args.url and not args.video:
        parser.error("Debes proporcionar una URL o un archivo de video (--video)")

    if not os.path.exists(args.transcript):
        parser.error(f"No se encontró el archivo de transcript: {args.transcript}")

    # Leer transcript
    print(f"\n📖 Leyendo transcript: {args.transcript}")
    with open(args.transcript, 'r', encoding='utf-8') as f:
        transcript_text = f.read()

    entries = parse_transcript(transcript_text)
    if not entries:
        print("❌ No se encontraron entradas en el transcript")
        sys.exit(1)

    print(f"   Encontradas {len(entries)} entradas")

    # Obtener o descargar video
    video_path = args.video
    video_duration = None

    if not video_path:
        # Descargar video
        video_path = "downloaded_video.mp4"
        info = download_video(args.url, video_path, args.cookies)
        if info:
            video_duration = info.get('duration')

    if not os.path.exists(video_path):
        print(f"❌ No se encontró el video: {video_path}")
        sys.exit(1)

    # Obtener duración del video
    if video_duration is None:
        video_duration = get_video_duration(video_path)

    print(f"   Duración del video: {video_duration:.1f} segundos" if video_duration else "   Duración desconocida")

    # Generar audio en español
    spanish_audio_path = "spanish_audio.mp3"
    await create_translated_audio(entries, spanish_audio_path, video_duration)

    # Determinar nombre de salida
    if args.output:
        output_path = args.output
    else:
        base_name = Path(video_path).stem
        output_path = f"{base_name}_español.mp4"

    # Crear video final
    if args.dual_audio:
        success = create_dual_audio_video(video_path, spanish_audio_path, output_path)
    else:
        success = mix_audio_with_video(
            video_path,
            spanish_audio_path,
            output_path,
            args.original_volume,
            args.spanish_volume
        )

    # Limpiar
    if os.path.exists(spanish_audio_path):
        os.remove(spanish_audio_path)

    if success:
        print(f"\n🎉 ¡Proceso completado!")
        print(f"   Video con audio español: {output_path}")
    else:
        print("\n❌ Error al crear el video")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
