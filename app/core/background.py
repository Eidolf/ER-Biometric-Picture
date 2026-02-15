
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
        
        # 2. Improved Heuristic: Flood Fill from corners
        # This assumes the top corners are definitely background.
        
        # Resize for speed and noise reduction
        scale = 0.5
        small_img = cv2.resize(img_bgr, (0,0), fx=scale, fy=scale)
        h_s, w_s = small_img.shape[:2]
        
        # Create a mask for floodFill (needs to be h+2, w+2)
        # 0 = Unfilled, 255 = Filled
        # NOTE: openCV floodFill mask needs to be uint8
        fill_mask = np.zeros((h_s+2, w_s+2), np.uint8)
        
        # Tolerance for color difference
        # If the background is truly uniform, variance is low.
        # But allow some lighting gradient.
        lo_diff = (8, 8, 8)
        up_diff = (8, 8, 8)
        
        # 4 connectivity, Fill Value 255, Mask Only, Fixed Range (compare to seed)
        flags = 4 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE
        
        # FloodFill from top-left and top-right (standard logical background spots)
        cv2.floodFill(small_img, fill_mask, (0, 0), 0, lo_diff, up_diff, flags)
        cv2.floodFill(small_img, fill_mask, (w_s-1, 0), 0, lo_diff, up_diff, flags)
        
        # Extract the actual mask (remove padding)
        final_mask_small = fill_mask[1:-1, 1:-1]
        
        # Resize back to original size
        mask = cv2.resize(final_mask_small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # Safety: ALWAYS exclude the face bbox (plus body below it) to prevent leaks into face
        x1, y1, x2, y2 = map(int, face_bbox)
        margin_x = int((x2 - x1) * 0.2)
        x1 = max(0, x1 - margin_x)
        x2 = min(w, x2 + margin_x)
        y1 = max(0, y1 - margin_x) # Top margin
        y2 = h # Exclude everything below face
        
        cv2.rectangle(mask, (x1, y1), (x2, y2), 0, -1)
        
        # Analyze Background region
        bg_pixels = img_bgr[mask == 255]
        
        if len(bg_pixels) == 0:
            return {'background': {'passed': False, 'msg': "Face covers entire image"}}, mask
            
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
             
        return results, mask
