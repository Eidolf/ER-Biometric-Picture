
import os
import cv2
import numpy as np

def generate_samples():
    os.makedirs("tests/samples", exist_ok=True)
    
    # 1. Good Image (Green background for easy seg, sharp, good exposure)
    img = np.zeros((450, 350, 3), dtype=np.uint8)
    img[:] = (200, 200, 200) # Light gray background
    # Draw a "face"
    cv2.circle(img, (175, 200), 80, (150, 150, 255), -1) # Face
    cv2.circle(img, (155, 180), 10, (0, 0, 0), -1) # Left Eye
    cv2.circle(img, (195, 180), 10, (0, 0, 0), -1) # Right Eye
    cv2.imwrite("tests/samples/01_good.jpg", img)
    
    # 2. Blurry
    img_blur = cv2.GaussianBlur(img, (21, 21), 0)
    cv2.imwrite("tests/samples/02_blur.jpg", img_blur)
    
    # 3. Underexposed
    img_dark = (img * 0.3).astype(np.uint8)
    cv2.imwrite("tests/samples/03_dark.jpg", img_dark)
    
    # 4. Overexposed
    img_bright = np.clip(img * 2.0, 0, 255).astype(np.uint8)
    cv2.imwrite("tests/samples/04_bright.jpg", img_bright)
    
    
    # 5. Bad Background
    img_bg = img.copy()
    cv2.rectangle(img_bg, (0, 0), (100, 450), (0, 0, 255), -1) # Red stripe
    cv2.imwrite("tests/samples/05_bad_bg.jpg", img_bg)
    
    # 6. Face Too Small
    img_small = np.zeros((450, 350, 3), dtype=np.uint8)
    img_small[:] = (200, 200, 200)
    cv2.circle(img_small, (175, 200), 40, (150, 150, 255), -1) # Small face
    cv2.imwrite("tests/samples/06_small_face.jpg", img_small)
    
    # 7. Face Too Big
    img_big = np.zeros((450, 350, 3), dtype=np.uint8)
    img_big[:] = (200, 200, 200)
    cv2.circle(img_big, (175, 200), 160, (150, 150, 255), -1) # Huge face
    cv2.imwrite("tests/samples/07_big_face.jpg", img_big)
    
    # 8. Eyes Too Low
    img_lowy = np.zeros((450, 350, 3), dtype=np.uint8)
    img_lowy[:] = (200, 200, 200)
    cv2.circle(img_lowy, (175, 300), 80, (150, 150, 255), -1) # Low face
    cv2.circle(img_lowy, (155, 280), 10, (0, 0, 0), -1)
    cv2.circle(img_lowy, (195, 280), 10, (0, 0, 0), -1)
    cv2.imwrite("tests/samples/08_low_face.jpg", img_lowy)
    
    # 9. Tilted Head
    img_tilt = img.copy()
    M = cv2.getRotationMatrix2D((175, 200), 15, 1)
    img_tilt = cv2.warpAffine(img_tilt, M, (350, 450), borderValue=(200,200,200))
    cv2.imwrite("tests/samples/09_tilted.jpg", img_tilt)
    
    # 10. Noisy
    noise = np.random.randint(0, 50, (450, 350, 3), dtype=np.uint8)
    img_noise = cv2.add(img, noise)
    cv2.imwrite("tests/samples/10_noisy.jpg", img_noise)
    
    print("Generated 10 synthetic samples in tests/samples/")

if __name__ == "__main__":
    generate_samples()
