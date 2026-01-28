"""
Unit tests for config module.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


class TestConfig(unittest.TestCase):
    """Config modülü için unit testler."""
    
    def test_base_dir_exists(self):
        """BASE_DIR'in var olduğunu test et."""
        self.assertIsNotNone(config.BASE_DIR)
        self.assertTrue(os.path.exists(config.BASE_DIR))
        self.assertTrue(os.path.isdir(config.BASE_DIR))
    
    def test_sound_file_path(self):
        """Ses dosyası yolunun doğru oluşturulduğunu test et."""
        self.assertIsNotNone(config.SOUND_FILE)
        self.assertTrue(config.SOUND_FILE.startswith(config.BASE_DIR))
    
    def test_time_options(self):
        """TIME_OPTIONS'ın geçerli değerler içerdiğini test et."""
        self.assertIsInstance(config.TIME_OPTIONS, dict)
        self.assertTrue(len(config.TIME_OPTIONS) > 0)
        
        for label, minutes in config.TIME_OPTIONS.items():
            self.assertIsInstance(label, str)
            self.assertIsInstance(minutes, int)
            self.assertGreater(minutes, 0)
    
    def test_gaze_sensitivity(self):
        """GAZE_SENSITIVITY değerinin geçerli olduğunu test et."""
        self.assertIsInstance(config.GAZE_SENSITIVITY, (int, float))
        self.assertGreaterEqual(config.GAZE_SENSITIVITY, 0)
        self.assertLessEqual(config.GAZE_SENSITIVITY, 1)
    
    def test_distraction_threshold(self):
        """DISTRACTION_THRESHOLD değerinin geçerli olduğunu test et."""
        self.assertIsInstance(config.DISTRACTION_THRESHOLD, int)
        self.assertGreater(config.DISTRACTION_THRESHOLD, 0)
    
    def test_frame_skip(self):
        """FRAME_SKIP değerinin geçerli olduğunu test et."""
        self.assertIsInstance(config.FRAME_SKIP, int)
        self.assertGreaterEqual(config.FRAME_SKIP, 1)
    
    def test_target_fps(self):
        """TARGET_FPS değerinin geçerli olduğunu test et."""
        self.assertIsInstance(config.TARGET_FPS, int)
        self.assertGreater(config.TARGET_FPS, 0)
        self.assertLessEqual(config.TARGET_FPS, 120)
    
    def test_webcam_resolution(self):
        """Webcam çözünürlük değerlerinin geçerli olduğunu test et."""
        self.assertIsInstance(config.WEBCAM_WIDTH, int)
        self.assertIsInstance(config.WEBCAM_HEIGHT, int)
        self.assertGreater(config.WEBCAM_WIDTH, 0)
        self.assertGreater(config.WEBCAM_HEIGHT, 0)
    
    def test_window_size(self):
        """Pencere boyutlarının geçerli olduğunu test et."""
        self.assertIsInstance(config.WINDOW_SIZE, tuple)
        self.assertEqual(len(config.WINDOW_SIZE), 2)
        self.assertGreater(config.WINDOW_SIZE[0], 0)
        self.assertGreater(config.WINDOW_SIZE[1], 0)
        
        self.assertIsInstance(config.MIN_WINDOW_SIZE, tuple)
        self.assertEqual(len(config.MIN_WINDOW_SIZE), 2)
    
    def test_window_title(self):
        """Pencere başlığının var olduğunu test et."""
        self.assertIsInstance(config.WINDOW_TITLE, str)
        self.assertTrue(len(config.WINDOW_TITLE) > 0)
    
    def test_alert_cooldown(self):
        """ALERT_COOLDOWN değerinin geçerli olduğunu test et."""
        self.assertIsInstance(config.ALERT_COOLDOWN, (int, float))
        self.assertGreater(config.ALERT_COOLDOWN, 0)
    
    def test_colors(self):
        """COLORS dictionary'sinin geçerli olduğunu test et."""
        self.assertIsInstance(config.COLORS, dict)
        
        required_colors = ["face", "eye", "text", "alert", "pupil"]
        for color_name in required_colors:
            self.assertIn(color_name, config.COLORS)
            color = config.COLORS[color_name]
            self.assertIsInstance(color, tuple)
            self.assertEqual(len(color), 3)
            
            for value in color:
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 255)
    
    def test_platform_detection(self):
        """Platform tespitinin çalıştığını test et."""
        self.assertIn(config.PLATFORM, ['windows', 'macos', 'linux', 'unknown'])
    
    def test_get_platform_function(self):
        """get_platform fonksiyonunun çalıştığını test et."""
        platform = config.get_platform()
        self.assertIsInstance(platform, str)
        self.assertIn(platform, ['windows', 'macos', 'linux', 'unknown'])
    
    def test_pygame_available_flag(self):
        """PYGAME_AVAILABLE flag'inin boolean olduğunu test et."""
        self.assertIsInstance(config.PYGAME_AVAILABLE, bool)
    
    def test_is_pygame_available_function(self):
        """is_pygame_available fonksiyonunun çalıştığını test et."""
        result = config.is_pygame_available()
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
