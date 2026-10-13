"""Sound effects and background music, all generated in code.

Because nothing is loaded from files there are no licences to worry about and
no missing-file errors. If the computer has no sound device the game simply
runs silently.
"""
import math
import random
import sys
from array import array

import pygame

SAMPLE_RATE = 22050
PEAK = 32767

# ---------------------------------------------------------------- sound building blocks
# These are plain Python (no pygame), so they are easy to test.


def _wave(kind, cycles):
    """One point of a wave. 'cycles' is how far through the wave we are (0.25 = a quarter turn)."""
    frac = cycles % 1.0
    if kind == "sine":
        return math.sin(2 * math.pi * frac)
    if kind == "square":
        return 1.0 if frac < 0.5 else -1.0
    if kind == "saw":
        return 2.0 * frac - 1.0
    if kind == "triangle":
        return 4.0 * abs(frac - 0.5) - 1.0
    raise ValueError(f"unknown wave kind: {kind}")


def make_tone(freq_start, freq_end, duration, volume=0.4, kind="square", rate=SAMPLE_RATE, decay=1.0):
    """A beep that slides from freq_start to freq_end. Returns an array of 16-bit samples."""
    count = max(1, int(duration * rate))
    attack = max(1, int(0.004 * rate))  # tiny fade-in avoids a click
    out = array("h")
    phase = 0.0
    for i in range(count):
        t = i / count
        freq = freq_start + (freq_end - freq_start) * t
        phase += freq / rate
        env = min(1.0, i / attack) * (1.0 - t) ** decay
        out.append(int(PEAK * volume * env * _wave(kind, phase)))
    return out


def make_noise(duration, volume=0.4, rate=SAMPLE_RATE, smooth=0.0, seed=1):
    """A burst of static (crashes, thumps). 'smooth' near 0.9 makes it sound lower and softer."""
    rng = random.Random(seed)
    count = max(1, int(duration * rate))
    out = array("h")
    last = 0.0
    for i in range(count):
        last = last * smooth + rng.uniform(-1, 1) * (1.0 - smooth)
        env = (1.0 - i / count) ** 2
        out.append(int(PEAK * volume * env * last))
    return out


def join(*parts):
    """Play sounds one after another."""
    out = array("h")
    for p in parts:
        out.extend(p)
    return out


def overlay(base, extra, gain=1.0):
    """Play two sounds at the same time (the result is as long as the longer one)."""
    size = max(len(base), len(extra))
    out = array("h", bytes(2 * size))
    for i in range(size):
        v = (base[i] if i < len(base) else 0) + gain * (extra[i] if i < len(extra) else 0)
        out[i] = int(max(-PEAK, min(PEAK, v)))
    return out


def build_effects(rate=SAMPLE_RATE):
    """Returns {name: samples} for every sound effect in the game."""
    r = rate
    return {
        "jump": make_tone(280, 640, 0.16, 0.30, "square", r),
        "coin": join(make_tone(988, 988, 0.07, 0.28, "square", r),
                     make_tone(1319, 1319, 0.20, 0.28, "square", r)),
        "hurt": overlay(make_tone(320, 90, 0.32, 0.40, "saw", r),
                        make_noise(0.18, 0.35, r, 0.3), 0.8),
        "stomp": overlay(make_tone(230, 70, 0.14, 0.60, "sine", r),
                         make_noise(0.08, 0.30, r, 0.85), 0.8),
        "checkpoint": join(make_tone(660, 660, 0.09, 0.30, "sine", r),
                           make_tone(990, 990, 0.20, 0.30, "sine", r)),
        "click": make_tone(700, 700, 0.04, 0.22, "square", r),
        "victory": join(make_tone(523, 523, 0.12, 0.30, "square", r),
                        make_tone(659, 659, 0.12, 0.30, "square", r),
                        make_tone(784, 784, 0.12, 0.30, "square", r),
                        make_tone(1047, 1047, 0.45, 0.30, "square", r, 0.6)),
        "game_over": join(make_tone(392, 392, 0.18, 0.32, "saw", r),
                          make_tone(330, 330, 0.18, 0.32, "saw", r),
                          make_tone(262, 262, 0.18, 0.32, "saw", r),
                          make_tone(196, 196, 0.50, 0.32, "saw", r, 0.6)),
    }


NOTES = {
    "G2": 98.00, "A2": 110.00, "C3": 130.81, "F2": 87.31,
    "A4": 440.00, "B4": 493.88, "C5": 523.25, "D5": 587.33, "E5": 659.25, "G5": 783.99,
}

