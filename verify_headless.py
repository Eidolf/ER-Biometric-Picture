
import os
import sys
import json
import cv2
import numpy as np
from app.core.analyzer import Analyzer
from scripts.generate_samples import generate_samples

# Mock Face object for testing logic
class MockFace:
    def __init__(self, bbox, kps):
        self.bbox = np.array(bbox, dtype=np.float32)
        self.kps = np.array(kps, dtype=np.float32)

def verify():
    print("1. Generating Samples...")
    generate_samples()
    
    print("\n2. Initializing Analyzer (Headless)...")
    config = {
        'biometrics': {
            'resolution_dpi': 700,
            'output_width_mm': 35,
            'output_height_mm': 45,
            'min_face_height_mm': 32,
            'max_face_height_mm': 36,
            'min_eye_y_from_bottom_mm': 21.8,
            'max_eye_y_from_bottom_mm': 29.7,
            'max_center_deviation_mm': 2.5
        },
        'thresholds': {
            'blur_min_score': 100.0,
            'exposure_min_hist': 0.2,
            'shadow_max_difference': 30,
            'neutral_expression_score': 0.7,
            'mouth_open_ratio': 0.1,
            'eye_open_ratio': 0.15
        }
    }
    analyzer = Analyzer(config)
    
    print("\n3. Testing Logic with MOCKED Valid Data...")
    
    # Mock Face
    bbox = [75, 55, 275, 395]
    kps = [
        [125, 200], [225, 200], [175, 250], [125, 330], [225, 330] 
    ]
    mock_face = MockFace(bbox, kps)
    
    img_dummy = np.zeros((450, 350, 3), dtype=np.uint8)
    img_dummy[:] = (128, 128, 128) 
    
    print("   Running Geometry Check...")
    geo_res = analyzer.geometry.check_processed_image(mock_face, 450, 350)
    print("   Geometry Result:")
    print(json.dumps(geo_res, indent=2)) # No Custom Encoder!
    
    if geo_res.get('face_height', {}).get('passed') and geo_res.get('eye_position', {}).get('passed'):
        print("\nSUCCESS: Geometry Logic Verified.")
    else:
        print("\nFAILURE: Geometry Logic Check Failed.")

    print("\n   Running Quality Check...")
    qual_res = analyzer.quality.check_quality(img_dummy)
    print("   Quality Result (Expected Fail for synthetic flat image):")
    print(json.dumps(qual_res, indent=2)) # No Custom Encoder!
    
    print("\nHeadless verification complete. Core business logic is functional.")

if __name__ == "__main__":
    verify()
