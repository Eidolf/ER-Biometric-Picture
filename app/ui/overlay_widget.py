
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from PySide6.QtCore import Qt, QRectF

class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.ratio = 35 / 45
        self.scale_factor = 1.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        w = rect.width()
        h = rect.height()
        
        # Calculate ideal 35:45 box centered
        if w / h > self.ratio:
            # Too wide, fit height
            box_h = h * 0.9
            box_w = box_h * self.ratio
        else:
            # Too tall, fit width
            box_w = w * 0.9
            box_h = box_w / self.ratio
            
        x = (w - box_w) / 2
        y = (h - box_h) / 2
        self.box_rect = QRectF(x, y, box_w, box_h)
        
        # Draw darkened background outside the box
        # Actually standard BMI template is just lines
        
        pen = QPen(QColor(0, 255, 255), 3) # Cyan color
        painter.setPen(pen)
        painter.drawRect(self.box_rect)
        
        # Draw Face Oval (approximate)
        # Face height min 32mm (71%), max 36mm (80%) of 45mm
        # Top of head to chin check
        
        min_face_h = box_h * 0.71
        max_face_h = box_h * 0.80
        
        # Center oval vertically? No, chin is at specific point.
        # Bottom of chin is roughly at B ms from bottom.
        # Let's simple draw an oval in the center for guidance.
        
        oval_w = box_w * 0.7
        oval_h = box_h * 0.8
        oval_x = x + (box_w - oval_w) / 2
        oval_y = y + (box_h - oval_h) / 2
        
        painter.setPen(QPen(QColor(255, 255, 0, 150), 2, Qt.DashLine))
        painter.drawEllipse(QRectF(oval_x, oval_y, oval_w, oval_h))
        
        
        # Draw Eye Line Zone (BMI Step 1: Augenbereich)
        # Min: 21.8mm from bottom, Max: 29.7mm from bottom (relative to 45mm height)
        # Convert to pixels relative to box_h
        
        min_eye_mm = 21.8
        max_eye_mm = 29.7
        total_h_mm = 45.0
        
        # Img Bottom is y + box_h
        # Line Y = (y + box_h) - (mm / 45 * box_h)
        
        y_eye_lower_limit = (y + box_h) - (min_eye_mm / total_h_mm * box_h)
        y_eye_upper_limit = (y + box_h) - (max_eye_mm / total_h_mm * box_h)
        
        # Draw the zone as a semi-transparent band
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(200, 200, 200, 80))) # Gray zone
        painter.drawRect(QRectF(x, y_eye_upper_limit, box_w, y_eye_lower_limit - y_eye_upper_limit))
        
        painter.setPen(QPen(QColor(0, 255, 0, 200), 2))
        painter.drawLine(x, y_eye_upper_limit, x + box_w, y_eye_upper_limit)
        painter.drawLine(x, y_eye_lower_limit, x + box_w, y_eye_lower_limit)
        
        # Draw Center Line (Nasenmitte)
        center_x = x + box_w / 2
        painter.setPen(QPen(QColor(255, 255, 0, 200), 1, Qt.DashLine))
        painter.drawLine(center_x, y, center_x, y + box_h)
        
        # Face Height Zone (Chin is assumed at bottom margin? No, chin can be anywhere but usually aligned)
        # If we align Chin to a specific line, say 4mm from bottom?
        # ICAO: Chin to Bottom > 2mm usually?
        # Let's just draw the "Ideal Face Top" zone assuming chin is at y + box_h - margin?
        # The overlay is a guide. Let's just show the eye zone clearing.
        
        painter.setPen(QPen(Qt.white))
        painter.drawText(x + 5, y_eye_upper_limit - 5, "Eye Zone Top")
        painter.drawText(x + 5, y_eye_lower_limit + 15, "Eye Zone Bottom")

    def get_crop_rect(self):
        return self.box_rect
