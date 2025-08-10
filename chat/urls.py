# chat/urls.py
from rest_framework.routers import DefaultRouter
from .views import ThreadViewSet
router = DefaultRouter()
router.register('', ThreadViewSet, basename='threads')
urlpatterns = router.urls
