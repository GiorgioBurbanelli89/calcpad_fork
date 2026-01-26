"""
Script para ejecutar Octave y capturar la ventana gráfica
"""
import subprocess
import time
import pyautogui
import win32gui
import win32con
import sys

def find_octave_window():
    """Encontrar ventana de Octave Figure"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if 'Figure' in title:
                windows.append((hwnd, title))
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

def capture_octave_graph(octave_script, output_image):
    """
    Ejecutar script Octave y capturar la ventana
    """
    # Ejecutar Octave en background
    process = subprocess.Popen(
        ['octave-cli', '--eval', octave_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Esperar a que aparezca la ventana
    max_wait = 10
    window_found = False

    for i in range(max_wait):
        time.sleep(0.5)
        windows = find_octave_window()
        if windows:
            window_found = True
            hwnd, title = windows[0]
            print(f"Ventana encontrada: {title}")

            # Traer ventana al frente
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)

            # Obtener posición de la ventana
            rect = win32gui.GetWindowRect(hwnd)
            x, y, x2, y2 = rect

            # Capturar screenshot
            screenshot = pyautogui.screenshot(region=(x, y, x2-x, y2-y))
            screenshot.save(output_image)
            print(f"Captura guardada: {output_image}")

            # Cerrar ventana
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            break

    # Terminar proceso de Octave
    if process.poll() is None:
        process.terminate()

    return window_found

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python octave-screenshot-helper.py <script> <output_image>")
        sys.exit(1)

    script = sys.argv[1]
    output = sys.argv[2]

    success = capture_octave_graph(script, output)

    if success:
        print(f"SUCCESS: {output}")
    else:
        print("ERROR: No se encontró ventana de Octave")
        sys.exit(1)
