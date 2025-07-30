from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django.http import JsonResponse
from django.conf import settings

import os
import uuid
import logging

# from .utils.inference import load_model, style_transfer
from styletransfer.utils.inference import load_model, style_transfer

# Setup logger
logger = logging.getLogger(__name__)

# Constants
STYLE_MODEL_MAP = {
    'vintage': 'latest_net_G.pth',
    'vangogh': 'vangogh_stylized_output.pth',
    # Add more styles as needed
}

MEDIA_INPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'input')
MEDIA_OUTPUT_DIR = os.path.join(settings.MEDIA_ROOT, 'output')

# Ensure directories exist
os.makedirs(MEDIA_INPUT_DIR, exist_ok=True)
os.makedirs(MEDIA_OUTPUT_DIR, exist_ok=True)

# Load models at startup
loaded_models = {}
for style, filename in STYLE_MODEL_MAP.items():
    try:
        model_path = os.path.join(settings.BASE_DIR, 'styletransfer', 'model', filename)
        loaded_models[style] = load_model(model_path)
        logger.info(f"✅ Loaded model for style '{style}' from {filename}")
    except Exception as e:
        loaded_models[style] = None
        logger.error(f"❌ Failed to load model for style '{style}': {e}")

class StyleTransferView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        logger.info("🔵 Received POST request for style transfer")

        selected_style = request.data.get('style')
        if selected_style not in STYLE_MODEL_MAP:
            return JsonResponse({'error': 'Invalid style selected'}, status=400)

        model = loaded_models.get(selected_style)
        if model is None:
            return JsonResponse({'error': f'Model for style "{selected_style}" not loaded'}, status=500)

        image_file = request.FILES.get('image')
        if not image_file:
            return JsonResponse({'error': 'No image file provided'}, status=400)

        filename = f"{uuid.uuid4()}.jpg"
        input_path = os.path.join(MEDIA_INPUT_DIR, filename)
        output_path = os.path.join(MEDIA_OUTPUT_DIR, filename)

        try:
            with open(input_path, 'wb+') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
        except Exception as e:
            logger.error(f"❌ Failed to save input image: {e}")
            return JsonResponse({'error': f'Failed to save input image: {str(e)}'}, status=500)

        try:
            style_transfer(model, input_path, output_path)
            output_url = request.build_absolute_uri(f'/media/output/{filename}')
            return JsonResponse({'output_url': output_url})
        except Exception as e:
            logger.error(f"❌ Style transfer failed: {e}")
            return JsonResponse({'error': f'Style transfer failed: {str(e)}'}, status=500)
