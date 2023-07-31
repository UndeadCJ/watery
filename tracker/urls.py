from rest_framework.routers import DefaultRouter

from tracker.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
urlpatterns = router.urls
