
import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QPixmap, QImage
from app.ui.overlay_widget import OverlayWidget

class CameraWidget(QWidget):
    # Signals
    image_captured_signal = Signal(object) # param: numpy array (BGR)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.view_label = QLabel("Camera Feed")
        self.view_label.setAlignment(Qt.AlignCenter)
        self.view_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.view_label, 1)
        
        # Overlay
        self.overlay = OverlayWidget(self.view_label)
        self.overlay.show()
        
        # Controls
        controls = QHBoxLayout()
        self.btn_capture = QPushButton("Capture Photo")
        self.btn_capture.clicked.connect(self.capture_image)
        
        self.btn_load = QPushButton("Load File")
        self.btn_load.clicked.connect(self.load_from_file)
        
        self.btn_toggle = QPushButton("Start Camera")
        self.btn_toggle.clicked.connect(self.toggle_camera)
        
        controls.addWidget(self.btn_toggle)
        controls.addWidget(self.btn_capture)
        controls.addWidget(self.btn_load)
        self.layout.addLayout(controls)
        
        # Camera internal
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.current_frame = None
        self.is_camera_active = False

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize overlay to match label
        if self.view_label:
             self.overlay.resize(self.view_label.size())

    def toggle_camera(self):
        if self.is_camera_active:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0) # Default camera
            # Set high res if possible
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
        if self.cap.isOpened():
            self.is_camera_active = True
            self.timer.start(30) # ~30fps
            self.btn_toggle.setText("Stop Camera")

    def stop_camera(self):
        self.is_camera_active = False
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.btn_toggle.setText("Start Camera")

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self.display_frame(frame)

    def display_frame(self, frame_bgr):
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        
        # Scale to fit label
        lbl_w = self.view_label.width()
        lbl_h = self.view_label.height()
        
        # Keep aspect ratio
        scale = min(lbl_w / w, lbl_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        frame_resized = cv2.resize(frame_rgb, (new_w, new_h))
        
        q_img = QImage(frame_resized.data, new_w, new_h, new_w * ch, QImage.Format_RGB888)
        self.view_label.setPixmap(QPixmap.fromImage(q_img))

    def capture_image(self):
        if self.current_frame is not None:
            self.image_captured_signal.emit(self.current_frame)

    def load_from_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.jpg *.png *.jpeg)")
        if path:
            img = cv2.imread(path)
            if img is not None:
                self.current_frame = img
                self.stop_camera() # Stop live feed to show loaded image
                self.display_frame(img)
                # Auto emit? Or wait for "Process" button? 
                # Let's auto emit for now or user clicks capture?
                # Better: Treat "Load" as immediate selection
                self.image_captured_signal.emit(img)
