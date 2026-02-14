
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
        """
        Uses GrabCut with strict mask initialization to protect dark clothing.
        """
        h, w = img.shape[:2]
        mask = np.zeros((h, w), np.uint8)
        
        # 0. Initialize Layout
        # GrabCut constants:
        # 0 = GC_BGD (Sure Background)
        # 1 = GC_FGD (Sure Foreground)
        # 2 = GC_PR_BGD (Probable Background)
        # 3 = GC_PR_FGD (Probable Foreground)
        
        # Default to Probable Background
        mask[:] = cv2.GC_PR_BGD
        
        # 1. Define "Sure Background" (Edges)
        # Top corners are usually background
        margin_w = int(w * 0.1)
        margin_h = int(h * 0.1)
        cv2.rectangle(mask, (0, 0), (margin_w, margin_h), cv2.GC_BGD, -1) # Top-Left
        cv2.rectangle(mask, (w - margin_w, 0), (w, margin_h), cv2.GC_BGD, -1) # Top-Right
        
        # Top strip (exclude head area if face is high?)
        # Let's trust corners more.
        
        # 2. Define "Sure Foreground" (Face)
        box = face.bbox.astype(int)
        x1, y1, x2, y2 = box
        
        # Face ellipse as SURE Foreground
        face_center = ((x1 + x2) // 2, (y1 + y2) // 2)
        face_size = ((x2 - x1) // 2, (y2 - y1) // 2)
        cv2.ellipse(mask, face_center, face_size, 0, 0, 360, cv2.GC_FGD, -1)
        
        # 3. Define "Probable Foreground" (Torso/Body)
        # We assume the body is below the face approx width of face * 1.5
        fw = x2 - x1
        body_x1 = max(0, x1 - int(fw * 0.5))
        body_x2 = min(w, x2 + int(fw * 0.5))
        body_y1 = y2 # Chin
        body_y2 = h  # Bottom of image
        
        # Important: Mark the CENTRAL STRIP of the body as SURE Foreground
        # This forces GrabCut to keep the center of the t-shirt, expanding out to similar colors.
        core_w = int(fw * 0.4)
        core_x1 = face_center[0] - core_w // 2
        core_x2 = face_center[0] + core_w // 2
        
        # But ensure we don't go out of bounds or into background if neck is thin?
        # Usually safe for passport photos (shoulders visible).
        cv2.rectangle(mask, (core_x1, body_y1), (core_x2, body_y2), cv2.GC_FGD, -1)

        # The wider area is Probable Foreground
        # (Already implicit if default is PR_FGD? No default is PR_BGD)
        # Let's set the wider body box as PR_FGD
        cv2.rectangle(mask, (body_x1, body_y1), (body_x2, body_y2), cv2.GC_PR_FGD, -1)

        # 4. Run GrabCut
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        
        try:
            cv2.grabCut(img, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)
        except Exception:
            return img
        
        # 5. Create Final Mask
        # Pixels 0 and 2 are background
        mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
        
        # 6. Apply White Background
        white_bg = np.ones_like(img, dtype=np.uint8) * 255
        img_fg = img * mask2[:, :, np.newaxis]
        bg_part = white_bg * (1 - mask2[:, :, np.newaxis])
        
        final = cv2.add(img_fg, bg_part)
        return final
