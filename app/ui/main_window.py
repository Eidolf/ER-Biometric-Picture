
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QMessageBox, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap

from app.ui.camera_widget import CameraWidget
from app.ui.overlay_widget import OverlayWidget
from app.ui.result_widget import ResultWidget
from app.core.analyzer import Analyzer
from app.core.optimizer import ImageOptimizer
from app.utils.export import Exporter
from app.ui.cropper import InteractiveCropper

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.analyzer = None # Lazy load or init in background to show UI fast?
        self.optimizer = ImageOptimizer(config)
        self.exporter = Exporter(config)
        self.current_face = None
        self.current_report = None
        self.current_image = None
        # Init analyzer here for now
        self.setWindowTitle(config.get("app", {}).get("name", "PassPhotoCheck"))
        self.resize(1200, 800)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Stack for different views
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        # 1. Capture View
        self.capture_container = QWidget()
        self.capture_layout = QVBoxLayout(self.capture_container)
        
        self.camera_widget = CameraWidget()
        self.capture_layout.addWidget(self.camera_widget)
        
        # Overlay on top of camera?
        # To do this properly, OverlayWidget needs to be child of CameraWidget's label or distinct.
        # For simplicity, let's put it in a separate layout or rely on CameraWidget to show it?
        # Better: CameraWidget emits image, we show it in "Review" stage with overlay?
        # Or real-time overlay.
        # Let's add overlay to camera widget via simple parenting if possible or just draw on frame.
        # For now: Capture -> simple view -> Analyze.
        
        self.camera_widget.image_captured_signal.connect(self.on_image_captured)
        
        self.stack.addWidget(self.capture_container)
        
        # 2. Review/Analyze View
        self.review_container = QWidget()
        self.review_layout = QHBoxLayout(self.review_container)
        
        # Left Side: Stack (Preview Label OR Cropper)
        self.review_stack = QStackedWidget()
        self.review_layout.addWidget(self.review_stack, 1)
        
        # Page 0: Preview Label
        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.review_stack.addWidget(self.preview_label)
        
        # Page 1: Cropper
        self.cropper = InteractiveCropper()
        self.review_stack.addWidget(self.cropper)
        
        self.result_widget = ResultWidget()
        self.result_widget.btn_export.clicked.connect(self.export_results)
        
        # Connect Optimization Buttons
        self.result_widget.btn_brighten.clicked.connect(lambda: self.adjust_brightness(1.1))
        self.result_widget.btn_darken.clicked.connect(lambda: self.adjust_brightness(0.9))
        self.result_widget.btn_fix_bg.clicked.connect(self.optimize_background)
        self.result_widget.btn_undo.clicked.connect(self.reset_image)
        
        # Connect Crop Button
        self.result_widget.btn_crop.clicked.connect(self.toggle_crop_mode)
        
        self.review_layout.addWidget(self.result_widget, 1)
        
        # Back button
        self.btn_back = QPushButton("Back to Camera")
        self.btn_back.clicked.connect(self.reset_to_camera)
        self.review_layout.addWidget(self.btn_back)
        
        self.stack.addWidget(self.review_container)
        
        # Initialize Analyzer
        # TODO: Move to thread to avoid freezing startup
        self.init_analyzer()
        
        # Show Disclaimer
        QTimer.singleShot(100, self.show_disclaimer)

    def show_disclaimer(self):
        msg = (
            "WICHTIGER HINWEIS:\n\n"
            "Diese Anwendung dient nur zur VORPRÜFUNG von Passbildern.\n"
            "Seit Mai 2025 sind für deutsche Ausweise ausschließlich digitale, "
            "behördlich zertifizierte eFotos zulässig.\n\n"
            "Diese App ersetzt NICHT den offiziellen eFoto-Prozess!"
        )
        QMessageBox.warning(self, "Rechtlicher Hinweis (DE)", msg)

    def init_analyzer(self):
        try:
            self.analyzer = Analyzer(self.config)
        except Exception as e:
            QMessageBox.critical(self, "Init Error", f"Failed to initialize AI models: {e}")

    def on_image_captured(self, img_bgr):
        self.current_image = img_bgr
        self.original_capture = img_bgr.copy() # Store original for undo
        self.stack.setCurrentWidget(self.review_container)
        
        # Show image
        self.show_image_in_label(img_bgr, self.preview_label)
        
        # Run Analysis
        if self.analyzer:
            report, face = self.analyzer.analyze(img_bgr)
            self.current_face = face
            self.current_report = report
            self.result_widget.update_results(report)
            
            # Draw Face Box on preview for feedback
            if face:
                import cv2
                box = face.bbox.astype(int)
                img_copy = img_bgr.copy()
                cv2.rectangle(img_copy, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
                # Draw landmarks
                if face.kps is not None:
                    for p in face.kps:
                        cv2.circle(img_copy, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)
                        
                self.show_image_in_label(img_copy, self.preview_label)

    def show_image_in_label(self, img_bgr, label):
        import cv2
        from PySide6.QtGui import QImage, QPixmap
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        
        # Scale
        lbl_w = label.width()
        lbl_h = label.height()
        scale = min(lbl_w / w, lbl_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        img_resized = cv2.resize(img_rgb, (new_w, new_h))
        qimg = QImage(img_resized.data, new_w, new_h, new_w * ch, QImage.Format_RGB888)
        label.setPixmap(QPixmap.fromImage(qimg))

    def reset_to_camera(self):
        self.stack.setCurrentWidget(self.capture_container)
        self.camera_widget.start_camera()

    def adjust_brightness(self, factor):
        if self.current_image is None: return
        self.current_image = self.optimizer.adjust_brightness(self.current_image, factor)
        self.rerun_analysis()
        
    def optimize_background(self):
        if self.current_image is None or self.current_face is None: return
        # Background fix logic
        # We use singleShot to allow UI to breathe or show loading if we had one
        QTimer.singleShot(50, lambda: self._run_bg_fix())

    def _run_bg_fix(self):
        self.current_image = self.optimizer.optimize_background(self.current_image, self.current_face)
        self.rerun_analysis()
        
    def reset_image(self):
        if hasattr(self, 'original_capture') and self.original_capture is not None:
            self.current_image = self.original_capture.copy()
            self.rerun_analysis()
            
    def rerun_analysis(self):
        # Show Image
        self.show_image_in_label(self.current_image, self.preview_label)
        
        # Re-Run Analysis
        if self.analyzer:
            report, face = self.analyzer.analyze(self.current_image)
            # Only update current_face if we found one, otherwise keep old or strict?
            # Actually if we adjust brightness, face detection should still work, maybe better.
            if face:
                 self.current_face = face
            self.current_report = report
            self.result_widget.update_results(report)
            
            # Draw Face Box on preview for feedback
            face_to_draw = face if face else self.current_face
            
            if face_to_draw:
                import cv2
                box = face_to_draw.bbox.astype(int)
                img_copy = self.current_image.copy()
                cv2.rectangle(img_copy, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
                # Draw landmarks
                if face_to_draw.kps is not None:
                    for p in face_to_draw.kps:
                        cv2.circle(img_copy, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)
                        
                self.show_image_in_label(img_copy, self.preview_label)

    def export_results(self):
        if self.current_image is not None and self.current_report is not None:
             res = self.exporter.export(self.current_image, self.current_face, self.current_report)
             if 'image_path' in res:
                 QMessageBox.information(self, "Export Successful", f"Saved to {res['image_path']}")
             else:
                 QMessageBox.warning(self, "Export Partial", f"Saved report but could not crop image: {res.get('msg')}")
        else:
             QMessageBox.warning(self, "Export Failed", "No analyis data to export.")
