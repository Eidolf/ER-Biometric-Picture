
import pytest
from app.core.geometry import GeometryChecker

def test_face_height_check(mock_config, mock_face):
    checker = GeometryChecker(mock_config)
    
    # Image height 1000px. 45mm equivalent.
    # Min height 32mm -> 711px. Max 36mm -> 800px.
    
    # Case 1: Perfect height (34mm -> ~755px)
    face = mock_face([100, 100, 500, 855], [[0,0]]*5) # bbox height 755
    res = checker.check_processed_image(face, 1000, 1000)
    assert res['face_height']['passed'] == True
    
    # Case 2: Too small (30mm -> 666px)
    face = mock_face([100, 100, 500, 766], [[0,0]]*5) 
    res = checker.check_processed_image(face, 1000, 1000)
    assert res['face_height']['passed'] == False
    
    # Case 3: Too big (38mm -> 844px)
    face = mock_face([100, 50, 500, 894], [[0,0]]*5)
    res = checker.check_processed_image(face, 1000, 1000)
    assert res['face_height']['passed'] == False

def test_eye_position(mock_config, mock_face):
    checker = GeometryChecker(mock_config)
    img_h = 1000
    px_per_mm = 1000 / 45
    
    # Eyes needed between 21.8mm and 29.7mm from bottom
    # 25mm from bottom = good.
    eye_y_from_bot = 25 * px_per_mm
    eye_y = img_h - eye_y_from_bot
    
    face = mock_face([0,0,10,10], [[10, eye_y], [20, eye_y], [0,0], [0,0], [0,0]])
    res = checker.check_processed_image(face, 1000, 1000)
    assert res['eye_position']['passed'] == True
    
    # Too low (15mm from bottom)
    eye_y_low = img_h - (15 * px_per_mm)
    face = mock_face([0,0,10,10], [[10, eye_y_low], [20, eye_y_low], [0,0], [0,0], [0,0]])
    res = checker.check_processed_image(face, 1000, 1000)
    assert res['eye_position']['passed'] == False

def test_roll_check(mock_config, mock_face):
    checker = GeometryChecker(mock_config)
    face = mock_face([0,0,10,10], [[10, 10], [20, 10], [0,0], [0,0], [0,0]])
    res = checker.check_processed_image(face, 100, 100)
    assert res['roll']['passed'] == True
