
import os
import json
import cv2
from datetime import datetime

class Exporter:
    def __init__(self, config):
        self.config = config
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export(self, img_bgr, face_info, report, original_filename="capture"):
        """
        Export processed image, overlay (optional), and JSON report.
        Target: 35x45mm @ 600dpi -> 827x1063 px
        Uses INTER_LANCZOS4 for best quality and unsharp mask.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{original_filename}_{timestamp}"
        
        results = {}
        
        # 1. Image Export
        if face_info:
            bbox = face_info.bbox
            face_h = bbox[3] - bbox[1]
            face_w = bbox[2] - bbox[0]
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            
            # Calculate Target Pixels based on Config DPI
            dpi = self.config.get('biometrics', {}).get('resolution_dpi', 600)
            width_mm = self.config.get('biometrics', {}).get('output_width_mm', 35)
            height_mm = self.config.get('biometrics', {}).get('output_height_mm', 45)
            
            target_w = int((width_mm / 25.4) * dpi)
            target_h = int((height_mm / 25.4) * dpi)
            
            scale = (target_h * 0.75) / face_h
            
            M = cv2.getRotationMatrix2D((cx, cy), 0, scale)
            M[0, 2] += (target_w / 2) - cx
            M[1, 2] += (target_h / 2) - cy 
            
            # Use LANCZOS4 for high quality resizing
            final_img = cv2.warpAffine(img_bgr, M, (target_w, target_h), flags=cv2.INTER_LANCZOS4)
            
            # Apply Unsharp Mask (Sharpening)
            # Standard technique: Sharpened = Original + (Original - Blurred) * Amount
            gaussian_3 = cv2.GaussianBlur(final_img, (0, 0), 2.0)
            final_img = cv2.addWeighted(final_img, 1.5, gaussian_3, -0.5, 0)
            
            img_path = os.path.join(self.output_dir, f"{base_name}.jpg")
            
            self._save_compressed(img_path, final_img)
            results['image_path'] = img_path
        else:
            results['msg'] = "No face to crop"

        # 2. JSON Report
        self._save_report(report, base_name)
        results['json_path'] = os.path.join(self.output_dir, f"{base_name}_report.json")
        
        return results

    def save_exact_image(self, img_bgr, report, original_filename="capture"):
        """
        Saves the image exactly as provided (no re-cropping).
        Useful for manual crops.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{original_filename}_{timestamp}_manual"
        
        img_path = os.path.join(self.output_dir, f"{base_name}.jpg")
        self._save_compressed(img_path, img_bgr)
        
        self._save_report(report, base_name)
        
        return {'image_path': img_path}

    def _save_compressed(self, path, img):
        quality = 95
        max_size_bytes = 3 * 1024 * 1024 # 3MB
        
        while quality > 10:
            cv2.imwrite(path, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
            if os.path.getsize(path) < max_size_bytes:
                break
            quality -= 5

    def _save_report(self, report, base_name):
        json_path = os.path.join(self.output_dir, f"{base_name}_report.json")
        with open(json_path, "w") as f:
            def default(o):
                if hasattr(o, 'item'): return o.item()
                if hasattr(o, 'tolist'): return o.tolist()
                return str(o)
            json.dump(report, f, indent=4, default=default)
