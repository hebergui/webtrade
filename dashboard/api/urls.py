from django.urls import include, path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
#Block
router.register(r'companies', views.CompanyViewSet)
router.register(r'indicators', views.IndicatorViewSet)
#Block
router.register(r'blocks', views.BlockViewSet)
router.register(r'headers', views.HeaderViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
