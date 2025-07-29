from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.conf import settings
from django.http import JsonResponse
import os
import uuid

from .utils.inference import load_model, style_transfer

# Load model once when the app starts
MODEL_PATH = os.path.join(settings.BASE_DIR, 'styletransfer/model/latest_net_G.pth')
try:
    model = load_model(MODEL_PATH)
except Exception as e:
    model = None
    print(f"Failed to load model: {e}")

class StyleTransferView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        if model is None:
            return JsonResponse({'error': 'Model not loaded'}, status=500)

        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'error': 'No image file provided'}, status=400)

        # Generate unique file paths
        filename = f"{uuid.uuid4()}.jpg"
        input_dir = os.path.join(settings.MEDIA_ROOT, 'input')
        output_dir = os.path.join(settings.MEDIA_ROOT, 'output')
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Ensure directories exist
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Save uploaded image
        try:
            with open(input_path, 'wb+') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
        except Exception as e:
            return JsonResponse({'error': f'Failed to save input image: {str(e)}'}, status=500)

        # Run style transfer
        try:
            style_transfer(model, input_path, output_path)
            output_url = request.build_absolute_uri(f'/media/output/{filename}')
            return JsonResponse({'output_url': output_url})
        except Exception as e:
            return JsonResponse({'error': f'Style transfer failed: {str(e)}'}, status=500)
