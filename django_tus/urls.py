from django.urls import path

from .views import TusUpload, TusUploadDelete

urlpatterns = [
    path('upload/', TusUpload.as_view(), name='tus_upload'),
    path('upload/<uuid:resource_id>', TusUpload.as_view(), name='tus_upload'),
    path('upload/delete/<uuid:resource_id>', TusUploadDelete.as_view(), name='tus_upload_delete'),
]
