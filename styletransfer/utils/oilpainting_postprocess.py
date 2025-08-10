# from PIL import Image, ImageEnhance, ImageFilter
# import numpy as np
# import cv2
# from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan

# def run_postprocessing(input_path, output_path, use_superres=False):
#     # Load image
#     img = Image.open(input_path).convert("RGB")
#     img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

#     # === STEP 1: Apply finer oil-painting filter ===
#     oil_painted = cv2.xphoto.oilPainting(img_cv, size=3, dynRatio=1)
#     oil_img = Image.fromarray(cv2.cvtColor(oil_painted, cv2.COLOR_BGR2RGB))

#     # === STEP 2: Enhance details and color ===
#     oil_img = ImageEnhance.Color(oil_img).enhance(1.3)     # stronger color
#     oil_img = ImageEnhance.Contrast(oil_img).enhance(1.15) # better contrast
#     oil_img = ImageEnhance.Sharpness(oil_img).enhance(1.2) # recover edge

#     # === STEP 3: Add subtle texture ===
#     noise_texture = Image.effect_noise(oil_img.size, 5).convert("L")
#     texture_rgb = Image.merge("RGB", [noise_texture]*3)
#     blended = Image.blend(oil_img, texture_rgb, alpha=0.05)  # subtle grain

#     # === STEP 4: Optional super-resolution ===
#     if use_superres:
#         blended = upscale_with_realesrgan(blended)

#     blended.save(output_path)
from PIL import Image, ImageEnhance
import numpy as np
import cv2
from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan

def run_postprocessing(input_path, output_path, use_superres=False):
    # Load original
    original_pil = Image.open(input_path).convert("RGB")
    original_cv = cv2.cvtColor(np.array(original_pil), cv2.COLOR_RGB2BGR)

    # === Detect face ===
    gray = cv2.cvtColor(original_cv, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # === Apply oil painting globally ===
    oil_painted_cv = cv2.xphoto.oilPainting(original_cv, size=3, dynRatio=1)
    oil_painted_rgb = cv2.cvtColor(oil_painted_cv, cv2.COLOR_BGR2RGB)
    oil_pil = Image.fromarray(oil_painted_rgb)

    # === Enhance color, contrast ===
    oil_pil = ImageEnhance.Color(oil_pil).enhance(1.8)
    oil_pil = ImageEnhance.Contrast(oil_pil).enhance(1.3)
    oil_pil = ImageEnhance.Sharpness(oil_pil).enhance(1.2)

    # === Paste face region from original for sharpness ===
    if len(faces) > 0:
        oil_pil_np = np.array(oil_pil)
        original_np = np.array(original_pil)

        for (x, y, w, h) in faces:
            # Define a slightly larger face patch (to include eyes/mouth)
            pad = int(w * 0.15)
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(original_np.shape[1], x + w + pad)
            y2 = min(original_np.shape[0], y + h + pad)

            # Blend original face back into painted image
            blended_face = cv2.addWeighted(
                oil_pil_np[y1:y2, x1:x2],
                0.3,
                original_np[y1:y2, x1:x2],
                0.7,
                0
            )
            oil_pil_np[y1:y2, x1:x2] = blended_face

        oil_pil = Image.fromarray(oil_pil_np)

    # === Optional texture noise ===
    noise = Image.effect_noise(oil_pil.size, 6).convert("L")
    textured = Image.blend(oil_pil, Image.merge("RGB", [noise]*3), alpha=0.05)

    # === Super-resolution (optional) ===
    final_img = upscale_with_realesrgan(textured) if use_superres else textured

    final_img.save(output_path)
