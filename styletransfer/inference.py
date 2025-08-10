# import os
# import cv2
# import torch
# import numpy as np
# from uuid import uuid4
# from PIL import Image
# from django.conf import settings
# import torchvision.transforms as T
# import torchvision.transforms.functional as TF

# # Import models
# from styletransfer.model.generator import Generator
# from styletransfer.utils.anime_postprocess import run_postprocessing as anime_post
# from styletransfer.utils.cyberverse_postprocess import run_postprocessing as cyber_post
# from styletransfer.utils.artbyai_postprocess import run_postprocessing as artbyai_post  # New style
# from styletransfer.utils.real_esrgan_upscale import upscale_with_realesrgan
# from styletransfer.utils.vangogh_postprocess import run_postprocessing as vangogh_post
# from styletransfer.utils.oilpainting_postprocess import run_postprocessing as oilpainting_post
# # from styletransfer.utils.oilpainting_postprocess import run_postprocessing as oilpainting_post


# # Caching model instances
# _model_cache = {}


# @torch.no_grad()
# def load_animegan_model():
#     if "anime" not in _model_cache:
#         model = torch.hub.load(
#             "bryandlee/animegan2-pytorch:main",
#             "generator",
#             pretrained="face_paint_512_v2"
#         )
#         model.eval()
#         _model_cache["anime"] = model
#     return _model_cache["anime"]


# def load_cyberverse_model():
#     if "cyberverse" not in _model_cache:
#         model_path = os.path.join("styletransfer", "model", "cyberVerse.pth")
#         if not os.path.exists(model_path):
#             raise FileNotFoundError("Cyberverse model 'cyberVerse.pth' not found.")

#         model = Generator()
#         model.load_state_dict(torch.load(model_path, map_location="cpu"))
#         model.eval()
#         _model_cache["cyberverse"] = model
#     return _model_cache["cyberverse"]


# def load_artbyai_model():
#     if "artbyai" not in _model_cache:
#         model_path = os.path.join("styletransfer", "model", "artbyai.pth")
#         if not os.path.exists(model_path):
#             raise FileNotFoundError("ArtByAI model 'artbyai.pth' not found.")

#         model = Generator()
#         model.load_state_dict(torch.load(model_path, map_location="cpu"))
#         model.eval()
#         _model_cache["artbyai"] = model
#     return _model_cache["artbyai"]


# def load_vangogh_model():
#     if "vangogh" not in _model_cache:
#         model_path = os.path.join("styletransfer", "model", "vangogh.pth")
#         if not os.path.exists(model_path):
#             raise FileNotFoundError("Van Gogh model 'vangogh.pth' not found.")

#         model = Generator()
#         model.load_state_dict(torch.load(model_path, map_location="cpu"))
#         model.eval()
#         _model_cache["vangogh"] = model
#     return _model_cache["vangogh"]

# def load_oilpainting_model():
#     if "oilpainting" in _model_cache:
#         return _model_cache["oilpainting"]

#     model = Generator()
#     model.load_state_dict(torch.load(os.path.join(settings.BASE_DIR, 'styletransfer/model/oilpainting.pth'), map_location='cpu'))
#     model.eval()
#     _model_cache["oilpainting"] = model
#     return model


# # === Centralized config ===
# STYLE_CONFIG = {
#     "anime": {
#         "loader": load_animegan_model,
#         "post": anime_post,
#         "resize": (512, 512)
#     },
#     "cyberverse": {
#         "loader": load_cyberverse_model,
#         "post": cyber_post,
#         "resize": (256, 256)
#     },
#     "artbyai": {
#         "loader": load_artbyai_model,
#         "post": artbyai_post,
#         "resize": (256, 256)
#     },
#      "vangogh": {
#         "loader": load_vangogh_model,
#         "post": vangogh_post,
#         "resize": (256, 256)
#     },
#     "oilpainting": {
#     "loader": load_oilpainting_model,
#     "post": oilpainting_post,
#     "resize": 256
# }


    
# }


# # === Style Transfer Core ===
# @torch.no_grad()
# def apply_style(input_image_path, model_loader, style_name):
#     image = Image.open(input_image_path).convert("RGB")
#     config = STYLE_CONFIG[style_name]

#     transform = T.Compose([
#         T.Resize(config["resize"]),
#         T.ToTensor(),
#         T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
#     ])

#     input_tensor = transform(image).unsqueeze(0)
#     model = model_loader()
#     output_tensor = model(input_tensor)[0]

