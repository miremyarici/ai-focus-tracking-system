"""
Gaze Detector Module (Auto-Lighting Fix)
Işık değişimlerine karşı Histogram Eşitleme ve Dinamik Eşikleme içerir.
"""

import cv2
import numpy as np
from typing import Tuple

from config import GAZE_SENSITIVITY, COLORS


class GazeDetector:
    """
    OpenCV tabanlı bakış yönü tespit sınıfı.
    Haar Cascade kullanarak yüz ve göz tespiti yapar.
    """
    
    def __init__(self, sensitivity: float = None):
        """
        GazeDetector'ı başlat.
        
        Args:
            sensitivity: Bakış hassasiyeti (0.0-1.0 arası)
        """
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        self.sensitivity = sensitivity if sensitivity is not None else GAZE_SENSITIVITY
        
        self.COLOR_FACE = COLORS.get("face", (155, 152, 229))
        self.COLOR_EYE = COLORS.get("eye", (141, 131, 181))
        self.COLOR_TEXT = COLORS.get("text", (155, 152, 229))
        self.COLOR_ALERT = COLORS.get("alert", (141, 131, 181))
        self.COLOR_PUPIL = COLORS.get("pupil", (117, 104, 109))
        
        self._is_looking_at_screen = True
        self._gaze_direction = "merkez"
        self._face_detected = False

    def detect_pupil(self, eye_roi_gray):
        """
        Işık değişimlerine dayanıklı göz bebeği tespiti.
        
        Args:
            eye_roi_gray: Gri tonlamalı göz bölgesi
            
        Returns:
            tuple: (center, radius) veya (None, 0)
        """
        try:
            eye_roi_gray = cv2.equalizeHist(eye_roi_gray)
            blur = cv2.GaussianBlur(eye_roi_gray, (7, 7), 0)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(blur)
            threshold_value = min_val + 20 
            _, threshold = cv2.threshold(blur, threshold_value, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
            
            if len(contours) > 0:
                cnt = contours[0]
                (cx, cy), radius = cv2.minEnclosingCircle(cnt)
                area = cv2.contourArea(cnt)
                if 2 < radius < (eye_roi_gray.shape[0] * 0.4):
                    return (int(cx), int(cy)), int(radius)
            
            return None, 0
        except Exception as e:
            return None, 0

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, bool, str]:
        """
        Video frame'ini işle ve bakış yönünü tespit et.
        
        Args:
            frame: BGR formatında video frame
            
        Returns:
            tuple: (işlenmiş_frame, ekrana_bakıyor_mu, bakış_yönü)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        output_frame = frame.copy()
        
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            self._face_detected = True
            (x, y, w, h) = faces[0]
            
            cv2.rectangle(output_frame, (x, y), (x+w, y+h), self.COLOR_FACE, 2)
            
            roi_gray_face = gray[y:y+h//2, x:x+w]
            roi_color_face = output_frame[y:y+h//2, x:x+w]
            
            eyes = self.eye_cascade.detectMultiScale(roi_gray_face)
            
            pupil_ratios = [] 
            
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color_face, (ex, ey), (ex+ew, ey+eh), self.COLOR_EYE, 1)
                
                eye_roi = roi_gray_face[ey:ey+eh, ex:ex+ew]
                pupil_center, radius = self.detect_pupil(eye_roi)
                
                if pupil_center:
                    cv2.circle(
                        roi_color_face, 
                        (ex + pupil_center[0], ey + pupil_center[1]), 
                        radius, 
                        self.COLOR_PUPIL, 
                        2
                    )
                    
                    ratio = pupil_center[0] / ew
                    pupil_ratios.append(ratio)

            if len(pupil_ratios) > 0:
                avg_ratio = sum(pupil_ratios) / len(pupil_ratios)
                
                limit_low = 0.50 - (self.sensitivity / 2)
                limit_high = 0.50 + (self.sensitivity / 2)
                
                if limit_low <= avg_ratio <= limit_high:
                    self._gaze_direction = "merkez"
                    self._is_looking_at_screen = True
                else:
                    self._is_looking_at_screen = False
                    if avg_ratio < limit_low:
                        self._gaze_direction = "sol" 
                    else:
                        self._gaze_direction = "sag"
                
                cv2.putText(
                    output_frame, 
                    f"Bakis: {self._gaze_direction}", 
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, 
                    self.COLOR_TEXT, 
                    2
                )
            else:
                self._is_looking_at_screen = False 
                cv2.putText(
                    output_frame, 
                    "Goz tespit edilemiyor", 
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, 
                    self.COLOR_ALERT, 
                    2
                )
        else:
            self._face_detected = False
            self._is_looking_at_screen = False
            cv2.putText(
                output_frame, 
                "Yuz tespit edilemedi!", 
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                self.COLOR_TEXT, 
                2
            )
        
        return output_frame, self._is_looking_at_screen, self._gaze_direction

    def release(self):
        """Kaynakları serbest bırak."""
        pass

    def is_looking_at_screen(self) -> bool:
        return self._is_looking_at_screen
    
    def is_face_detected(self) -> bool:
        return self._face_detected
    
    def get_gaze_direction(self) -> str:
        return self._gaze_direction
    
    def set_sensitivity(self, val: float):
        self.sensitivity = val
