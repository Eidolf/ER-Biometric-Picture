
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QHBoxLayout, QSlider
from PySide6.QtCore import Qt

class ResultWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        
        self.header = QLabel("Analysis Results")
        self.header.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.header)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Check", "Status", "Value", "Message"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 80)
        self.layout.addWidget(self.tree)
        
        # Buttons Layout
        btn_layout = QHBoxLayout()
        self.layout.addLayout(btn_layout)
        
        # Optimization Controls Group
        self.opt_group = QWidget()
        opt_layout = QVBoxLayout(self.opt_group)
        opt_layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        lbl = QLabel("Optimization Tools:")
        lbl.setStyleSheet("font-weight: bold; margin-top: 10px;")
        opt_layout.addWidget(lbl)
        
        # Brightness
        bright_layout = QHBoxLayout()
        self.btn_darken = QPushButton("🌑 - Darker")
        self.btn_brighten = QPushButton("☀️ + Brighter")
        bright_layout.addWidget(self.btn_darken)
        bright_layout.addWidget(self.btn_brighten)
        opt_layout.addLayout(bright_layout)
        
        # Special
        tools_layout = QHBoxLayout()
        self.btn_fix_bg = QPushButton("Fix Background")
        self.btn_undo = QPushButton("↩️ Reset / Undo")
        
        tools_layout.addWidget(self.btn_fix_bg)
        tools_layout.addWidget(self.btn_undo)
        opt_layout.addLayout(tools_layout)
        
        self.layout.addWidget(self.opt_group)
        
        # Spacer
        self.layout.addSpacing(10)
        
        # Main Export
        self.btn_export = QPushButton("Export Results")
        self.btn_export.setStyleSheet("height: 40px; font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.btn_export)
        
        # Save Exact (Raw) Button
        self.btn_export_exact = QPushButton("💾 Save Exact Preview")
        self.btn_export_exact.setToolTip("Save the image exactly as displayed now (no auto-crop)")
        self.layout.addWidget(self.btn_export_exact)
        
        # Crop Button
        self.btn_crop = QPushButton("✂️ Adjust Crop")
        self.btn_crop.setCheckable(True)
        self.btn_crop.setStyleSheet("height: 30px; font-weight: bold; margin-top: 5px;")
        self.layout.addWidget(self.btn_crop)
        
        # Zoom Controls (Hidden by default, shown in Crop Mode)
        self.zoom_group = QWidget()
        zoom_layout = QHBoxLayout(self.zoom_group)
        zoom_layout.setContentsMargins(0, 5, 0, 5)
        
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        self.btn_zoom_out = QPushButton("➖")
        self.btn_zoom_out.setFixedWidth(30)
        zoom_layout.addWidget(self.btn_zoom_out)
        
        self.slider_zoom = QSlider(Qt.Horizontal)
        self.slider_zoom.setRange(10, 400) # 10% to 400%
        self.slider_zoom.setValue(100)
        zoom_layout.addWidget(self.slider_zoom)

        self.btn_zoom_in = QPushButton("➕")
        self.btn_zoom_in.setFixedWidth(30)
        zoom_layout.addWidget(self.btn_zoom_in)
        
        self.lbl_zoom_val = QLabel("100%")
        self.lbl_zoom_val.setFixedWidth(40)
        zoom_layout.addWidget(self.lbl_zoom_val)
        
        self.layout.addWidget(self.zoom_group)
        self.zoom_group.hide()

    def update_results(self, results):
        self.tree.clear()
        
        all_passed = True
        
        groups = {
            'Geometry': ['face_height', 'eye_position', 'roll'],
            'Quality': ['blur', 'exposure', 'contrast'],
            'Background': ['uniformity', 'brightness']
        }
        
        for group, keys in groups.items():
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, group)
            parent.setExpanded(True)
            
            group_passed = True
            
            for key in keys:
                if key in results:
                    data = results[key]
                    item = QTreeWidgetItem(parent)
                    item.setText(0, key.replace('_', ' ').title())
                    passed = data.get('passed', False)
                    item.setText(1, "PASS" if passed else "FAIL")
                    item.setText(2, str(data.get('value', '')))
                    item.setText(3, data.get('msg', ''))
                    item.setToolTip(3, data.get('msg', ''))
                    
                    if not passed:
                        item.setForeground(1, Qt.red)
                        item.setForeground(3, Qt.red)
                        group_passed = False
                        all_passed = False
                    else:
                        item.setForeground(1, Qt.green)
            
            if group_passed:
                parent.setForeground(0, Qt.green)
            else:
                parent.setForeground(0, Qt.red)
                
        if all_passed:
            self.header.setText("Analysis Results: PASSED")
            self.header.setStyleSheet("color: green; font-size: 18px; font-weight: bold;")
        else:
            self.header.setText("Analysis Results: FAILED")
            self.header.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
