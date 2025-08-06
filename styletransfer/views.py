from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import os
from uuid import uuid4
from .inference import run_inference_with_postprocessing

@api_view(['POST'])
def style_transfer_view(request):
    image_file = request.FILES.get('image')
    model_name = request.data.get('model')  # 'anime', 'vangogh', etc.

    if not image_file or not model_name:
        return Response({'error': 'Image and model are required'}, status=400)

    # Save input
    input_dir = os.path.join(settings.MEDIA_ROOT, "input")
    os.makedirs(input_dir, exist_ok=True)
    input_path = os.path.join(input_dir, f"{uuid4().hex}.jpg")

    with open(input_path, 'wb+') as f:
        for chunk in image_file.chunks():
            f.write(chunk)

    # Run inference
    final_output_path = run_inference_with_postprocessing(input_path, model_name)

    # Return URL
    final_filename = os.path.basename(final_output_path)
    final_url = request.build_absolute_uri(settings.MEDIA_URL + "output/" + final_filename)
    return Response({'output_url': final_url})
