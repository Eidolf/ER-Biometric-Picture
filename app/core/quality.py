
import cv2
import numpy as np

class QualityChecker:
    def __init__(self, config):
        self.config = config
        self.thresholds = config.get('thresholds', {})

    def check_quality(self, img_bgr):
        """
        Check technical quality of the image.
        """
        results = {}
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # 1. Blur Detection (Laplacian Variance)
        blur_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        min_blur = self.thresholds.get('blur_min_score', 100.0)
        
        if blur_var < min_blur:
            results['blur'] = {'passed': False, 'value': float(round(blur_var, 2)), 'msg': "Blurry"}
        else:
             results['blur'] = {'passed': True, 'value': float(round(blur_var, 2)), 'msg': "Sharp"}

        # 2. Exposure / Histogram
        # Simple check: is histogram spread okay?
        # Avoid over/underexposure
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        # Normalize
        hist_norm = hist / hist.sum()
        
        # Check extremes
        dark_ratio = np.sum(hist_norm[:20]) # Shadows
        bright_ratio = np.sum(hist_norm[230:]) # Highlights
        
        if dark_ratio > 0.5:
             results['exposure'] = {'passed': False, 'value': "Dark", 'msg': "Underexposed"}
        elif bright_ratio > 0.5:
             results['exposure'] = {'passed': False, 'value': "Bright", 'msg': "Overexposed"}
        else:
             results['exposure'] = {'passed': True, 'value': "OK", 'msg': "Good Exposure"}
             
        # 3. Contrast (Std Dev of gray)
        contrast = gray.std()
        if contrast < 30:
             results['contrast'] = {'passed': False, 'value': float(round(contrast, 2)), 'msg': "Low Contrast"}
        else:
             results['contrast'] = {'passed': True, 'value': float(round(contrast, 2)), 'msg': "OK"}
             
        # 4. Illumination / Shadows
        # Split image into left and right halves (approx) to check symmetry
        h, w = gray.shape
        left_half = gray[:, :w//2]
        right_half = gray[:, w//2:]
        
        mean_l = np.mean(left_half)
        mean_r = np.mean(right_half)
        diff = abs(mean_l - mean_r)
        
        max_diff = self.thresholds.get('shadow_max_difference', 30)
        
        if diff > max_diff:
             results['illumination'] = {'passed': False, 'value': f"Diff {diff:.1f}", 'msg': "Uneven lighting/Shadows"}
        else:
             results['illumination'] = {'passed': True, 'value': f"Diff {diff:.1f}", 'msg': "Even lighting"}

        return results