# 4 bars of 8 eighth-notes. "." is a rest. Chords: C, Am, F, G.
MELODY = ("E5 . G5 E5 D5 . C5 D5 "
          "C5 . E5 C5 A4 . C5 E5 "
          "A4 . C5 A4 C5 . A4 G5 "
          "D5 . G5 D5 B4 . D5 G5").split()
BASS = ["C3", "A2", "F2", "G2"]
EIGHTH = 0.25  # seconds per eighth-note (120 beats per minute)


def build_music(rate=SAMPLE_RATE):
    """An 8-second chiptune loop. Returns 16-bit samples."""
    total = int(len(MELODY) * EIGHTH * rate)
    mix = [0] * total

    def add(samples, start_seconds):
        start = int(start_seconds * rate)
        for i, v in enumerate(samples):
            if start + i < total:
                mix[start + i] += v

    for step, name in enumerate(MELODY):
        if name != ".":
            f = NOTES[name]
            add(make_tone(f, f, 0.22, 0.13, "square", rate, 0.6), step * EIGHTH)
    for bar, name in enumerate(BASS):
        f = NOTES[name]
        for half in (0, 1):
            add(make_tone(f, f, 0.9, 0.26, "triangle", rate, 0.4), bar * 8 * EIGHTH + half * 1.0)
    return array("h", [max(-PEAK, min(PEAK, v)) for v in mix])


def clamp01(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return 0.0
    if v != v:  # NaN
        return 0.0
    return min(1.0, max(0.0, v))


# ---------------------------------------------------------------- the Audio class the game uses


class Audio:
    """Plays effects and music. Every method is safe to call even when sound is unavailable."""

    def __init__(self, muted=False, music_volume=0.5, sfx_volume=0.7):
        self.enabled = False
        self.muted = bool(muted)
        self.music_volume = clamp01(music_volume)
        self.sfx_volume = clamp01(sfx_volume)
        self.sounds = {}
        self._music = None
        self._channel = None
        self._rate = SAMPLE_RATE
        self._channels = 1
        self._init_mixer()

    def _init_mixer(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
            info = pygame.mixer.get_init()
            if not info:
                raise pygame.error("mixer did not start")
            self._rate, fmt, self._channels = info
            if fmt != -16:
                raise pygame.error(f"unsupported sample format {fmt}")
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(1)  # channel 0 is kept only for the music
            self._channel = pygame.mixer.Channel(0)
            for name, samples in build_effects(self._rate).items():
                self.sounds[name] = pygame.mixer.Sound(buffer=self._to_bytes(samples))
            self.enabled = True
        except (pygame.error, OSError, ValueError) as exc:
            self.enabled = False
            print(f"[audio] Sound is off: {exc}", file=sys.stderr)

    def _to_bytes(self, samples):
        """Repeat each sample if the sound card wants stereo."""
        if self._channels == 1:
            return samples.tobytes()
        out = array("h")
        for v in samples:
            out.extend([v] * self._channels)
        return out.tobytes()

    # ---- effects ----
    def play(self, name):
        if not self.enabled or self.muted:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.set_volume(self.sfx_volume)
            sound.play()

    # ---- music ----
    def start_music(self):
        if not self.enabled:
            return
        try:
            if self._music is None:
                self._music = pygame.mixer.Sound(buffer=self._to_bytes(build_music(self._rate)))
            if not self._channel.get_busy():
                self._channel.play(self._music, loops=-1)
            self._channel.unpause()
            self._apply_volumes()
        except pygame.error as exc:
            print(f"[audio] Music could not start: {exc}", file=sys.stderr)

    def stop_music(self):
        if self.enabled and self._channel is not None:
            self._channel.stop()

    def pause_music(self):
        if self.enabled and self._channel is not None:
            self._channel.pause()

    def resume_music(self):
        if self.enabled and self._channel is not None:
            self._channel.unpause()

    # ---- settings ----
    def _apply_volumes(self):
        if self.enabled and self._channel is not None:
            self._channel.set_volume(0.0 if self.muted else self.music_volume)

    def toggle_mute(self):
        self.muted = not self.muted
        self._apply_volumes()
        return self.muted

    def set_music_volume(self, value):
        self.music_volume = clamp01(value)
        self._apply_volumes()

    def set_sfx_volume(self, value):
        self.sfx_volume = clamp01(value)

    def apply_settings(self, data):
        """data is the dict from SaveSystem.data."""
        self.muted = bool(data.get("muted", self.muted))
        self.music_volume = clamp01(data.get("music_volume", self.music_volume))
        self.sfx_volume = clamp01(data.get("sfx_volume", self.sfx_volume))
        self._apply_volumes()

    def settings(self):
        return {"muted": self.muted, "music_volume": self.music_volume, "sfx_volume": self.sfx_volume}