
import cv2
import numpy as np

class ImageOptimizer:
    def __init__(self, config=None):
        self.config = config

    def optimize(self, img_bgr, face):
        """
        Optimize the image:
        1. Auto-Brightness/Contrast correction.
        2. Background removal/whitening (using GrabCut initialized by face bbox).
        """
        # 1. Brightness / Contrast (CLAHE on LAB Lightness)
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l_opt = clahe.apply(l)
        
        # Merge back
        lab_opt = cv2.merge((l_opt, a, b))
        img_opt = cv2.cvtColor(lab_opt, cv2.COLOR_LAB2BGR)
        
        # 2. Background Optimization (GrabCut)
        if face:
            img_opt = self.optimize_background(img_opt, face)
            
        return img_opt

    def optimize_background(self, img, face):
        # Use GrabCut
        mask = np.zeros(img.shape[:2], np.uint8)
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        
        # Define Rect: Face Box expanded
        h, w = img.shape[:2]
        box = face.bbox.astype(int)
        
        # Expand box to include hair/neck (roughly)
        x1, y1, x2, y2 = box
        
        # Margin: Head width * 0.5?
        fw = x2 - x1
        fh = y2 - y1
        
        rec_x1 = max(0, x1 - int(fw * 0.3))
        rec_x2 = min(w, x2 + int(fw * 0.3))
        rec_y1 = max(0, y1 - int(fh * 0.4)) # Above head
        rec_y2 = min(h, y2 + int(fh * 0.8)) # Neck/Shoulders
        
        rect = (rec_x1, rec_y1, rec_x2 - rec_x1, rec_y2 - rec_y1)
        
        try:
            cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 3, cv2.GC_INIT_WITH_RECT)
        except Exception:
            # Fallback if grabcut fails
            return img
        
        # Mask: 0=BG, 1=FG, 2=Prob_BG, 3=Prob_FG
        # We want FG+ProbFG
        mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
        
        # Create white background
        white_bg = np.ones_like(img, dtype=np.uint8) * 255
        
        # Combine: Keep FG from img, put White on BG
        # mask2 is 1 for FG.
        img_fg = img * mask2[:, :, np.newaxis]
        bg_part = white_bg * (1 - mask2[:, :, np.newaxis])
        
        final = cv2.add(img_fg, bg_part)
        return final
