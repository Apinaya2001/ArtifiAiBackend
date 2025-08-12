# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# # from django.conf import settings
# # import os
# # from uuid import uuid4
# # from .inference import run_inference_with_postprocessing

# # @api_view(['POST'])
# # def style_transfer_view(request):
# #     image_file = request.FILES.get('image')
# #     model_name = request.data.get('model')  # 'anime', 'vangogh', etc.

# #     if not image_file or not model_name:
# #         return Response({'error': 'Image and model are required'}, status=400)

# #     # Save input
# #     input_dir = os.path.join(settings.MEDIA_ROOT, "input")
# #     os.makedirs(input_dir, exist_ok=True)
# #     input_path = os.path.join(input_dir, f"{uuid4().hex}.jpg")

# #     with open(input_path, 'wb+') as f:
# #         for chunk in image_file.chunks():
# #             f.write(chunk)

# #     # Run inference
# #     final_output_path = run_inference_with_postprocessing(input_path, model_name)

# #     # Return URL
# #     final_filename = os.path.basename(final_output_path)
# #     final_url = request.build_absolute_uri(settings.MEDIA_URL + "output/" + final_filename)
# #     return Response({'output_url': final_url})
# # styletransfer/views.py
# from rest_framework.decorators import api_view, permission_classes, parser_classes
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage
# from django.utils import timezone
# import os

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser, FormParser])
# def style_transfer_view(request):
#     img = request.FILES.get("image")
#     if not img:
#         return Response({"error": "image is required"}, status=400)
#     style = request.data.get("style", "anime")

#     # --- dummy processing: save a copy to /media/outputs so the URL works ---
#     ts = timezone.now().strftime("%Y%m%d%H%M%S")
#     in_rel = f"inputs/{ts}_{img.name}"
#     default_storage.save(in_rel, ContentFile(img.read()))

#     base, ext = os.path.splitext(os.path.basename(in_rel))
#     out_rel = f"outputs/{base}_{style}{ext}"
#     with default_storage.open(in_rel, "rb") as f:
#         default_storage.save(out_rel, ContentFile(f.read()))
#     # ------------------------------------------------------------------------

#     return Response({"output_url": f"/media/{out_rel}"}, status=200)
# styletransfer/views.py
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from django.conf import settings
from django.utils import timezone

import os
from .inference import run_inference_with_postprocessing

# Map UI dropdown values to your internal model keys
STYLE_MAP = {
    "anime": "anime",
    "cyberpunk": "cyberverse",
     "cyberverse": "cyberverse",
    "artbyai": "artbyai",
     "artibi": "artbyai",
    "vangogh": "vangogh",
    "oilpainting": "oilpainting",
}

FREE_STYLES = {"anime", "artbyai"}  # free on marketing

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def style_transfer_view(request):
    """
    Expects multipart/form-data with:
      - image: file
      - style: anime|cyberpunk|artbyai|vangogh|oilpainting
      - (optional) use_superres: "true"/"false"
    Returns: {"output_url": "/media/output/....jpg"}
    """
    f = request.FILES.get("image")
    if not f:
        return Response({"error": "image is required"}, status=status.HTTP_400_BAD_REQUEST)

    ui_style = (request.data.get("style") or "anime").lower()
    model_name = STYLE_MAP.get(ui_style, ui_style)

    # Save uploaded image to MEDIA/inputs
    inputs_dir = os.path.join(settings.MEDIA_ROOT, "inputs")
    os.makedirs(inputs_dir, exist_ok=True)
    ts = timezone.now().strftime("%Y%m%d%H%M%S")
    base, _ = os.path.splitext(f.name or "upload")
    in_rel = f"inputs/{base}_{ts}.jpg"
    in_abs = os.path.join(settings.MEDIA_ROOT, in_rel)

    with open(in_abs, "wb") as dst:
        for chunk in f.chunks():
            dst.write(chunk)

    # Optional flag from client
    use_superres = str(request.data.get("use_superres", "true")).lower() in ("1", "true", "yes")

    try:
        out_abs = run_inference_with_postprocessing(in_abs, model_name=model_name, use_superres=use_superres)
    except FileNotFoundError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"inference_failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Convert absolute path to MEDIA_URL for the frontend
    rel_from_media = os.path.relpath(out_abs, settings.MEDIA_ROOT).replace(os.sep, "/")
    return Response({"output_url": f"{settings.MEDIA_URL}{rel_from_media}"}, status=status.HTTP_200_OK)
