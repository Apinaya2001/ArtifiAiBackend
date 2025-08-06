
import cv2
import numpy as np
from PIL import Image

# 🧠 Step 1: Detect faces using Haar cascade
def detect_faces(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return faces

# 🎯 Step 2: Enhance facial region with soft blending
def enhance_face_softly(image, face):
    x, y, w, h = face
    roi = image[y:y+h, x:x+w]

    # 💧 Smoothing that preserves texture
    smoothed = cv2.bilateralFilter(roi, d=9, sigmaColor=50, sigmaSpace=75)

    # ✨ Gentle sharpening
    sharpen_kernel = np.array([[0, -1, 0],
                               [-1, 5.0, -1],
                               [0, -1, 0]])
    sharpened = cv2.filter2D(smoothed, -1, sharpen_kernel)

    # 🎭 Feathered mask for soft face overlay
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)
    mask = cv2.GaussianBlur(mask, (25, 25), 10)
    alpha = mask[y:y+h, x:x+w].astype(float) / 255.0

    # 🎨 Blend the enhanced face back into the image
    for c in range(3):
        image[y:y+h, x:x+w, c] = (
            sharpened[:, :, c] * alpha + roi[:, :, c] * (1 - alpha)
        )
    return image

# 🌌 Step 3: Create mask for background smoothing (ignore face region)
def create_face_mask(image_shape, faces):
    mask = np.zeros(image_shape[:2], dtype=np.uint8)
    for (x, y, w, h) in faces:
        cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    return mask

# 🌊 Step 4: Smooth background while preserving edges
def smooth_background(image, face_mask):
    blurred = cv2.edgePreservingFilter(image, flags=1, sigma_s=60, sigma_r=0.4)
    return np.where(face_mask[:, :, np.newaxis] == 0, blurred, image)

# 🧪 Final post-processing pipeline
def run_postprocessing(stylized_pil_image):
    image = np.array(stylized_pil_image.convert('RGB'))
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # 🎯 Detect and enhance all detected faces
    faces = detect_faces(image)
    for face in faces:
        image = enhance_face_softly(image, face)

    # 🌌 Smooth background excluding faces
    face_mask = create_face_mask(image.shape, faces)
    image = smooth_background(image, face_mask)

    # 💫 Global detail enhancement (overall softening)
    image = cv2.edgePreservingFilter(image, flags=1, sigma_s=80, sigma_r=0.35)

    # 🔁 Back to PIL
    final_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(final_rgb)
