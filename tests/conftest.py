
import pytest
import numpy as np

@pytest.fixture
def mock_config():
    return {
        'biometrics': {
            'output_height_mm': 45,
            'face_height_min_mm': 30.0,
            'face_height_max_mm': 33.0,
            'min_eye_y_from_bottom_mm': 21.8,
            'max_eye_y_from_bottom_mm': 29.7,
            'max_center_deviation_mm': 2.5,
            'uniformity_min_score': 75.0
        },
        'thresholds': {
            'blur_min_score': 100.0,
            'exposure_min_hist': 0.2,
            'shadow_max_difference': 30,
            'uniformity_min_score': 75.0
        }
    }

@pytest.fixture
def mock_face():
    class Face:
        def __init__(self, bbox, kps):
            self.bbox = np.array(bbox) # x1, y1, x2, y2
            self.kps = np.array(kps)   # 5x2 landmarks
    return Face
