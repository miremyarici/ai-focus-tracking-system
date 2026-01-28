"""
Unit tests for AlertManager module.
"""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alert_manager import AlertManager


class TestAlertManager(unittest.TestCase):
    """AlertManager sınıfı için unit testler."""
    
    def setUp(self):
        """Her test öncesi çalışır."""
        self.manager = AlertManager(cooldown_seconds=1.0)
    
    def tearDown(self):
        """Her test sonrası çalışır."""
        self.manager.stop_alert()
    
    def test_initialization(self):
        """AlertManager başlatma testi."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.cooldown_seconds, 1.0)
        self.assertFalse(self.manager.should_show_warning())
    
    def test_trigger_alert(self):
        """Uyarı tetikleme testi."""
        self.manager.trigger_alert()
        self.assertTrue(self.manager.should_show_warning())
    
    def test_stop_alert(self):
        """Uyarı durdurma testi."""
        self.manager.trigger_alert()
        self.assertTrue(self.manager.should_show_warning())
        
        self.manager.stop_alert()
        self.assertFalse(self.manager.should_show_warning())
    
    def test_warning_state(self):
        """Uyarı durumu get/set testi."""
        self.assertFalse(self.manager.should_show_warning())
        
        self.manager.set_warning_state(True)
        self.assertTrue(self.manager.should_show_warning())
        
        self.manager.set_warning_state(False)
        self.assertFalse(self.manager.should_show_warning())
    
    def test_reset(self):
        """Reset fonksiyonu testi."""
        self.manager.trigger_alert()
        self.assertTrue(self.manager.should_show_warning())
        
        self.manager.reset()
        self.assertFalse(self.manager.should_show_warning())
    
    def test_cooldown_setter(self):
        """Cooldown ayarlama testi."""
        self.manager.set_cooldown(3.0)
        self.assertEqual(self.manager.cooldown_seconds, 3.0)
        
        self.manager.set_cooldown(0.1)
        self.assertEqual(self.manager.cooldown_seconds, 0.5)
    
    def test_custom_sound_file(self):
        """Özel ses dosyası testi."""
        custom_path = "custom_sound.mp3"
        manager = AlertManager(sound_file=custom_path)
        self.assertEqual(manager.sound_file, custom_path)
    
    def test_thread_safety(self):
        """Thread güvenliği testi."""
        import threading
        
        errors = []
        
        def trigger_alerts():
            try:
                for _ in range(10):
                    self.manager.trigger_alert()
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)
        
        def stop_alerts():
            try:
                for _ in range(10):
                    self.manager.stop_alert()
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=trigger_alerts),
            threading.Thread(target=stop_alerts),
            threading.Thread(target=trigger_alerts),
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
