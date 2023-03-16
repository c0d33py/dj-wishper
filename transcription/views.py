from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.shortcuts import render
from django.http import JsonResponse
import os
import whisper

from rest_framework import viewsets, pagination

from .models import MediaField
from .serializers import FileSerializer

model = whisper.load_model("large")


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 50


def index(request):
    ''' Initial page render '''
    return render(request, 'index.html')


class MediaFieldAPIView(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    queryset = MediaField.objects.all()
    pagination_class = CustomPagination
