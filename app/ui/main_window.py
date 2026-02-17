
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QMessageBox, QLabel, QProgressDialog
from PySide6.QtCore import Qt, QTimer, QThread
from PySide6.QtGui import QIcon, QPixmap

from app.ui.camera_widget import CameraWidget
from app.ui.overlay_widget import OverlayWidget
from app.ui.result_widget import ResultWidget
# Analyzer imported lazily in workers or later
from app.core.optimizer import ImageOptimizer
from app.utils.export import Exporter
from app.ui.cropper import InteractiveCropper
from app.ui.workers import InitWorker, AnalysisWorker

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.analyzer = None 
        self.optimizer = ImageOptimizer(config)
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
        self.result_widget.btn_export_exact.clicked.connect(self.export_exact_results)
        
        # Connect Optimization Buttons
        self.result_widget.btn_brighten.clicked.connect(lambda: self.adjust_brightness(1.1))
        self.result_widget.btn_darken.clicked.connect(lambda: self.adjust_brightness(0.9))
        self.result_widget.btn_fix_bg.clicked.connect(self.optimize_background)
        self.result_widget.btn_undo.clicked.connect(self.reset_image)
        
        # Connect Crop Button
        self.result_widget.btn_crop.clicked.connect(self.toggle_crop_mode)
        self.result_widget.slider_zoom.valueChanged.connect(self.on_zoom_slider)
        self.result_widget.btn_zoom_in.clicked.connect(lambda: self.step_zoom(1))
        self.result_widget.btn_zoom_out.clicked.connect(lambda: self.step_zoom(-1))
        
        # Connect Cropper Callback
        self.cropper.zoom_changed_callback = self.update_zoom_slider
        
        self.review_layout.addWidget(self.result_widget, 1)
        
        # Navigation Buttons
        nav_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("📂 Upload New")
        self.btn_load.setToolTip("Open a new image file")
        self.btn_load.clicked.connect(self.load_new_file)
        nav_layout.addWidget(self.btn_load)
        
        self.btn_back = QPushButton("📷 Back to Camera")
        self.btn_back.clicked.connect(self.reset_to_camera)
        nav_layout.addWidget(self.btn_back)
        
        self.review_layout.addLayout(nav_layout)
        
        self.stack.addWidget(self.review_container)
        
        # Initialize Analyzer in Background
        self.start_init_thread()
        
        # Show Disclaimer
        QTimer.singleShot(100, self.show_disclaimer)

    def start_init_thread(self):
        # Create Thread
        self.init_thread = QThread()
        self.init_worker = InitWorker(self)
        self.init_worker.moveToThread(self.init_thread)
        
        # Connect signals
        self.init_thread.started.connect(self.init_worker.run)
        self.init_worker.finished.connect(self.on_init_finished)
        self.init_worker.finished.connect(self.init_thread.quit)
        self.init_worker.finished.connect(self.init_worker.deleteLater)
        self.init_thread.finished.connect(self.init_thread.deleteLater)
        self.init_worker.error.connect(self.on_init_error)
        
        # Start
        self.init_thread.start()
        
        # Show splash/loading status in StatusBar
        self.statusBar().showMessage("Initializing AI Models... Please wait.")

    def on_init_finished(self):
        self.statusBar().showMessage("Ready", 5000)

    def on_init_error(self, err):
        self.statusBar().showMessage(f"Error initializing AI: {err}")
        QMessageBox.critical(self, "Init Error", f"Failed to initialize AI models: {err}")

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
        # Legacy method kept for interface safety but unused if threaded
        pass
        
    def on_image_captured(self, img_bgr):
        self.current_image = img_bgr
        self.original_capture = img_bgr.copy() # Store original for undo
        self.stack.setCurrentWidget(self.review_container)
        
        # Show image immediately
        self.show_image_in_label(img_bgr, self.preview_label)
        
        if not self.analyzer:
            QMessageBox.warning(self, "Not Ready", "AI Models are still loading. Please wait a moment.")
            return

        # Run Analysis in Background
        self.run_analysis_thread(img_bgr)

    def run_analysis_thread(self, img_bgr):
        # Show Progress
        self.progress_dialog = QProgressDialog("Analyzing image...", None, 0, 0, self) # No cancel button
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()
        
        # Create Thread
        self.analysis_thread = QThread()
        self.analysis_worker = AnalysisWorker(self.analyzer, img_bgr)
        self.analysis_worker.moveToThread(self.analysis_thread)
        
        # Connect signals
        self.analysis_thread.started.connect(self.analysis_worker.run)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        self.analysis_worker.finished.connect(self.analysis_thread.quit)
        self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)
        self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)
        self.analysis_worker.error.connect(self.on_analysis_error)
        
        # Start
        self.analysis_thread.start()

    def on_analysis_finished(self, report, face):
        if self.progress_dialog:
            self.progress_dialog.close()
            
        self.current_face = face
        self.current_report = report
        self.result_widget.update_results(report)
        
        # Draw Face Box on preview
        self.draw_face_overlay(face)

    def on_analysis_error(self, err):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Analysis Error", f"An error occurred: {err}")

    def draw_face_overlay(self, face):
        if not face: return
        import cv2
        img_copy = self.current_image.copy()
        box = face.bbox.astype(int)
        cv2.rectangle(img_copy, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        
        # Label
        label_text = "Detected Face"
        (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        # Background strip
        cv2.rectangle(img_copy, (box[0], box[1] - 25), (box[0] + w + 10, box[1]), (0, 255, 0), -1)
        # Text
        cv2.putText(img_copy, label_text, (box[0] + 5, box[1] - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2) # Black text

        # Draw landmarks
        if face.kps is not None:
            for p in face.kps:
                cv2.circle(img_copy, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)
                
        self.show_image_in_label(img_copy, self.preview_label)

    def step_zoom(self, delta):
        val = self.result_widget.slider_zoom.value()
        self.result_widget.slider_zoom.setValue(val + delta)

    def on_zoom_slider(self, val):
        self.cropper.set_zoom(val)
        self.result_widget.lbl_zoom_val.setText(f"{val}%")
        
    def update_zoom_slider(self, val):
        self.result_widget.slider_zoom.blockSignals(True)
        self.result_widget.slider_zoom.setValue(val)
        self.result_widget.slider_zoom.blockSignals(False)
        self.result_widget.lbl_zoom_val.setText(f"{val}%")

    def toggle_crop_mode(self, checked):
        if self.current_image is None:
            if checked:
                # Reset button state if no image
                self.result_widget.btn_crop.setChecked(False)
                QMessageBox.warning(self, "No Image", "Please capture or load an image first.")
            return

        if checked:
            # Enter Crop Mode
            self.cropper.set_image(self.current_image)
            self.review_stack.setCurrentWidget(self.cropper)
            self.result_widget.btn_crop.setText("✅ Apply Crop")
            
            # Disable other buttons?
            self.result_widget.btn_export.setEnabled(False)
            self.result_widget.btn_export_exact.setEnabled(False)
            # self.result_widget.btn_optimize.setEnabled(False) 
            self.result_widget.btn_fix_bg.setEnabled(False)
            self.result_widget.btn_darken.setEnabled(False)
            self.result_widget.btn_brighten.setEnabled(False)
            self.result_widget.btn_undo.setEnabled(False)
            self.result_widget.zoom_group.show()
        else:
            # Apply Crop
            self.apply_crop()
            self.review_stack.setCurrentWidget(self.preview_label)
            self.result_widget.btn_crop.setText("✂️ Adjust Crop")
            
            self.result_widget.zoom_group.hide()
            self.result_widget.btn_export.setEnabled(True)
            self.result_widget.btn_export_exact.setEnabled(True)
            # self.result_widget.btn_optimize.setEnabled(True)
            self.result_widget.btn_fix_bg.setEnabled(True)
            self.result_widget.btn_darken.setEnabled(True)
            self.result_widget.btn_brighten.setEnabled(True)
            self.result_widget.btn_undo.setEnabled(True)

    def apply_crop(self):
        # Get crop logic
        rect = self.cropper.get_current_crop() # QRectF in image coords
        if rect:
            x = int(rect.x())
            y = int(rect.y())
            w = int(rect.width())
            h = int(rect.height())
            
            if w > 10 and h > 10:
                import cv2
                # Warping to handle out-of-bounds seamlessly
                center = (x + w/2, y + h/2)
                # We simply want to extract this rectangle.
                # getRectSubPix is good but expects center.
                
                # Let's use getRectSubPix which handles float coords and padding
                cropped = cv2.getRectSubPix(self.current_image, (w, h), center)
                
                self.current_image = cropped
                
                # Rerun analysis
                self.rerun_analysis()

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
                
                # Green Box = Detected Face
                cv2.rectangle(img_copy, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
                
                # Label
                label_text = "Detected Face"
                (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                # Background strip
                cv2.rectangle(img_copy, (box[0], box[1] - 25), (box[0] + w + 10, box[1]), (0, 255, 0), -1)
                # Text
                cv2.putText(img_copy, label_text, (box[0] + 5, box[1] - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2) # Black text

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

    def load_new_file(self):
        from PySide6.QtWidgets import QFileDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            import cv2
            img = cv2.imread(file_name)
            if img is not None:
                self.on_image_captured(img)
            else:
                QMessageBox.warning(self, "Error", "Could not load image.")

    def export_exact_results(self):
        if self.current_image is not None and self.current_report is not None:
             res = self.exporter.save_exact_image(self.current_image, self.current_report)
             if 'image_path' in res:
                 QMessageBox.information(self, "Exact Export Successful", f"Saved EXACT preview to {res['image_path']}")
        else:
             QMessageBox.warning(self, "Export Failed", "No image to export.")
