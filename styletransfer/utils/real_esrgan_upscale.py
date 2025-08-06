import numpy as np
from PIL import Image
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
import os
from django.conf import settings  # Add this to access settings.BASE_DIR

def upscale_with_realesrgan(image: Image.Image) -> Image.Image:
    # Construct full path to the correct Real-ESRGAN model
    model_path = os.path.join(
        settings.BASE_DIR,
        "styletransfer",
        "model",
        "RealESRGAN_x4plus.pth"
    )

    model = RRDBNet(
        num_in_ch=3, num_out_ch=3,
        num_feat=64, num_block=23, num_grow_ch=32, scale=4
    )

    upsampler = RealESRGANer(
        scale=4,
        model_path=model_path,
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False  # set to True if using float16 GPU
    )

    img_np = np.array(image)
    output, _ = upsampler.enhance(img_np, outscale=1)

    return Image.fromarray(output)
