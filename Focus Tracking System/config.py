"""
Focus Tracker Configuration Module
Merkezi konfigürasyon dosyası - tüm ayarlar burada tanımlanır.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.join(BASE_DIR, "Loud Alarm Sound Effect.mp3")

TIME_OPTIONS = {
    "10 Dakika": 10,
    "30 Dakika": 30,
    "1 Saat": 60,
    "2 Saat": 120
}

GAZE_SENSITIVITY = 0.25
DISTRACTION_THRESHOLD = 100

TARGET_FPS = 30
FRAME_SKIP = 2
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480

WINDOW_SIZE = (900, 700)
MIN_WINDOW_SIZE = (800, 600)
WINDOW_TITLE = "Odak Yardımcısı"

ALERT_COOLDOWN = 2.0

COLORS = {
    "face": (155, 152, 229),
    "eye": (141, 131, 181),
    "text": (155, 152, 229),
    "alert": (141, 131, 181),
    "pupil": (117, 104, 109),
}

def get_platform():
    """İşletim sistemini tespit et."""
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'macos'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return 'unknown'

PLATFORM = get_platform()

def is_pygame_available():
    """Pygame kütüphanesinin kullanılabilir olup olmadığını kontrol et."""
    try:
        import pygame
        return True
    except ImportError:
        return False

PYGAME_AVAILABLE = is_pygame_available()
