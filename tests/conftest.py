
import pytest
import numpy as np

@pytest.fixture
def mock_config():
    return {
        'biometrics': {
            'output_height_mm': 45,
            'min_face_height_percent': 70,
            'max_face_height_percent': 80,
            'eye_line_min_percent': 45,
            'eye_line_max_percent': 65
        },
        'thresholds': {
            'blur_min_score': 100.0,
            'exposure_min_hist': 0.2,
            'shadow_max_difference': 30
        }
    }

@pytest.fixture
def mock_face():
    class Face:
        def __init__(self, bbox, kps):
            self.bbox = np.array(bbox) # x1, y1, x2, y2
            self.kps = np.array(kps)   # 5x2 landmarks
    return Face
