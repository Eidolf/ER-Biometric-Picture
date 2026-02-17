
from PySide6.QtCore import QObject, Signal, QThread
import traceback

class InitWorker(QObject):
    finished = Signal()
    error = Signal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
    def run(self):
        try:
            from app.core.analyzer import Analyzer
            self.main_window.analyzer = Analyzer(self.main_window.config)
            self.finished.emit()
        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))

class AnalysisWorker(QObject):
    finished = Signal(object, object) # report, face
    error = Signal(str)
    
    def __init__(self, analyzer, image):
        super().__init__()
        self.analyzer = analyzer
        self.image = image
        
    def run(self):
        try:
            report, face = self.analyzer.analyze(self.image)
            self.finished.emit(report, face)
        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))
