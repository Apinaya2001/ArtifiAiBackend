# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import path, include

# urlpatterns = [
#     path('api/', include('styletransfer.urls')),  # Add this if not already
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ArtifiAiBackend/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/style-transfer/', include('styletransfer.urls')), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
