"""
Gesture detection module for HandLaunch.

This module handles hand gesture detection using MediaPipe and OpenCV.
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Dict, Optional
from loguru import logger


class GestureDetector:
    """Hand gesture detection using MediaPipe."""
    
    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Create hands instance
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Gesture templates
        self.gesture_templates = self._load_gesture_templates()
        
        logger.info("Gesture detector initialized")
    
    def detect_gestures(self, frame: np.ndarray) -> List[Tuple[str, float]]:
        """Detect gestures in the given frame."""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            results = self.hands.process(rgb_frame)
            
            detected_gestures = []
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Extract hand landmarks
                    landmarks = self._extract_landmarks(hand_landmarks)
                    
                    # Classify gesture
                    gesture_name, confidence = self._classify_gesture(landmarks)
                    
                    if gesture_name and confidence > 0.5:
                        detected_gestures.append((gesture_name, confidence))
            
            return detected_gestures
            
        except Exception as e:
            logger.error(f"Error in gesture detection: {e}")
            return []
    
    def _extract_landmarks(self, hand_landmarks) -> np.ndarray:
        """Extract normalized landmarks from hand."""
        landmarks = []
        
        for landmark in hand_landmarks.landmark:
            landmarks.extend([landmark.x, landmark.y, landmark.z])
        
        return np.array(landmarks)
    
    def _classify_gesture(self, landmarks: np.ndarray) -> Tuple[Optional[str], float]:
        """Classify gesture based on landmarks."""
        try:
            # Simple gesture classification based on finger positions
            # This is a basic implementation - can be enhanced with ML models
            
            # Extract key points
            thumb_tip = landmarks[3:6]  # Thumb tip
            index_tip = landmarks[6:9]  # Index finger tip
            middle_tip = landmarks[9:12]  # Middle finger tip
            ring_tip = landmarks[12:15]  # Ring finger tip
            pinky_tip = landmarks[15:18]  # Pinky tip
            
            # Calculate finger distances from palm center
            palm_center = landmarks[0:3]  # Wrist as palm center
            
            thumb_dist = np.linalg.norm(thumb_tip - palm_center)
            index_dist = np.linalg.norm(index_tip - palm_center)
            middle_dist = np.linalg.norm(middle_tip - palm_center)
            ring_dist = np.linalg.norm(ring_tip - palm_center)
            pinky_dist = np.linalg.norm(pinky_tip - palm_center)
            
            # Simple gesture recognition
            if self._is_open_palm(thumb_dist, index_dist, middle_dist, ring_dist, pinky_dist):
                return "open_palm", 0.9
            elif self._is_fist(thumb_dist, index_dist, middle_dist, ring_dist, pinky_dist):
                return "fist", 0.9
            elif self._is_peace_sign(index_dist, middle_dist, ring_dist, pinky_dist):
                return "peace_sign", 0.8
            elif self._is_thumbs_up(thumb_dist, index_dist, middle_dist, ring_dist, pinky_dist):
                return "thumbs_up", 0.8
            elif self._is_pointing(index_dist, middle_dist, ring_dist, pinky_dist):
                return "pointing", 0.7
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Error in gesture classification: {e}")
            return None, 0.0
    
    def _is_open_palm(self, thumb_dist, index_dist, middle_dist, ring_dist, pinky_dist) -> bool:
        """Check if gesture is an open palm."""
        # All fingers extended
        threshold = 0.1
        return (index_dist > threshold and middle_dist > threshold and 
                ring_dist > threshold and pinky_dist > threshold)
    
    def _is_fist(self, thumb_dist, index_dist, middle_dist, ring_dist, pinky_dist) -> bool:
        """Check if gesture is a fist."""
        # All fingers closed
        threshold = 0.05
        return (index_dist < threshold and middle_dist < threshold and 
                ring_dist < threshold and pinky_dist < threshold)
    
    def _is_peace_sign(self, index_dist, middle_dist, ring_dist, pinky_dist) -> bool:
        """Check if gesture is a peace sign (V)."""
        # Index and middle extended, others closed
        extended_threshold = 0.1
        closed_threshold = 0.05
        
        return (index_dist > extended_threshold and middle_dist > extended_threshold and
                ring_dist < closed_threshold and pinky_dist < closed_threshold)
    
    def _is_thumbs_up(self, thumb_dist, index_dist, middle_dist, ring_dist, pinky_dist) -> bool:
        """Check if gesture is thumbs up."""
        # Thumb extended, others closed
        thumb_threshold = 0.1
        finger_threshold = 0.05
        
        return (thumb_dist > thumb_threshold and index_dist < finger_threshold and
                middle_dist < finger_threshold and ring_dist < finger_threshold and
                pinky_dist < finger_threshold)
    
    def _is_pointing(self, index_dist, middle_dist, ring_dist, pinky_dist) -> bool:
        """Check if gesture is pointing."""
        # Only index finger extended
        extended_threshold = 0.1
        closed_threshold = 0.05
        
        return (index_dist > extended_threshold and middle_dist < closed_threshold and
                ring_dist < closed_threshold and pinky_dist < closed_threshold)
    
    def _load_gesture_templates(self) -> Dict[str, np.ndarray]:
        """Load pre-defined gesture templates."""
        # This would load saved gesture templates from files
        # For now, return empty dict
        return {}
    
    def save_gesture_template(self, name: str, landmarks: np.ndarray):
        """Save a gesture template."""
        self.gesture_templates[name] = landmarks
        logger.info(f"Saved gesture template: {name}")
    
    def draw_landmarks(self, frame: np.ndarray, results) -> np.ndarray:
        """Draw hand landmarks on frame."""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
        return frame
    
    def cleanup(self):
        """Cleanup MediaPipe resources."""
        if hasattr(self, 'hands'):
            self.hands.close()
        logger.info("Gesture detector cleaned up")

