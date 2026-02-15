
import numpy as np

class GeometryChecker:
    def __init__(self, config):
        self.config = config
        self.biometrics = config.get('biometrics', {})

    def check_processed_image(self, face, img_height, img_width):
        """
        Validate geometry on the FINAL processed/cropped image (assumed 35x45mm ratio).
        Input image is typically the full image, but calculations map to 35x45mm space.
        
        If we are checking a raw image, we simulate how it WOULD be cropped (centering on face).
        For strict BMI checking, we assume the face is centered horizontally.
        """
        results = {}
        
        # Landmarks: [LeftEye, RightEye, Nose, LeftMouth, RightMouth]
        kps = face.kps
        if kps is None or len(kps) < 5:
             results['meta'] = {'passed': False, 'msg': "Landmarks missing"}
             return results

        left_eye = kps[0]
        right_eye = kps[1]
        nose = kps[2]
        mouth_l = kps[3]
        mouth_r = kps[4]
        
        # Scaling factor: We assume the image IS 35mm x 45mm for these checks,
        # or we project pixel dimensions to mm based on image height = 45mm.
        px_to_mm = 45.0 / img_height
        
        # 1. Face Height (Chin to Top of Head).
        # Approximating "Crown" is hard without full mesh. 
        # Using bbox often includes forehead. 
        # Metric: Bounding box height is a decent proxy for Chin-Crown if detection is tight.
        # Alternatively: Chin to Eye + Eye to Crown (Eye to Crown approx 1.618 * Eye to Chin?)
        # Let's use bbox height for now, but strict BMI requires "Chin line to Crown".
        
        face_h_px = face.bbox[3] - face.bbox[1]
        face_h_mm = face_h_px * px_to_mm
        
        # Use new keys matching config.yaml
        min_h = self.biometrics.get('face_height_min_mm', 30.0) 
        max_h = self.biometrics.get('face_height_max_mm', 36.0)
        
        # BMI Step 2: Face Size
        if min_h <= face_h_mm <= max_h:
            results['face_height'] = {'passed': True, 'value': f"{face_h_mm:.1f}mm", 'msg': f"OK ({min_h}-{max_h}mm)"}
        else:
            results['face_height'] = {'passed': False, 'value': f"{face_h_mm:.1f}mm", 
                                      'msg': f"Height must be {min_h}-{max_h}mm"}

        # 2. Eye Position (Step 1: Augenbereich)
        # Eyes must be in gray area.
        # Height from bottom.
        # Average eye Y.
        avg_eye_y = (left_eye[1] + right_eye[1]) / 2
        eye_y_from_bottom_px = img_height - avg_eye_y
        eye_y_from_bottom_mm = eye_y_from_bottom_px * px_to_mm
        
        min_eye = self.biometrics.get('min_eye_y_from_bottom_mm', 21.8)
        max_eye = self.biometrics.get('max_eye_y_from_bottom_mm', 29.7)
        
        if min_eye <= eye_y_from_bottom_mm <= max_eye:
             results['eye_position'] = {'passed': True, 'value': f"{eye_y_from_bottom_mm:.1f}mm", 'msg': "OK (In Zone)"}
        else:
             results['eye_position'] = {'passed': False, 'value': f"{eye_y_from_bottom_mm:.1f}mm", 
                                        'msg': f"Eyes outside zone ({min_eye}-{max_eye}mm)"}

        # 3. Eyes Level (Waagerecht) - "Augen auf gleicher Höhe"
        eye_diff_y = abs(left_eye[1] - right_eye[1])
        eye_diff_mm = eye_diff_y * px_to_mm
        if eye_diff_mm < 1.0: # 1mm tolerance
             results['eyes_level'] = {'passed': True, 'value': f"{eye_diff_mm:.1f}mm", 'msg': "Level"}
        else:
             results['eyes_level'] = {'passed': False, 'value': f"{eye_diff_mm:.1f}mm", 'msg': "Tilted"}

        # 4. Nose Center (Nasenmitte im Bereich)
        # Should be horizontally centered.
        img_center_x = img_width / 2
        nose_dist_x = abs(nose[0] - img_center_x)
        nose_dist_mm = nose_dist_x * px_to_mm
        
        max_dev = self.biometrics.get('max_center_deviation_mm', 2.5)
        
        if nose_dist_mm <= max_dev:
             results['nose_center'] = {'passed': True, 'value': f"{nose_dist_mm:.1f}mm", 'msg': "Centered"}
        else:
             results['nose_center'] = {'passed': False, 'value': f"{nose_dist_mm:.1f}mm", 'msg': "Off-center"}

        # 5. Head Roll (Kopfhaltung gerade)
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        angle = np.degrees(np.arctan2(dy, dx))
        if abs(angle) < 5:
            results['roll'] = {'passed': True, 'value': f"{angle:.1f}°", 'msg': "Straight"}
        else:
             results['roll'] = {'passed': False, 'value': f"{angle:.1f}°", 'msg': "Tilted"}
             
        # 6. Mouth Closed
        # Simple heuristic: distance between lips.
        # kps[3] (L mouth), kps[4] (R mouth).
        # We need landmarks for inner lips to be accurate, but 5-point only gives corners.
        # Fallback: We cannot strictly check "Mouth Closed" with 5 landmarks reliably.
        # But we can check if mouth is "smiling" or "open" via aspect ratio if we had 68 pts.
        # With 5 pts, we can't do much check except maybe relative position to nose.
        # We will assume "Optional" or "Check visually" if model is limited.
        # FOR NOW: Skip automatic check or assume Pass, mark as Manual Check.
        results['mouth_closed'] = {'passed': True, 'value': "Manual", 'msg': "Verify manually"}

        return results
