from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register('files', MediaFieldAPIView)


urlpatterns = [
    path('', index, name='home-page'),
    path('api/', include(router.urls)),
]
