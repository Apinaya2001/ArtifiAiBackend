
# # # styletransfer/views.py
# # from rest_framework.decorators import api_view, permission_classes, parser_classes
# # from rest_framework.permissions import IsAuthenticated
# # from rest_framework.parsers import MultiPartParser, FormParser
# # from rest_framework.response import Response
# # from rest_framework import status

# # from django.conf import settings
# # from django.utils import timezone

# # import os
# # from .inference import run_inference_with_postprocessing

# # # Map UI dropdown values to your internal model keys
# # STYLE_MAP = {
# #     "anime": "anime",
# #     "cyberpunk": "cyberverse",
# #     "artbyai": "artbyai",
# #     "vangogh": "vangogh",
# #     "oilpainting": "oilpainting",
# # }

# # @api_view(["POST"])
# # @permission_classes([IsAuthenticated])
# # @parser_classes([MultiPartParser, FormParser])
# # def style_transfer_view(request):
# #     """
# #     Expects multipart/form-data with:
# #       - image: file
# #       - style: anime|cyberpunk|artbyai|vangogh|oilpainting
# #       - (optional) use_superres: "true"/"false"
# #     Returns: {"output_url": "/media/output/....jpg"}
# #     """
# #     f = request.FILES.get("image")
# #     if not f:
# #         return Response({"error": "image is required"}, status=status.HTTP_400_BAD_REQUEST)

# #     ui_style = (request.data.get("style") or "anime").lower()
# #     model_name = STYLE_MAP.get(ui_style, ui_style)

# #     # Save uploaded image to MEDIA/inputs
# #     inputs_dir = os.path.join(settings.MEDIA_ROOT, "inputs")
# #     os.makedirs(inputs_dir, exist_ok=True)
# #     ts = timezone.now().strftime("%Y%m%d%H%M%S")
# #     base, _ = os.path.splitext(f.name or "upload")
# #     in_rel = f"inputs/{base}_{ts}.jpg"
# #     in_abs = os.path.join(settings.MEDIA_ROOT, in_rel)

# #     with open(in_abs, "wb") as dst:
# #         for chunk in f.chunks():
# #             dst.write(chunk)

# #     # Optional flag from client
# #     use_superres = str(request.data.get("use_superres", "true")).lower() in ("1", "true", "yes")

# #     try:
# #         out_abs = run_inference_with_postprocessing(in_abs, model_name=model_name, use_superres=use_superres)
# #     except FileNotFoundError as e:
# #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# #     except Exception as e:
# #         return Response({"error": f"inference_failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# #     # Convert absolute path to MEDIA_URL for the frontend
# #     rel_from_media = os.path.relpath(out_abs, settings.MEDIA_ROOT).replace(os.sep, "/")
# #     return Response({"output_url": f"{settings.MEDIA_URL}{rel_from_media}"}, status=status.HTTP_200_OK)


# from rest_framework.decorators import api_view, permission_classes, parser_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework import status
# from django.conf import settings
# from django.utils import timezone
# import os

# from .inference import run_inference_with_postprocessing

# FREE_STYLES = {"anime", "artbyai"}  # free on marketing
# STYLE_MAP = {
#     "anime": "anime",
#     "artbyai": "artbyai",
#     "cyberpunk": "cyberverse",
#     "cyberverse": "cyberverse",
#     "vangogh": "vangogh",
#     "oilpainting": "oilpainting",
# }

# @api_view(["POST"])
# @permission_classes([AllowAny])                 # <-- IMPORTANT
# @parser_classes([MultiPartParser, FormParser])
# def style_transfer_view(request):
#     img = request.FILES.get("image")
#     style = (request.data.get("style") or request.data.get("model") or "").lower()
#     if not img or not style:
#         return Response({"error": "image and style are required"}, status=400)

#     if (not request.user.is_authenticated) and (style not in FREE_STYLES):
#         return Response({"detail": "Login required for this style"}, status=401)

#     model_name = STYLE_MAP.get(style, style)

#     inputs_dir = os.path.join(settings.MEDIA_ROOT, "inputs")
#     os.makedirs(inputs_dir, exist_ok=True)
#     ts = timezone.now().strftime("%Y%m%d%H%M%S")
#     base, _ = os.path.splitext(img.name or "upload")
#     in_abs = os.path.join(settings.MEDIA_ROOT, f"inputs/{base}_{ts}.jpg")
#     with open(in_abs, "wb") as dst:
#         for chunk in img.chunks():
#             dst.write(chunk)

#     use_superres = str(request.data.get("use_superres", "true")).lower() in ("1", "true", "yes")

#     try:
#         out_abs = run_inference_with_postprocessing(in_abs, model_name=model_name, use_superres=use_superres)
#     except FileNotFoundError as e:
#         return Response({"error": str(e)}, status=400)
#     except Exception as e:
#         return Response({"error": f"inference_failed: {e}"}, status=500)

#     rel = os.path.relpath(out_abs, settings.MEDIA_ROOT).replace(os.sep, "/")
#     return Response({"output_url": f"{settings.MEDIA_URL}{rel}"}, status=200)




# styletransfer/views.py
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.utils import timezone
from django.utils.text import get_valid_filename

from .models import StylizedImage
from .inference import run_inference_with_postprocessing

import logging
import os

log = logging.getLogger(__name__)

# Public styles that don’t require auth
FREE_STYLES = {"anime", "artbyai"}

