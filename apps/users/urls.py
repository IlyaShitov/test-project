from rest_framework.routers import SimpleRouter

from apps.users import views

router = SimpleRouter()

router.register('', views.UserViewSet)

urlpatterns = router.urls
