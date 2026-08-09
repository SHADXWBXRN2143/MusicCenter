"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Spectrum Analyzer

 Reads real PCM from an ALSA capture device (an ALSA-loopback
 monitor of whatever mpv is actually playing - see README) and
 turns it into per-band levels for the "now playing" waveform,
 so it can be audio-reactive instead of decorative.

 Fully optional: if numpy/pyalsaaudio aren't installed, or no
 capture device is configured, this stays inert and the
 frontend falls back to the existing CSS animation - exactly
 the same degrade-gracefully approach as MPVPlayer when `mpv`
 itself isn't installed.

 Version : 0.1
===========================================================
"""

import threading
import time

import config

try:
    import alsaaudio
    import numpy as np
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False


class SpectrumAnalyzer:

    def __init__(self):
        self.available = False

        self._levels = [0.0] * config.SPECTRUM_BAR_COUNT
        self._lock = threading.Lock()

        if _DEPS_OK and config.SPECTRUM_CAPTURE_DEVICE:
            threading.Thread(target=self._run, daemon=True).start()

    def _open(self):
        """
        Retries opening the capture device for a few seconds - right after
        the service starts, the loopback card can briefly fail to open
        (seen in practice: works fine seconds later, same process, same
        device string), so a single immediate attempt isn't reliable here,
        the same reasoning MPVPlayer already applies to its own IPC socket.
        """

        last_error = None

        for _ in range(10):
            try:
                return alsaaudio.PCM(
                    alsaaudio.PCM_CAPTURE,
                    alsaaudio.PCM_NORMAL,
                    channels=1,
                    rate=44100,
                    format=alsaaudio.PCM_FORMAT_S16_LE,
                    periodsize=1024,
                    device=config.SPECTRUM_CAPTURE_DEVICE,
                )
            except Exception as e:
                last_error = e
                time.sleep(1)

        raise last_error

    def _run(self):
        try:
            pcm = self._open()
        except Exception as e:
            print("SpectrumAnalyzer: capture device unavailable:", e)
            return

        self.available = True
        bands = config.SPECTRUM_BAR_COUNT

        while True:
            try:
                length, data = pcm.read()
            except Exception as e:
                print("SpectrumAnalyzer: read error:", e)
                time.sleep(0.5)
                continue

            if length <= 0:
                time.sleep(0.01)
                continue

            samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)

            if samples.size == 0:
                continue

            windowed = samples * np.hanning(samples.size)
            spectrum = np.abs(np.fft.rfft(windowed))
            chunks = np.array_split(spectrum, bands)

            levels = [
                float(min(1.0, chunk.mean() / config.SPECTRUM_GAIN))
                for chunk in chunks
            ]

            with self._lock:
                self._levels = levels

    def get_levels(self):
        with self._lock:
            return list(self._levels)


spectrum = SpectrumAnalyzer()