#     output_tensor = (output_tensor + 1) / 2
#     output_image = TF.to_pil_image(output_tensor.clamp(0, 1))

#     # Save raw stylized output
#     raw_path = input_image_path.replace(".jpg", f"_{style_name}_raw.jpg")
#     output_image.save(raw_path)
#     return raw_path


# def run_inference_with_postprocessing(input_image_path, model_name="anime"):
#     print(f"Running inference on: {input_image_path} with model: {model_name}")

#     if model_name not in STYLE_CONFIG:
#         raise ValueError(f"Unsupported model: {model_name}")

#     # 1. Apply style transfer
#     model_loader = STYLE_CONFIG[model_name]["loader"]
#     stylized_path = apply_style(input_image_path, model_loader, model_name)

#     # 2. Create output path
#     output_dir = os.path.join(settings.MEDIA_ROOT, "output")
#     os.makedirs(output_dir, exist_ok=True)
#     output_filename = f"styled_{uuid4().hex}.jpg"
#     final_path = os.path.join(output_dir, output_filename)

#     # 3. Run postprocessing
#     postprocess = STYLE_CONFIG[model_name]["post"]
#     postprocess(stylized_path, final_path, use_superres=True)

#     return final_path
# styletransfer/inference.py
import os
from uuid import uuid4
from importlib import import_module

import torch
from PIL import Image
from django.conf import settings
import torchvision.transforms as T
import torchvision.transforms.functional as TF


# -------------------------
# Paths & device
# -------------------------
MODEL_DIR = os.path.join(settings.BASE_DIR, "styletransfer", "model")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Cache for loaded models
_MODEL_CACHE: dict[str, torch.nn.Module] = {}


# -------------------------
# Model loaders
# -------------------------
def _model_path(filename: str) -> str:
    p = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(p):
        raise FileNotFoundError(f"Model file not found: {p}")
    return p


def _load_with_generator(weight_path: str) -> torch.nn.Module:
    """Generic eager loader for your Generator-based checkpoints."""
    from styletransfer.model.generator import Generator  # local class
    net = Generator()
    state = torch.load(weight_path, map_location="cpu")
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    net.load_state_dict(state, strict=False)
    net.eval()
    net.to(DEVICE)
    return net


def load_anime_model() -> torch.nn.Module:
    """
    Prefer local anime.pth; fallback to AnimeGAN2 hub (face_paint_512_v2).
    """
    key = "anime"
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]

    local = os.path.join(MODEL_DIR, "anime.pth")
    if os.path.exists(local):
        net = _load_with_generator(local)
    else:
        # Fallback (requires internet on first run)
        net = torch.hub.load(
            "bryandlee/animegan2-pytorch:main",
            "generator",
            pretrained="face_paint_512_v2",
            map_location="cpu",
        )
        net.eval()
        net.to(DEVICE)

    _MODEL_CACHE[key] = net
    return net


def load_cyberverse_model() -> torch.nn.Module:
    key = "cyberverse"
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]
    net = _load_with_generator(_model_path("cyberVerse.pth"))
    _MODEL_CACHE[key] = net
    return net


def load_artbyai_model() -> torch.nn.Module:
    key = "artbyai"
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]
    # Note: your file is 'ArtByAi.pth' (casing matters on some OS)
    net = _load_with_generator(_model_path("ArtByAi.pth"))
    _MODEL_CACHE[key] = net
    return net


def load_vangogh_model() -> torch.nn.Module:
    key = "vangogh"
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]
    net = _load_with_generator(_model_path("vangogh.pth"))
    _MODEL_CACHE[key] = net
    return net


def load_oilpainting_model() -> torch.nn.Module:
    key = "oilpainting"
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]
    net = _load_with_generator(_model_path("OilPainting.pth"))
    _MODEL_CACHE[key] = net
    return net


# -------------------------
# Style registry
# -------------------------
# Support UI aliases (e.g., "cyberpunk" -> "cyberverse")
STYLE_ALIAS = {
    "cyberpunk": "cyberverse",
}

STYLE_CONFIG: dict[str, dict] = {
    "anime":       {"loader": load_anime_model,      "post_mod": "anime_postprocess",      "resize": (512, 512)},
    "cyberverse":  {"loader": load_cyberverse_model, "post_mod": "cyberverse_postprocess", "resize": (256, 256)},
    "artbyai":     {"loader": load_artbyai_model,    "post_mod": "artbyai_postprocess",     "resize": (256, 256)},
    "vangogh":     {"loader": load_vangogh_model,    "post_mod": "vangogh_postprocess",     "resize": (256, 256)},
    "oilpainting": {"loader": load_oilpainting_model,"post_mod": "oilpainting_postprocess", "resize": (256, 256)},
}


