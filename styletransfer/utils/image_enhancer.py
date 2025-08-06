from PIL import Image, ImageEnhance
import cv2
import numpy as np

def enhance_image(image_path):
    image = Image.open(image_path).convert('RGB')
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Denoise
    denoised = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)

    # Sharpen
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)

    # Back to PIL
    final_img = Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))

    # Optional contrast boost
    enhancer = ImageEnhance.Contrast(final_img)
    final_img = enhancer.enhance(1.2)

    return final_img
