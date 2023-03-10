

from rest_framework import serializers
from django.core.validators import FileExtensionValidator

from .models import MediaField


class FileSerializer(serializers.ModelSerializer):
    upload_file = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['mp3', 'mp4'])])

    class Meta:
        model = MediaField
        fields = ('id', 'transcript', 'upload_file')
        read_only_fields = ['transcript', ]
