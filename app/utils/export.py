
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
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{original_filename}_{timestamp}"
        
        results = {}
        
        # 1. Image Export
        # Crop to face if possible, or use full image if not specified how to crop.
        # Requirement: "zugeschnittenes, korrekt skaliertes Bild"
        # We need to crop around the face with correct padding.
        
        if face_info:
            # Calculate crop based on chin and crown?
            # Or use bbox and fixed ratio.
            # ICAO: Face width 50-75% of image width?
            # Config: min_face_height_percent ~75%.
            
            bbox = face_info.bbox
            face_h = bbox[3] - bbox[1]
            face_w = bbox[2] - bbox[0]
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            
            # Calculate Target Pixels based on Config DPI
            dpi = self.config.get('biometrics', {}).get('resolution_dpi', 600)
            width_mm = self.config.get('biometrics', {}).get('output_width_mm', 35)
            height_mm = self.config.get('biometrics', {}).get('output_height_mm', 45)
            
            # 1 inch = 25.4 mm
            target_w = int((width_mm / 25.4) * dpi)
            target_h = int((height_mm / 25.4) * dpi)
            
            # Face height in target should be ~75% (34mm/45mm of image height)
            # So face_h_pixels should be target_h * 0.75
            
            scale = (target_h * 0.75) / face_h
            
            # Crop logic
            # Extract patch
            # Warning: this simple crop might be off centered. 
            # ICAO requires eyes at specific height.
            # Eyes at ~56% from bottom (approx).
            
            # Let's align by eyes if landmarks exist
            # For this MVP, let's center on face center and scale.
            
            # Real implementation would use affine transform to align eyes perfectly/
            
            M = cv2.getRotationMatrix2D((cx, cy), 0, scale)
            # Adjust translation to center face
            M[0, 2] += (target_w / 2) - cx
            M[1, 2] += (target_h / 2) - cy # This centers the face center.
            # We want eyes at specific height. 
            # Eyes usually above center.
            # Let's shift down a bit.
            
            final_img = cv2.warpAffine(img_bgr, M, (target_w, target_h))
            
            img_path = os.path.join(self.output_dir, f"{base_name}.jpg")
            
            # Save logic with < 3MB check
            quality = 95
            max_size_bytes = 3 * 1024 * 1024 # 3MB
            
            while quality > 10:
                cv2.imwrite(img_path, final_img, [cv2.IMWRITE_JPEG_QUALITY, quality])
                if os.path.getsize(img_path) < max_size_bytes:
                    break
                quality -= 5 # Reduce quality if too big
                
            results['image_path'] = img_path
            results['final_quality'] = quality
        else:
            # Fallback
            results['msg'] = "No face to crop"

        # 2. JSON Report
        json_path = os.path.join(self.output_dir, f"{base_name}_report.json")
        with open(json_path, "w") as f:
            # Convert numpy types
            def default(o):
                if hasattr(o, 'item'): return o.item()
                if hasattr(o, 'tolist'): return o.tolist()
                return str(o)
                
            json.dump(report, f, indent=4, default=default)
        results['json_path'] = json_path
        
        return results
