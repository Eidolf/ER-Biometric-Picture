
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QHBoxLayout
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
        
        self.btn_export = QPushButton("Export Results")
        self.layout.addWidget(self.btn_export)

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