# UI aliases → internal keys (kept for convenience)
STYLE_MAP = {
    "anime": "anime",
    "artbyai": "artbyai",
    "cyberpunk": "cyberverse",
    "cyberverse": "cyberverse",
    "vangogh": "vangogh",
    "oilpainting": "oilpainting",
}

ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp"}
MAX_UPLOAD_MB = 20


def _ensure_dir(name: str) -> str:
    """Ensure MEDIA_ROOT/name exists; return its absolute path."""
    root = getattr(settings, "MEDIA_ROOT", None)
    if not root:
        raise RuntimeError("MEDIA_ROOT is not configured.")
    path = os.path.join(root, name)
    os.makedirs(path, exist_ok=True)
    return path


def _rel(path_abs: str) -> str:
    """Absolute → MEDIA-relative with forward slashes."""
    return os.path.relpath(path_abs, settings.MEDIA_ROOT).replace(os.sep, "/")


def _ext_from(name: str, default="jpg") -> str:
    ext = os.path.splitext(name or "")[1].lower().lstrip(".")
    return ext if ext in ALLOWED_EXTS else default


def _boolish(v, default=True) -> bool:
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}


@api_view(["POST", "GET"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def style_transfer_view(request):
    """
    POST: run style transfer, save files+DB row, return URLs
    GET : quick list of recent rows (debug) ?limit=10
    """
    if request.method == "GET":
        limit = int(request.query_params.get("limit", 10))
        qs = StylizedImage.objects.order_by("-id")[:max(1, min(limit, 100))]
        data = [
            {
                "id": r.id,
                "model": r.model_used,
                "original_url": f"{settings.MEDIA_URL}{r.original_image}",
                "output_url": f"{settings.MEDIA_URL}{r.styled_image}",
                "created_at": r.created_at,
            }
            for r in qs
        ]
        return Response(data, status=200)

    # --------- POST ---------
    img = request.FILES.get("image")
    style = (request.data.get("style") or request.data.get("model") or "").strip().lower()

    if not img or not style:
        return Response({"error": "image and style are required"}, status=400)

    # gating: only FREE_STYLES allowed without login
    if (not request.user.is_authenticated) and (style not in FREE_STYLES):
        return Response({"detail": "Login required for this style"}, status=401)

    model_name = STYLE_MAP.get(style, style)

    # size guard
    if getattr(img, "size", 0) and img.size > MAX_UPLOAD_MB * 1024 * 1024:
        return Response({"error": f"image too large (>{MAX_UPLOAD_MB} MB)"}, status=413)

    # save input to MEDIA_ROOT/input/...
    input_dir_abs = _ensure_dir("input")    # <-- singular to match your model/inference
    output_dir_abs = _ensure_dir("output")  # <-- singular to match your inference

    ts = timezone.now().strftime("%Y%m%d%H%M%S")
    safe_base = os.path.splitext(get_valid_filename(img.name or "upload"))[0] or "upload"
    ext = _ext_from(img.name, default="jpg")

    in_filename = f"{safe_base}_{ts}.{ext}"
    in_abs = os.path.join(input_dir_abs, in_filename)

    try:
        with open(in_abs, "wb") as dst:
            for chunk in img.chunks():
                dst.write(chunk)
    except Exception as e:
        log.exception("Failed to write input file")
        return Response({"error": f"failed_to_save_input: {e}"}, status=500)

    # run inference (returns absolute path under MEDIA_ROOT/output)
    use_superres = _boolish(request.data.get("use_superres"), default=True)
    try:
        out_abs = run_inference_with_postprocessing(
            in_abs, model_name=model_name, use_superres=use_superres
        )
    except FileNotFoundError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        log.exception("Inference failed")
        return Response({"error": f"inference_failed: {e}"}, status=500)

    # sanity: ensure output actually under MEDIA_ROOT/output
    if not os.path.abspath(out_abs).startswith(os.path.abspath(output_dir_abs)):
        # if your postprocess wrote elsewhere, move it into /output with a stable name
        out_filename = f"styled_{safe_base}_{ts}.{ext}"
        fixed_abs = os.path.join(output_dir_abs, out_filename)
        try:
            # copy/rename
            with open(out_abs, "rb") as src, open(fixed_abs, "wb") as dst:
                dst.write(src.read())
            out_abs = fixed_abs
        except Exception as e:
            log.exception("Failed moving output into MEDIA_ROOT/output")
            return Response({"error": f"failed_to_save_output: {e}"}, status=500)

    # relative paths for ImageFields (so Django won’t re-write files)
    in_rel = _rel(in_abs)     # e.g., "input/foo_20250811.jpg"
    out_rel = _rel(out_abs)   # e.g., "output/styled_abc.jpg"

    # CREATE THE ROW
    try:
        rec = StylizedImage.objects.create(
            original_image=in_rel,
            styled_image=out_rel,
            model_used=model_name,
        )
    except Exception as e:
        log.exception("DB insert failed")
        return Response({"error": f"db_insert_failed: {e}"}, status=500)

    return Response(
        {
            "id": rec.id,
            "model": rec.model_used,
            "original_url": f"{settings.MEDIA_URL}{in_rel}",
            "output_url": f"{settings.MEDIA_URL}{out_rel}",
            "created_at": rec.created_at,
        },
        status=status.HTTP_201_CREATED,
    )
