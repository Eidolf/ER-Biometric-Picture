
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QImage, QPixmap, QColor, QPen, QBrush
from PySide6.QtCore import Qt, QRectF, QPointF, Signal

class InteractiveCropper(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.pixmap = None
        
        # Transform state
        self.scale = 1.0
        # Transform state
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.zoom_changed_callback = None
        
        # Interaction state
        self.last_mouse_pos = QPointF()
        self.is_panning = False
        
        # Target Output (35x45mm)
        self.aspect_ratio = 35 / 45
        self.target_height_pct = 0.8 # Target box height relative to widget height (max)
        
        # Overlay settings
        self.overlay_color = QColor(0, 255, 255)
        self.dim_color = QColor(0, 0, 0, 150)
        
    def set_image(self, img_bgr):
        import cv2
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        # KEY FIX: .copy() to ensure deep copy of data because img_rgb will be garbage collected
        self.image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
        self.pixmap = QPixmap.fromImage(self.image)
        
        # Reset transform to fit image
        self.reset_view()
        self.update()

    def reset_view(self):
        if not self.pixmap: return
        
        # Fit image to widget? Or fit to crop box?
        # Initial: Center image in widget, scale to reasonable fit
        w = self.width()
        h = self.height()
        
        img_w = self.pixmap.width()
        img_h = self.pixmap.height()
        
        # Scale to fill at least the crop box? 
        # For now fit to widget with some margin
        scale_w = w / img_w
        scale_h = h / img_h
        self.scale = min(scale_w, scale_h) * 0.8
        
        self.offset_x = (w - img_w * self.scale) / 2
        self.offset_y = (h - img_h * self.scale) / 2
        
        self.update_zoom_callback()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Black background
        painter.fillRect(self.rect(), Qt.black)
        
        if self.pixmap:
            # Draw Image with Transform
            painter.save()
            painter.translate(self.offset_x, self.offset_y)
            painter.scale(self.scale, self.scale)
            painter.drawPixmap(0, 0, self.pixmap)
            painter.restore()
            
        # Draw Overlay (Fixed Center)
        self.draw_overlay(painter)
        
    def draw_overlay(self, painter):
        w = self.width()
        h = self.height()
        
        # Calculate Target Box
        box_h = h * self.target_height_pct
        box_w = box_h * self.aspect_ratio
        
        if box_w > w * 0.9:
            box_w = w * 0.9
            box_h = box_w / self.aspect_ratio
        
        cx = w / 2
        cy = h / 2
        
        x = cx - box_w / 2
        y = cy - box_h / 2
        
        self.crop_box = QRectF(x, y, box_w, box_h)
        
        # Draw Dimmed Surroundings
        
        # Top
        painter.fillRect(QRectF(0, 0, w, y), self.dim_color)
        # Bottom
        painter.fillRect(QRectF(0, y + box_h, w, h - (y + box_h)), self.dim_color)
        # Left
        painter.fillRect(QRectF(0, y, x, box_h), self.dim_color)
        # Right
        painter.fillRect(QRectF(x + box_w, y, w - (x + box_w), box_h), self.dim_color)
        
        # Draw Box Border
        painter.setPen(QPen(self.overlay_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.crop_box)
        
        # Draw Guides (Eye Zone)
        # 35x45mm. Eye zone 21.8 - 29.7mm from bottom.
        # Relative to Top:
        # Top = 0. Bottom = 45.
        # Eye Top (from top) = 45 - 29.7 = 15.3 mm
        # Eye Bottom (from top) = 45 - 21.8 = 23.2 mm
        
        # Draw Guides (Eye Zone)
        # 35x45mm. Eye zone 21.8 - 29.7mm from bottom.
        mm_h = box_h / 45.0
        eye_top_y = y + (45.0 - 29.7) * mm_h
        eye_bottom_y = y + (45.0 - 21.8) * mm_h
        
        # Eye Zone
        painter.setPen(QPen(QColor(0, 255, 0, 150), 1, Qt.DashLine))
        painter.drawLine(x, eye_top_y, x + box_w, eye_top_y)
        painter.drawText(x + 5, eye_top_y - 2, "Eye Max")
        
        painter.drawLine(x, eye_bottom_y, x + box_w, eye_bottom_y)
        painter.drawText(x + 5, eye_bottom_y + 12, "Eye Min")
        
        # Face Height Guides (Concentric Ovals)
        # Max Face (36mm) - RED
        max_fh_pix = 36.0 * mm_h
        max_fw_pix = max_fh_pix * 0.75
        painter.setPen(QPen(QColor(255, 0, 0, 180), 2))
        painter.drawEllipse(QPointF(cx, cy), max_fw_pix/2, max_fh_pix/2)
        painter.drawText(cx + max_fw_pix/2 + 2, cy, "Max")
        
        # Min Face (30mm) - YELLOW
        min_fh_pix = 30.0 * mm_h
        min_fw_pix = min_fh_pix * 0.75
        painter.setPen(QPen(QColor(255, 255, 0, 180), 2)) 
        painter.drawEllipse(QPointF(cx, cy), min_fw_pix/2, min_fh_pix/2)
        painter.drawText(cx + min_fw_pix/2 + 2, cy + 15, "Min")
        
        # Chin Guide Labels
        chin_max_y = cy + max_fh_pix/2
        painter.setPen(QPen(QColor(255, 0, 0, 200), 1))
        painter.drawText(cx - 40, chin_max_y + 12, "Chin Max")
        
        chin_min_y = cy + min_fh_pix/2
        painter.setPen(QPen(QColor(255, 255, 0, 200), 1))
        painter.drawText(cx - 40, chin_min_y - 2, "Chin Min")
        
        # Center Line
        painter.setPen(QPen(QColor(255, 255, 255, 50), 1, Qt.DashLine))
        painter.drawLine(cx, y, cx, y + box_h)
        
        # Oval hint
        painter.setPen(QPen(QColor(255, 255, 255, 50), 2))
        oval_w = box_w * 0.7
        oval_h = box_h * 0.8
        painter.drawEllipse(QPointF(cx, cy - box_h * 0.05), oval_w/2, oval_h/2)

    # Interaction
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_panning = True
            self.last_mouse_pos = event.globalPosition()
            
    def set_zoom(self, zoom_pct):
        # Set absolute zoom (factor)
        new_scale = zoom_pct / 100.0
        if abs(new_scale - self.scale) < 0.01: return
        
        # Center zoom logic
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        
        if self.scale > 0:
             ix = (cx - self.offset_x) / self.scale
             iy = (cy - self.offset_y) / self.scale
             
             self.offset_x = cx - ix * new_scale
             self.offset_y = cy - iy * new_scale
        
        self.scale = new_scale
        self.update()

    def update_zoom_callback(self):
         if self.zoom_changed_callback:
             pct = int(self.scale * 100)
             self.zoom_changed_callback(pct)

    def mouseMoveEvent(self, event):
        if self.is_panning:
            delta = event.globalPosition() - self.last_mouse_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_pos = event.globalPosition()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            
    def wheelEvent(self, event):
        # Zoom logic
        delta = event.angleDelta().y()
        zoom_factor = 1.1 if delta > 0 else 0.9
        
        # Focus on mouse position? Or center?
        # Center for now
        
        # New Scale
        new_scale = self.scale * zoom_factor
        
        # Limit scale
        if new_scale < 0.1: new_scale = 0.1
        if new_scale > 10.0: new_scale = 10.0
        
        # Adjust offset to zoom centered
        # S2 = S1 * Z
        # We want Center of Screen to map to same Image Point
        
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        
        # Vector from offset to center
        vx = cx - self.offset_x
        vy = cy - self.offset_y
        
        # Scale vector
        vx *= zoom_factor
        vy *= zoom_factor
        
        # New offset
        self.offset_x = cx - vx
        self.offset_y = cy - vy
        
        self.scale = new_scale
        self.update_zoom_callback()
        self.update()

    def get_current_crop(self):
        """
        Returns the image cropped to the current box.
        """
        if not self.pixmap: return None
        
        # Calculate logic
        # Box Rect in Widget Coords: self.crop_box
        # Image Transform: translate(ox, oy) scale(s, s)
        # We need to map Box Rect to Image Coords
        
        box = self.crop_box
        
        # Inverse Transform
        # P_img = (P_widget - Offset) / Scale
        
        x1 = (box.x() - self.offset_x) / self.scale
        y1 = (box.y() - self.offset_y) / self.scale
        w = box.width() / self.scale
        h = box.height() / self.scale
        
        # Convert QImage/QPixmap to numpy/cv2 ?
        # Actually easier to act on the original numpy array if we stored it?
        # We stored QImage. Let's convert back or store original in logic.
        
        return QRectF(x1, y1, w, h)

