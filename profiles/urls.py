# profiles/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet
router = DefaultRouter()
router.register('', ProfileViewSet, basename='profiles')
urlpatterns = router.urls
