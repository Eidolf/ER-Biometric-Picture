
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

class FaceDetector:
    def __init__(self, model_name='buffalo_l', ctx_id=0, det_size=(640, 640)):
        """
        Initialize InsightFace Analysis.
        :param model_name: 'buffalo_l' (more accurate) or 'buffalo_sc' (faster)
        :param ctx_id: GPU index (-1 for CPU)
        :param det_size: Detection size
        """
        self.app = FaceAnalysis(name=model_name, providers=['CPUExecutionProvider']) # Force CPU for compatibility
        self.app.prepare(ctx_id=ctx_id, det_size=det_size)

    def detect_faces(self, img_path_or_array):
        """
        Detect faces in an image.
        :param img_path_or_array: Path to image or numpy array (BGR)
        :return: List of detected face objects
        """
        if isinstance(img_path_or_array, str):
            img = cv2.imread(img_path_or_array)
        else:
            img = img_path_or_array
            
        if img is None:
            raise ValueError("Could not load image")

        faces = self.app.get(img)
        return faces, img
