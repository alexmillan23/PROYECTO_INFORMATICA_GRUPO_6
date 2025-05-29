import pygame
import numpy as np
import os

# Variables globales para el estado
playing = False
sound = None
current_music_file = None

def crear_sonido():
    """Crea un sonido relajante con ritmo directamente en memoria."""
    global sound
    try:
        # Asegurar que pygame esté iniciado
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        # Generar un sonido de música ambiental relajante
        sample_rate = 44100
        duration = 5.0  # Segundos

        # Crear matriz de tiempo
        t = np.linspace(0, duration, int(sample_rate * duration), False)

        # Generar un tono base relajante (432Hz)
        note1 = np.sin(2 * np.pi * 432 * t)

        # Añadir armónicos suaves
        note2 = 0.3 * np.sin(2 * np.pi * 432 * 1.5 * t)
        note3 = 0.2 * np.sin(2 * np.pi * 432 * 2 * t)

        # Combinar notas
        tone = note1 + note2 + note3

        # Aplicar un efecto de pulso lento (respiración)
        pulse = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
        tone = tone * pulse

        # Normalizar entre -1 y 1
        tone = tone / np.max(np.abs(tone))

        # Convertir a formato de audio de 16 bits
        tone = (tone * 32767).astype(np.int16)

        # Convertir a estéreo duplicando el canal
        stereo_tone = np.column_stack((tone, tone))

        # Crear el objeto de sonido de pygame
        sound = pygame.mixer.Sound(stereo_tone)

        print("Sonido relajante generado correctamente.")
        return True
    except Exception as e:
        print(f"Error al crear el sonido: {str(e)}")
        return False

def inicializar_reproductor():
    """Inicializa el reproductor de música."""
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    global playing, sound, current_music_file
    playing = False
    sound = None
    current_music_file = None
    crear_sonido()

def cargar_musica(music_file=None):
    """Carga un archivo de música o usa el sonido generado en memoria."""
    global sound, current_music_file
    try:
        # Si se proporciona un archivo de música, cargarlo
        if music_file:
            # Verificar si el archivo existe
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                current_music_file = music_file
                print(f"Archivo de música cargado: {music_file}")
                return True
            else:
                print(f"Archivo no encontrado: {music_file}")
                return False
        # Si no hay archivo, usar el sonido generado
        elif sound:
            return True
        else:
            return crear_sonido()
    except Exception as e:
        print(f"Error al cargar la música: {str(e)}")
        return False
    
def reproducir():
    """Reproduce la música cargada."""
    global playing, sound, current_music_file
    try:
        if not playing:
            if current_music_file:
                pygame.mixer.music.play(-1)  # -1 para reproducir en bucle
                playing = True
                print(f"Reproduciendo archivo: {current_music_file}")
                return True
            elif sound:
                sound.play(-1)  # -1 para reproducir en bucle
                playing = True
                print("Reproduciendo música relajante generada...")
                return True
        return False
    except Exception as e:
        print(f"Error al reproducir la música: {str(e)}")
        return False
        
def detener():
    """Detiene la reproducción de música."""
    global playing, sound, current_music_file
    try:
        if playing:
            if current_music_file:
                pygame.mixer.music.stop()
            elif sound:
                sound.stop()
            playing = False
            print("Música detenida.")
            return True
        return True
    except Exception as e:
        print(f"Error al detener la música: {str(e)}")
        return False
        
def alternar():
    """Alterna entre reproducir y detener la música."""
    global playing
    if playing:
        return detener()
    else:
        return reproducir()

# Aliases para mantener compatibilidad con el código que use la clase MusicPlayer
# Estas funciones mantienen la misma firma que los métodos de la clase
def create_sound():
    """Alias de crear_sonido para mantener compatibilidad."""
    return crear_sonido()

def load_music(music_file=None):
    """Alias de cargar_musica para mantener compatibilidad."""
    return cargar_musica(music_file)

def play():
    """Alias de reproducir para mantener compatibilidad."""
    return reproducir()

def stop():
    """Alias de detener para mantener compatibilidad."""
    return detener()

def toggle():
    """Alias de alternar para mantener compatibilidad."""
    return alternar()

# Clase mínima para mantener compatibilidad con código existente
class MusicPlayer:
    """Clase para mantener compatibilidad con código existente.

    Esta clase simplemente proporciona una interfaz compatible
    con el código que pudiera estar usando la clase anterior,
    pero internamente todas las funciones están a nivel de módulo.
    """
    def __init__(self):
        """Inicializa el reproductor de música."""
        inicializar_reproductor()

    def create_sound(self):
        return create_sound()

    def load_music(self, music_file=None):
        return load_music(music_file)

    def play(self):
        return play()

    def stop(self):
        return stop()

    def toggle(self):
        return toggle()

# Función auxiliar para reproducir una canción específica
def reproducir_cancion_de_carpeta(nombre_cancion=None):
    """Reproduce una canción específica de la carpeta de música."""
    # Ruta a la carpeta de música
    music_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
    
    # Si no se especifica nombre, reproducir la primera canción encontrada
    if not nombre_cancion:
        # Listar archivos en la carpeta de música
        archivos = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav', '.ogg'))]
        if archivos:
            nombre_cancion = archivos[0]
        else:
            print("No se encontraron archivos de música en la carpeta.")
            return False
    
    # Ruta completa al archivo de música
    ruta_cancion = os.path.join(music_folder, nombre_cancion)
    
    # Detener cualquier reproducción actual
    detener()
    
    # Cargar y reproducir la canción
    if cargar_musica(ruta_cancion):
        return reproducir()
    return False
