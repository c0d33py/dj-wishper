from rest_framework import serializers

from .models import MediaField


class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediaField
        fields = '__all__'

    def create(self, validated_data):
        return MediaField.objects.create(**validated_data)
