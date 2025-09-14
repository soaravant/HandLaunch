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
            # Improved classification using correct MediaPipe indices and relative distances
            # MediaPipe landmark indices: 0-wrist, 4/8/12/16/20 tips, 6/10/14/18 PIPs, 5/9/13/17 MCPs

            def lm(idx: int) -> np.ndarray:
                s = idx * 3
                return landmarks[s:s+3]

            wrist = lm(0)
            thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip = lm(4), lm(8), lm(12), lm(16), lm(20)
            index_pip, middle_pip, ring_pip, pinky_pip = lm(6), lm(10), lm(14), lm(18)
            index_mcp, middle_mcp, ring_mcp, pinky_mcp = lm(5), lm(9), lm(13), lm(17)

            # Use palm size as scale (wrist to middle_mcp)
            scale = np.linalg.norm(middle_mcp - wrist)
            if scale < 1e-6:
                scale = 1.0

            # Distances to wrist
            thumb_dist = np.linalg.norm(thumb_tip - wrist)
            index_dist = np.linalg.norm(index_tip - wrist)
            middle_dist = np.linalg.norm(middle_tip - wrist)
            ring_dist = np.linalg.norm(ring_tip - wrist)
            pinky_dist = np.linalg.norm(pinky_tip - wrist)

            # PIP distances to wrist for relative extension
            index_pip_dist = np.linalg.norm(index_pip - wrist)
            middle_pip_dist = np.linalg.norm(middle_pip - wrist)
            ring_pip_dist = np.linalg.norm(ring_pip - wrist)
            pinky_pip_dist = np.linalg.norm(pinky_pip - wrist)

            # Consider a finger extended if the tip is significantly further than its PIP
            # The margin is relative to palm size for scale invariance
            margin = 0.35 * scale
            index_ext = (index_dist - index_pip_dist) > margin
            middle_ext = (middle_dist - middle_pip_dist) > margin
            ring_ext = (ring_dist - ring_pip_dist) > margin
            pinky_ext = (pinky_dist - pinky_pip_dist) > margin
            # Thumb: compare tip to wrist versus middle_mcp to wrist
            thumb_ext = (thumb_dist - np.linalg.norm(middle_mcp - wrist)) > (0.15 * scale)

            # Compute simple confidence as proportion of criteria satisfied
            def confidence_from_bools(vals: list) -> float:
                return sum(1 for v in vals if v) / max(1, len(vals))

            # Order: specific gestures first, open palm last
            if not (index_ext or middle_ext or ring_ext or pinky_ext or thumb_ext):
                return "fist", 0.9
            if thumb_ext and not (index_ext or middle_ext or ring_ext or pinky_ext):
                return "thumbs_up", confidence_from_bools([thumb_ext])
            if index_ext and not (middle_ext or ring_ext or pinky_ext):
                return "pointing", confidence_from_bools([index_ext, not middle_ext, not ring_ext, not pinky_ext])
            if index_ext and middle_ext and not ring_ext and not pinky_ext:
                return "peace_sign", confidence_from_bools([index_ext, middle_ext, not ring_ext, not pinky_ext])
            if thumb_ext and index_ext and middle_ext and ring_ext and pinky_ext:
                return "open_palm", 0.9
            
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

