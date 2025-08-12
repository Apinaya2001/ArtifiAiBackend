
# from rest_framework.routers import DefaultRouter
# from .views import ProfileViewSet
# router = DefaultRouter()
# router.register('', ProfileViewSet, basename='profiles')
# urlpatterns = router.urls

# # profiles/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet
app_name = "profiles"
router = DefaultRouter()
router.register(r"", ProfileViewSet, basename="profiles")
urlpatterns = router.urls
