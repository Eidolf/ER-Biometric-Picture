
import cv2
import numpy as np

class ImageOptimizer:
    def __init__(self, config=None):
        self.config = config

    def optimize(self, img_bgr, face):
        """
        Deprecated: Use granular methods.
        """
        return self.optimize_background(img_bgr, face)

    def adjust_brightness(self, img_bgr, factor=1.0):
        """
        Adjust brightness/gamma.
        factor > 1.0: Brighter
        factor < 1.0: Darker
        """
        # Using Gamma correction for nicer results than linear addition
        # Reasonable range for factor: 0.5 to 1.5
        invGamma = 1.0 / factor
        table = np.array([((i / 255.0) ** invGamma) * 255
                          for i in np.arange(0, 256)]).astype("uint8")
        
        return cv2.LUT(img_bgr, table)

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
