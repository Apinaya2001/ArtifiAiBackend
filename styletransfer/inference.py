import os
import cv2
import torch
import numpy as np
from uuid import uuid4
from PIL import Image
from django.conf import settings
import torchvision.transforms as T
import torchvision.transforms.functional as TF

# Import models
from styletransfer.model.generator import Generator
from styletransfer.utils.anime_postprocess import run_postprocessing as anime_post
from styletransfer.utils.cyberverse_postprocess import run_postprocessing as cyber_post
from styletransfer.utils.artbyai_postprocess import run_postprocessing as artbyai_post  # New style
from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan


# Caching model instances
_model_cache = {}


@torch.no_grad()
def load_animegan_model():
    if "anime" not in _model_cache:
        model = torch.hub.load(
            "bryandlee/animegan2-pytorch:main",
            "generator",
            pretrained="face_paint_512_v2"
        )
        model.eval()
        _model_cache["anime"] = model
    return _model_cache["anime"]


def load_cyberverse_model():
    if "cyberverse" not in _model_cache:
        model_path = os.path.join("styletransfer", "model", "cyberVerse.pth")
        if not os.path.exists(model_path):
            raise FileNotFoundError("Cyberverse model 'cyberVerse.pth' not found.")

        model = Generator()
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()
        _model_cache["cyberverse"] = model
    return _model_cache["cyberverse"]


def load_artbyai_model():
    if "artbyai" not in _model_cache:
        model_path = os.path.join("styletransfer", "model", "artbyai.pth")
        if not os.path.exists(model_path):
            raise FileNotFoundError("ArtByAI model 'artbyai.pth' not found.")

        model = Generator()
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()
        _model_cache["artbyai"] = model
    return _model_cache["artbyai"]


# === Centralized config ===
STYLE_CONFIG = {
    "anime": {
        "loader": load_animegan_model,
        "post": anime_post,
        "resize": (512, 512)
    },
    "cyberverse": {
        "loader": load_cyberverse_model,
        "post": cyber_post,
        "resize": (256, 256)
    },
    "artbyai": {
        "loader": load_artbyai_model,
        "post": artbyai_post,
        "resize": (256, 256)
    }
}


# === Style Transfer Core ===
@torch.no_grad()
def apply_style(input_image_path, model_loader, style_name):
    image = Image.open(input_image_path).convert("RGB")
    config = STYLE_CONFIG[style_name]

    transform = T.Compose([
        T.Resize(config["resize"]),
        T.ToTensor(),
        T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    input_tensor = transform(image).unsqueeze(0)
    model = model_loader()
    output_tensor = model(input_tensor)[0]

    output_tensor = (output_tensor + 1) / 2
    output_image = TF.to_pil_image(output_tensor.clamp(0, 1))

    # Save raw stylized output
    raw_path = input_image_path.replace(".jpg", f"_{style_name}_raw.jpg")
    output_image.save(raw_path)
    return raw_path


def run_inference_with_postprocessing(input_image_path, model_name="anime"):
    print(f"Running inference on: {input_image_path} with model: {model_name}")

    if model_name not in STYLE_CONFIG:
        raise ValueError(f"Unsupported model: {model_name}")

    # 1. Apply style transfer
    model_loader = STYLE_CONFIG[model_name]["loader"]
    stylized_path = apply_style(input_image_path, model_loader, model_name)

    # 2. Create output path
    output_dir = os.path.join(settings.MEDIA_ROOT, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"styled_{uuid4().hex}.jpg"
    final_path = os.path.join(output_dir, output_filename)

    # 3. Run postprocessing
    postprocess = STYLE_CONFIG[model_name]["post"]
    postprocess(stylized_path, final_path, use_superres=True)

    return final_path
