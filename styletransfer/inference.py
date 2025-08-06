
import os
from uuid import uuid4
from PIL import Image
from django.conf import settings
import torch
import torchvision.transforms as T
import torchvision.transforms.functional as TF
from .utils.anime_postprocess import run_postprocessing  # ✅ Correct name

# 🔥 Cache AnimeGANv2 Torch Hub model
_animegan_model = None

@torch.no_grad()
def load_animegan_model():
    model = torch.hub.load(
        "bryandlee/animegan2-pytorch:main",
        "generator",
        pretrained="face_paint_512_v2",  # ✅ official supported model name
        trust_repo=True
    )
    model.eval()
    return model

# 🎨 Apply AnimeGANv2 to the image
def apply_anime_style(input_image_path):
    model = load_animegan_model()

    image = Image.open(input_image_path).convert("RGB")
    transform = T.Compose([
        T.Resize((512, 512)),
        T.ToTensor(),
        T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    input_tensor = transform(image).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        output_tensor = model(input_tensor)[0]

    output_tensor = (output_tensor + 1) / 2  # Denormalize to [0, 1]
    output_image = TF.to_pil_image(output_tensor.clamp(0, 1))

    raw_output_path = input_image_path.replace('.jpg', '_raw.jpg')
    output_image.save(raw_output_path)
    return raw_output_path


# 🚀 Full pipeline: stylization + soft post-processing
def run_inference_with_postprocessing(input_image_path, model_name=None):
    print(f"Running inference on: {input_image_path} with model: {model_name}")

    stylized_output_path = apply_anime_style(input_image_path)

    raw_image = Image.open(stylized_output_path)
    final_image = run_postprocessing(raw_image)

    output_dir = os.path.join(settings.MEDIA_ROOT, "output")
    os.makedirs(output_dir, exist_ok=True)

    final_filename = f"styled_{uuid4().hex}.jpg"
    final_output_path = os.path.join(output_dir, final_filename)
    final_image.save(final_output_path)

    return final_output_path
