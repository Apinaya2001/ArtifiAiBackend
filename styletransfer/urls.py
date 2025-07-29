from django.urls import path
from .views import StyleTransferView  # ✅ Correct

urlpatterns = [
    path('style/transfer/', StyleTransferView.as_view(), name='style_transfer'),  # ✅ FIXED
]