def _resolve_style(name: str) -> str:
    n = (name or "").lower()
    return STYLE_ALIAS.get(n, n)


# -------------------------
# Post-processing resolver
# -------------------------
def _get_post_fn(style_key: str):
    """
    Returns a callable like run_postprocessing(input_path, output_path, use_superres=True)
    from styletransfer.utils.<module>.
    """
    cfg = STYLE_CONFIG[style_key]
    module_name = cfg["post_mod"]  # e.g., "anime_postprocess"
    mod = import_module(f"styletransfer.utils.{module_name}")
    fn = getattr(mod, "run_postprocessing", None)
    if not callable(fn):
        # fallbacks: let your module export different names if needed
        for cand in ("postprocess", "apply", "enhance", "run"):
            fn = getattr(mod, cand, None)
            if callable(fn):
                break
    if not callable(fn):
        raise AttributeError(
            f"Postprocess function not found in utils.{module_name}. "
            f"Expected run_postprocessing(img_in, img_out, use_superres=True)"
        )
    return fn


# -------------------------
# Core transforms
# -------------------------
def _make_transform(size_xy: tuple[int, int]) -> T.Compose:
    """
    Transform: resize -> tensor -> normalize to [-1,1] channel-wise (0.5/0.5).
    """
    return T.Compose([
        T.Resize(size_xy, interpolation=T.InterpolationMode.BICUBIC, antialias=True),
        T.ToTensor(),
        T.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])


# -------------------------
# Inference helpers
# -------------------------
@torch.inference_mode()
def _forward(model: torch.nn.Module, x: torch.Tensor) -> torch.Tensor:
    y = model(x)
    if isinstance(y, (list, tuple)):
        y = y[0]
    return y


def _denorm_to_pil(t: torch.Tensor) -> Image.Image:
    # model output expected in [-1,1]; convert to [0,1]
    t = ((t.detach().cpu() + 1.0) / 2.0).clamp(0.0, 1.0)
    return TF.to_pil_image(t.squeeze(0))


# -------------------------
# Public API
# -------------------------
@torch.inference_mode()
def apply_style(input_image_path: str, model_loader, size_xy: tuple[int, int]) -> str:
    """
    Run the model and save a RAW stylized image to MEDIA_ROOT/output/raw_*.jpg.
    Returns absolute path to the raw stylized image.
    """
    # Load image
    img = Image.open(input_image_path).convert("RGB")

    # Transform & batch
    transform = _make_transform(size_xy)
    x = transform(img).unsqueeze(0).to(DEVICE)

    # Model
    model = model_loader()
    model.to(DEVICE).eval()

    # Forward
    y = _forward(model, x)

    # To PIL
    out_pil = _denorm_to_pil(y)

    # Save raw stylized file
    out_dir = os.path.join(settings.MEDIA_ROOT, "output")
    os.makedirs(out_dir, exist_ok=True)
    raw_name = f"raw_{uuid4().hex}.jpg"
    raw_path = os.path.join(out_dir, raw_name)
    out_pil.save(raw_path, quality=92)

    return raw_path


def run_inference_with_postprocessing(input_image_path: str, model_name: str = "anime",
                                      use_superres: bool = True) -> str:
    """
    High-level entry:
      - resolves style
      - loads/caches model
      - runs inference (RAW save)
      - calls your utils.<style>_postprocess.run_postprocessing
      - returns absolute final path under MEDIA_ROOT/output
    """
    style_key = _resolve_style(model_name)
    if style_key not in STYLE_CONFIG:
        raise ValueError(f"Unsupported style '{model_name}'. Supported: {list(STYLE_CONFIG)}")

    cfg = STYLE_CONFIG[style_key]
    loader = cfg["loader"]
    size = cfg["resize"]
    if isinstance(size, int):
        size = (size, size)

    # 1) stylize -> raw file
    raw_path = apply_style(input_image_path, loader, size)

    # 2) final output path
    out_dir = os.path.join(settings.MEDIA_ROOT, "output")
    os.makedirs(out_dir, exist_ok=True)
    final_path = os.path.join(out_dir, f"styled_{uuid4().hex}.jpg")

    # 3) post-process (your module owns sharpening/denoise/ESRGAN, etc.)
    post_fn = _get_post_fn(style_key)
    post_fn(raw_path, final_path, use_superres=use_superres)

    return final_path
