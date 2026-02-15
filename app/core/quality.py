
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
        # 1. Calc std dev of background pixels
        mean, stddev = cv2.meanStdDev(gray, mask=bg_mask_binary)
        std_val = stddev[0][0]
        
        # Score: 100 - std_val
        # User reported ~80.39 -> StdDev ~19.6
        # Slight shadows/gradients cause this.
        score = max(0, 100 - std_val)
        
        threshold = self.config.get('thresholds', {}).get('uniformity_min_score', 75.0)
        
        if score >= threshold:
            results['uniformity'] = {'passed': True, 'value': f"{score:.1f}", 'msg': "Uniform"}
        else:
            results['uniformity'] = {'passed': False, 'value': f"{score:.1f}", 
                                     'msg': f"Uneven background (StdDev: {std_val:.1f})"}

        return results
