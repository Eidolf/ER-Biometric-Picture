
import cv2
import numpy as np

class BackgroundChecker:
    def __init__(self, config):
        self.config = config
        # Assuming segmenter is initialized elsewhere or passed in config
        self.segmenter = None # Placeholder for a segmentation model

    def check_background(self, img_bgr, face_bbox):
        """
        Check if background is uniform/light enough.
        Returns (results, mask).
        """
        results = {}
        
        # 1. Simple color check on corners?
        # Or use the segmentation model if available.
        mask = None
        # Placeholder for future segmentation model usage
        h, w = img_bgr.shape[:2]
        
        # Create a mask for the background (outside face box + margin)
        mask = np.ones((h, w), dtype=np.uint8) * 255
        
        # Mask out the face
        x1, y1, x2, y2 = map(int, face_bbox)
        margin = int((x2 - x1) * 0.2)
        x1 = max(0, x1 - margin)
        x2 = min(w, x2 + margin)
        y1 = max(0, y1 - margin)
        y2 = min(h, y2 + margin)
        
        cv2.rectangle(mask, (x1, y1), (x2, y2), 0, -1)
        
        # Analyze Background region
        bg_pixels = img_bgr[mask == 255]
        
        if len(bg_pixels) == 0:
            return {'background': {'passed': False, 'msg': "Face covers entire image"}}
            
        std_dev = np.std(bg_pixels, axis=0) # Per channel std
        mean_val = np.mean(bg_pixels, axis=0)
        
        # Check uniformity
        max_std = np.max(std_dev)
        if max_std > 40: # Threshold for uniformity
             results['uniformity'] = {
                 'passed': False, 
                 'value': round(max_std, 2), 
                 'msg': "Uneven (shadows/texture). Use empty white wall."
             }
        else:
             results['uniformity'] = {'passed': True, 'value': round(max_std, 2), 'msg': "Uniform"}

        # Check brightness (Light gray/White)
        # BGR -> Mean should be high
        brightness = np.mean(mean_val)
        if brightness < 150:
             results['brightness'] = {
                 'passed': False, 
                 'value': round(brightness, 2), 
                 'msg': "Too dark. Need better light."
             }
        else:
             results['brightness'] = {'passed': True, 'value': round(brightness, 2), 'msg': "OK"}
             
        return results
