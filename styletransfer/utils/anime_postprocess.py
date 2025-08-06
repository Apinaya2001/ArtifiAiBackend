# # styletransfer/models/anime_postprocess.py

# import cv2
# import numpy as np
# from PIL import Image

# def detect_faces(image_bgr):
#     gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
#     face_cascade = cv2.CascadeClassifier(
#         cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
#     )
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
#     return faces

# def enhance_face_softly(image, face):
#     x, y, w, h = face
#     roi = image[y:y+h, x:x+w]
#     smoothed = cv2.bilateralFilter(roi, d=9, sigmaColor=50, sigmaSpace=75)
#     sharpen_kernel = np.array([[0, -1, 0], [-1, 5.0, -1], [0, -1, 0]])
#     sharpened = cv2.filter2D(smoothed, -1, sharpen_kernel)
#     mask = np.zeros(image.shape[:2], dtype=np.uint8)
#     cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)
#     mask = cv2.GaussianBlur(mask, (25, 25), 10)
#     alpha = mask[y:y+h, x:x+w].astype(float) / 255.0
#     for c in range(3):
#         image[y:y+h, x:x+w, c] = (
#             sharpened[:, :, c] * alpha + roi[:, :, c] * (1 - alpha)
#         )
#     return image

# def create_face_mask(image_shape, faces):
#     mask = np.zeros(image_shape[:2], dtype=np.uint8)
#     for (x, y, w, h) in faces:
#         cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
#     return mask

# def smooth_background(image, face_mask):
#     blurred = cv2.edgePreservingFilter(image, flags=1, sigma_s=60, sigma_r=0.4)
#     return np.where(face_mask[:, :, np.newaxis] == 0, blurred, image)

# def run_postprocessing(stylized_pil_image):
#     image = np.array(stylized_pil_image.convert('RGB'))
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#     faces = detect_faces(image)
#     for face in faces:
#         image = enhance_face_softly(image, face)
#     face_mask = create_face_mask(image.shape, faces)
#     image = smooth_background(image, face_mask)
#     image = cv2.edgePreservingFilter(image, flags=1, sigma_s=80, sigma_r=0.35)
#     final_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     return Image.fromarray(final_rgb)
from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan

def run_postprocessing(input_path, output_path, use_superres=True):
    from PIL import Image
    import cv2
    import numpy as np

    # Load image
    image = Image.open(input_path).convert("RGB")
    img_np = np.array(image)

    # Slight contrast boost and sharpening
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    img_cv = cv2.detailEnhance(img_cv, sigma_s=10, sigma_r=0.15)
    img_cv = cv2.edgePreservingFilter(img_cv, flags=1, sigma_s=60, sigma_r=0.4)

    # Back to PIL
    output_image = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
    output_image.save(output_path)

    # Optional: apply super-resolution
    if use_superres:
        try:
            upscale_with_realesrgan(output_path, output_path)
        except Exception as e:
            print("[Real-ESRGAN warning] Super-resolution failed:", e)

    return output_image
