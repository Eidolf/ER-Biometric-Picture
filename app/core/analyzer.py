
from app.core.face_detection import FaceDetector
from app.core.geometry import GeometryChecker
from app.core.quality import QualityChecker
from app.core.background import BackgroundChecker

class Analyzer:
    def __init__(self, config):
        self.config = config
        self.detector = FaceDetector()
        self.geometry = GeometryChecker(config)
        self.quality = QualityChecker(config)
        self.background = BackgroundChecker(config)
        
    def analyze(self, img_bgr):
        """
        Run all checks on the image.
        """
        report = {}
        
        try:
            # 1. Face Detection
            faces, _ = self.detector.detect_faces(img_bgr)
            
            if len(faces) == 0:
                report['meta'] = {'passed': False, 'msg': "No face detected"}
                return report, None
            elif len(faces) > 1:
                report['meta'] = {'passed': False, 'msg': "Multiple faces detected"}
                # We could select the largest face, but strict adherence says one person.
                # For now, pick largest.
                faces = sorted(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]), reverse=True)
                report['meta'] = {'passed': False, 'msg': "Multiple faces, analyzing largest"}
            else:
                report['meta'] = {'passed': True, 'msg': "One face detected"}
                
            face = faces[0]
            report['face_bbox'] = face.bbox.tolist()
            
            # 2. Background Checks
            # Returns results AND an optional mask (if it generated one)
            bg_res, bg_mask = self.background.check_background(img_bgr, face.bbox)
            report.update(bg_res)
            
            # 3. Quality Checks (Global)
            # Pass the mask from background check to quality check for better uniformity
            quality_res = self.quality.check_quality(img_bgr, bg_mask=bg_mask)
            report.update(quality_res)
            
            # 4. Geometry Checks
            h, w = img_bgr.shape[:2]
            geo_res = self.geometry.check_processed_image(face, h, w)
            report.update(geo_res)
            
            # Determine overall Pass/Fail
            failed = [k for k, v in report.items() if isinstance(v, dict) and not v.get('passed', True)]
            report['is_passed'] = len(failed) == 0
            
            return report, face
            
        except Exception as e:
            # Catch-all for analysis errors to prevent UI from showing nothing
            print(f"ERROR in Analyzer: {e}")
            import traceback
            traceback.print_exc()
            report['meta'] = {'passed': False, 'msg': f"Analysis Crash: {str(e)}"}
            return report, None
