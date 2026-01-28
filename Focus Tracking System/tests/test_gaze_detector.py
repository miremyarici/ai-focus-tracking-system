"""
Unit tests for GazeDetector module.
"""

import unittest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gaze_detector import GazeDetector


class TestGazeDetector(unittest.TestCase):
    """GazeDetector sınıfı için unit testler."""
    
    def setUp(self):
        """Her test öncesi çalışır."""
        self.detector = GazeDetector(sensitivity=0.25)
    
    def tearDown(self):
        """Her test sonrası çalışır."""
        self.detector.release()
    
    def test_initialization(self):
        """GazeDetector başlatma testi."""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.sensitivity, 0.25)
        self.assertIsNotNone(self.detector.face_cascade)
        self.assertIsNotNone(self.detector.eye_cascade)
    
    def test_default_sensitivity(self):
        """Varsayılan hassasiyet testi."""
        detector = GazeDetector()
        self.assertIsNotNone(detector.sensitivity)
        detector.release()
    
    def test_sensitivity_setter(self):
        """Hassasiyet ayarlama testi."""
        self.detector.set_sensitivity(0.5)
        self.assertEqual(self.detector.sensitivity, 0.5)
    
    def test_process_black_frame(self):
        """Siyah frame işleme testi (yüz yok)."""
        black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        processed, is_looking, direction = self.detector.process_frame(black_frame)
        
        self.assertIsNotNone(processed)
        self.assertEqual(processed.shape, black_frame.shape)
        self.assertFalse(is_looking)
        self.assertFalse(self.detector.is_face_detected())
    
    def test_process_white_frame(self):
        """Beyaz frame işleme testi (yüz yok)."""
        white_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
        
        processed, is_looking, direction = self.detector.process_frame(white_frame)
        
        self.assertIsNotNone(processed)
        self.assertFalse(is_looking)
    
    def test_getter_methods(self):
        """Getter metodları testi."""
        self.assertTrue(self.detector.is_looking_at_screen())
        self.assertFalse(self.detector.is_face_detected())
        self.assertEqual(self.detector.get_gaze_direction(), "merkez")
        
        black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.detector.process_frame(black_frame)
        
        self.assertFalse(self.detector.is_looking_at_screen())
    
    def test_color_values(self):
        """Renk değerlerinin doğruluğu testi."""
        self.assertIsInstance(self.detector.COLOR_FACE, tuple)
        self.assertEqual(len(self.detector.COLOR_FACE), 3)
        
        self.assertIsInstance(self.detector.COLOR_EYE, tuple)
        self.assertEqual(len(self.detector.COLOR_EYE), 3)
        
        self.assertIsInstance(self.detector.COLOR_PUPIL, tuple)
        self.assertEqual(len(self.detector.COLOR_PUPIL), 3)
    
    def test_detect_pupil_empty_roi(self):
        """Boş ROI ile göz bebeği tespiti testi."""
        empty_roi = np.zeros((10, 10), dtype=np.uint8)
        
        center, radius = self.detector.detect_pupil(empty_roi)
        
        self.assertTrue(center is None or radius == 0)
    
    def test_release(self):
        """Release metodu testi."""
        self.detector.release()
        self.detector.release()


class TestGazeDetectorEdgeCases(unittest.TestCase):
    """GazeDetector için edge case testleri."""
    
    def test_very_small_frame(self):
        """Çok küçük frame testi."""
        detector = GazeDetector()
        small_frame = np.zeros((10, 10, 3), dtype=np.uint8)
        
        processed, is_looking, direction = detector.process_frame(small_frame)
        self.assertIsNotNone(processed)
        detector.release()
    
    def test_extreme_sensitivity(self):
        """Uç hassasiyet değerleri testi."""
        detector_low = GazeDetector(sensitivity=0.01)
        self.assertEqual(detector_low.sensitivity, 0.01)
        detector_low.release()
        
        detector_high = GazeDetector(sensitivity=1.0)
        self.assertEqual(detector_high.sensitivity, 1.0)
        detector_high.release()


if __name__ == "__main__":
    unittest.main()
