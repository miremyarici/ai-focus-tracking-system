"""
Alert Manager Module
Ses ve görsel uyarıları yöneten modül.
Cross-platform destek: Windows, macOS, Linux
"""

import threading
import time
import os
import sys
from typing import Optional

from config import SOUND_FILE, ALERT_COOLDOWN, PLATFORM, PYGAME_AVAILABLE

if PYGAME_AVAILABLE:
    import pygame


class AlertManager:
    """
    Uyarı seslerini ve görsel uyarı durumunu yöneten sınıf.
    Thread-safe ve cross-platform.
    """
    
    def __init__(self, cooldown_seconds: float = None, sound_file: str = None):
        """
        AlertManager'ı başlat.
        
        Args:
            cooldown_seconds: Uyarılar arası minimum bekleme süresi
            sound_file: Uyarı ses dosyası yolu (MP3/WAV)
        """
        self.cooldown_seconds = cooldown_seconds if cooldown_seconds is not None else ALERT_COOLDOWN
        self._last_alert_time: float = 0
        self._should_show_warning: bool = False
        self._is_playing: bool = False
        self._stop_sound: bool = False
        self._sound_thread: Optional[threading.Thread] = None
        
        self._lock = threading.Lock()
        self.sound_file = sound_file if sound_file is not None else SOUND_FILE
        
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                if os.path.exists(self.sound_file):
                    print(f"Uyarı sesi yüklendi: {self.sound_file}")
                else:
                    print(f"Uyarı: Ses dosyası bulunamadı: {self.sound_file}")
            except Exception as e:
                print(f"Pygame mixer başlatma hatası: {e}")
    
    def _play_system_beep(self, frequency: int = 1000, duration: int = 500):
        """
        Cross-platform sistem beep sesi.
        
        Args:
            frequency: Ses frekansı (Hz) - sadece Windows'ta geçerli
            duration: Süre (ms) - sadece Windows'ta geçerli
        """
        try:
            if PLATFORM == 'windows':
                import winsound
                winsound.Beep(frequency, duration)
            elif PLATFORM == 'macos':
                os.system('afplay /System/Library/Sounds/Ping.aiff &')
            elif PLATFORM == 'linux':
                result = os.system('command -v paplay > /dev/null 2>&1')
                if result == 0:
                    os.system('paplay /usr/share/sounds/freedesktop/stereo/bell.oga &')
                else:
                    print('\a', end='', flush=True)
            else:
                print('\a', end='', flush=True)
        except Exception as e:
            print(f"Beep sesi çalma hatası: {e}")
    
    def _play_beep_sequence(self, frequencies: list, duration: int = 150):
        """
        Bir dizi beep sesi çal (Windows'ta melodi, diğerlerinde tek ses).
        
        Args:
            frequencies: Frekans listesi
            duration: Her ses için süre (ms)
        """
        if PLATFORM == 'windows':
            try:
                import winsound
                for freq in frequencies:
                    winsound.Beep(freq, duration)
            except Exception as e:
                print(f"Ses çalma hatası: {e}")
        else:
            self._play_system_beep()
        
    def trigger_alert(self):
    """Uyarıyı tetikle (ses + görsel). Thread-safe."""
    should_play = False
    with self._lock:
        self._should_show_warning = True
        if not self._is_playing:
            self._is_playing = True
            should_play = True
    
    if should_play:
        self._start_sound_thread()

def _start_sound_thread(self):
    """Ses çalma thread'ini başlat (lock almadan)."""
    def play_sound():
        try:
            if PYGAME_AVAILABLE and os.path.exists(self.sound_file):
                pygame.mixer.music.load(self.sound_file)
                pygame.mixer.music.play(-1)
            else:
                self._play_system_beep()
        except Exception as e:
            print(f"Ses çalma hatası: {e}")
            with self._lock:
                self._is_playing = False
            self._play_system_beep()
    
    self._sound_thread = threading.Thread(target=play_sound, daemon=True)
    self._sound_thread.start()
    
    def play_alert_sound(self):
        """Uyarı sesini senkron olarak çal."""
        try:
            if PYGAME_AVAILABLE and os.path.exists(self.sound_file):
                pygame.mixer.music.load(self.sound_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                self._play_system_beep()
        except Exception as e:
            print(f"Ses çalma hatası: {e}")
    
    def stop_alert(self):
        """
        Uyarıyı durdur (ses ve görsel uyarıyı kapat).
        Thread-safe.
        """
        with self._lock:
            self._should_show_warning = False
            
            if PYGAME_AVAILABLE and self._is_playing:
                try:
                    pygame.mixer.music.stop()
                except Exception as e:
                    print(f"Ses durdurma hatası: {e}")
            
            self._is_playing = False
    
    def should_show_warning(self) -> bool:
        """Görsel uyarı gösterilmeli mi? Thread-safe."""
        with self._lock:
            return self._should_show_warning
    
    def set_warning_state(self, state: bool):
        """Görsel uyarı durumunu ayarla. Thread-safe."""
        with self._lock:
            self._should_show_warning = state
    
    def reset(self):
        """AlertManager'ı sıfırla. Thread-safe."""
        with self._lock:
            self._last_alert_time = 0
            self._should_show_warning = False
            self._stop_sound = True
    
    def set_cooldown(self, seconds: float):
        """Cooldown süresini ayarla."""
        self.cooldown_seconds = max(0.5, seconds)
    
    def play_start_sound(self):
        """Oturum başlangıç sesi (yükselen ton)."""
        self._play_beep_sequence([500, 700, 900], 150)
    
    def play_end_sound(self):
        """Oturum bitiş sesi (alçalan ton)."""
        self._play_beep_sequence([900, 700, 500], 150)
    
    def play_complete_sound(self):
        """Tamamlanma sesi (melodi)."""
        self._play_beep_sequence([523, 659, 784, 1047], 150)


if __name__ == "__main__":
    print(f"Alert Manager Test - Platform: {PLATFORM}")
    print(f"Pygame available: {PYGAME_AVAILABLE}")
    print(f"Sound file: {SOUND_FILE}")
    print(f"Sound file exists: {os.path.exists(SOUND_FILE)}")
    
    manager = AlertManager(cooldown_seconds=1.0)
    
    print("\nBaşlangıç sesi çalınıyor...")
    manager.play_start_sound()
    time.sleep(1)
    
    print("Uyarı sesi çalınıyor...")
    manager.trigger_alert()
    print(f"Uyarı gösterilmeli mi: {manager.should_show_warning()}")
    
    time.sleep(2)
    print("Uyarı durduruluyor...")
    manager.stop_alert()
    
    time.sleep(0.5)
    print("Bitiş sesi çalınıyor...")
    manager.play_end_sound()
    
    print("\nTest tamamlandı!")
