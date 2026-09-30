import os
import math
import struct
import io
import wave
import threading

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
import pygame

class SoundManager:
    _inicializado = False
    _sonidos = {}
    _musica_activa = False

    @classmethod
    def init(cls):
        if not cls._inicializado:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                cls._inicializado = True
                cls._generar_efectos_en_memoria()
            except Exception as e:
                print(f"[SoundManager] No se pudo inicializar audio: {e}")

    @classmethod
    def _crear_wav_en_memoria(cls, tono_frec, duracion_seg=0.06, decay=True):
        sample_rate = 44100
        num_muestras = int(sample_rate * duracion_seg)
        buffer = io.BytesIO()
        
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            
            muestras = []
            for i in range(num_muestras):
                t = i / sample_rate
                val = math.sin(2 * math.pi * tono_frec * t)
                factor = math.exp(-4 * (i / num_muestras)) if decay else 1.0
                val = int(val * factor * 16000)
                muestras.append(struct.pack('<h', val))
            
            wav.writeframes(b''.join(muestras))
        
        buffer.seek(0)
        return pygame.mixer.Sound(buffer)

    @classmethod
    def _generar_efectos_en_memoria(cls):
        try:
            cls._sonidos["click"] = cls._crear_wav_en_memoria(800, duracion_seg=0.03)
            cls._sonidos["click"].set_volume(0.20)

            cls._sonidos["exito"] = cls._crear_wav_en_memoria(950, duracion_seg=0.10)
            cls._sonidos["exito"].set_volume(0.30)

            cls._sonidos["alerta"] = cls._crear_wav_en_memoria(240, duracion_seg=0.12)
            cls._sonidos["alerta"].set_volume(0.25)

            cls._sonidos["modal"] = cls._crear_wav_en_memoria(620, duracion_seg=0.06)
            cls._sonidos["modal"].set_volume(0.20)
        except Exception:
            pass

    @classmethod
    def reproducir(cls, nombre):
        if not cls._inicializado:
            return
        snd = cls._sonidos.get(nombre)
        if snd:
            threading.Thread(target=snd.play, daemon=True).start()

    @classmethod
    def reproducir_musica_bienvenida(cls, ruta_cancion="bienvenida.mp3"):
        if not cls._inicializado:
            return
        
        def _play():
            try:
                if os.path.exists(ruta_cancion):
                    pygame.mixer.music.load(ruta_cancion)
                    pygame.mixer.music.set_volume(0.35)
                    pygame.mixer.music.play(-1)
                    cls._musica_activa = True
            except Exception as e:
                print(f"[SoundManager] Nota sobre música: {e}")

        threading.Thread(target=_play, daemon=True).start()

    @classmethod
    def detener_musica(cls, fade_ms=700):
        if cls._inicializado and cls._musica_activa:
            try:
                pygame.mixer.music.fadeout(fade_ms)
                cls._musica_activa = False
            except Exception:
                pass