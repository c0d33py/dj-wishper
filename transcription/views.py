from django.shortcuts import render
# login required decorator
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, pagination

from .models import MediaField
from .serializers import FileSerializer


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 50


@login_required
def index(request):
    ''' Initial page render '''
    return render(request, 'index.html')


class MediaFieldAPIView(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    queryset = MediaField.objects.all()
    pagination_class = CustomPagination