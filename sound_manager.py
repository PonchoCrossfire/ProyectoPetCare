import io
import math
import os
import struct
import threading
import wave

# Detección de motor de audio (soporta tanto pygame tradicional como pygame-ce)
PYGAME_LIB = None
try:
    import pygame
    PYGAME_LIB = pygame
except ImportError:
    try:
        import pygame_ce as pygame
        PYGAME_LIB = pygame
    except ImportError:
        PYGAME_LIB = None

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        if PYGAME_LIB is not None:
            try:
                PYGAME_LIB.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
                self._prepare_minecraft_sounds()
            except Exception:
                pass

    def _generate_wav_bytes(self, samples, sample_rate=44100) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            packed = struct.pack("<" + "h" * len(samples), *samples)
            wf.writeframes(packed)
        return buf.getvalue()

    def _synth_wolf_bark(self) -> bytes:
        sr = 44100
        duration = 0.34
        samples = []
        seed = 1337
        for i in range(int(sr * duration)):
            t = i / sr
            if t < 0.13:
                lt = t / 0.13
                env = math.sin(math.pi * lt) ** 0.6
                freq = 320 + 220 * math.sin(math.pi * lt) - 120 * lt
            elif 0.15 <= t < 0.32:
                lt = (t - 0.15) / 0.17
                env = math.sin(math.pi * lt) ** 0.7
                freq = 360 + 260 * math.sin(math.pi * lt) - 180 * lt
            else:
                env = 0.0
                freq = 100

            seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
            noise = ((seed / 0x7FFFFFFF) * 2.0 - 1.0) * 0.35

            tone = (
                0.55 * math.sin(2 * math.pi * freq * t)
                + 0.25 * math.sin(4 * math.pi * freq * t)
                + noise
            )
            val = int(max(-1.0, min(1.0, tone * env)) * 26000)
            samples.append(val)
        return self._generate_wav_bytes(samples, sr)

    def _synth_cat_meow(self) -> bytes:
        sr = 44100
        duration = 0.48
        samples = []
        phase = 0.0
        for i in range(int(sr * duration)):
            t = i / sr
            lt = t / duration
            env = math.sin(math.pi * lt) ** 0.8
            freq = 580 + 320 * math.sin(math.pi * (lt ** 0.65)) - 220 * (lt ** 1.4)
            vibrato = 12 * math.sin(2 * math.pi * 6.5 * t)
            phase += 2 * math.pi * (freq + vibrato) / sr

            wave_val = (
                0.65 * math.sin(phase)
                + 0.25 * math.sin(2 * phase)
                + 0.10 * math.sin(3 * phase)
            )
            val = int(max(-1.0, min(1.0, wave_val * env)) * 24000)
            samples.append(val)
        return self._generate_wav_bytes(samples, sr)

    def _prepare_minecraft_sounds(self):
        os.makedirs("assets", exist_ok=True)
        wolf_path = os.path.join("assets", "minecraft_wolf_bark.wav")
        cat_path = os.path.join("assets", "minecraft_cat_meow.wav")

        if not os.path.exists(wolf_path):
            with open(wolf_path, "wb") as f:
                f.write(self._synth_wolf_bark())
        if not os.path.exists(cat_path):
            with open(cat_path, "wb") as f:
                f.write(self._synth_cat_meow())

        self.sounds["wolf"] = PYGAME_LIB.mixer.Sound(wolf_path)
        self.sounds["cat"] = PYGAME_LIB.mixer.Sound(cat_path)

    def play_wolf_bark(self):
        if not self.enabled:
            return
        threading.Thread(target=self._play_thread, args=("wolf",), daemon=True).start()

    def play_cat_meow(self):
        if not self.enabled:
            return
        threading.Thread(target=self._play_thread, args=("cat",), daemon=True).start()

    def _play_thread(self, kind: str):
        if PYGAME_LIB is not None and kind in self.sounds:
            self.sounds[kind].play()
        elif WINSOUND_AVAILABLE:
            if kind == "wolf":
                winsound.Beep(420, 90)
                winsound.Beep(520, 130)
            else:
                winsound.Beep(780, 160)
                winsound.Beep(620, 220)