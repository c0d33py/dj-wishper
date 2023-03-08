from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.shortcuts import render
from django.http import JsonResponse
import os
import whisper

from .input import mic_hardware

model = whisper.load_model("base")


def index(request):
    ''' Initial page render '''
    return render(request, 'index.html')


def wishper_json_api(request):
    ''' Wishper speach to text '''
    mic_hardware()
    # load audio and pad/trim it to fit 30 seconds
    audio = os.path.join('assets/audio/wh.mp4')
    # result = model.transcribe(audio, language='urdu')

    return JsonResponse(None, safe=False)


# views.py


@csrf_exempt
@require_POST
def transcription(request):
    data = json.loads(request.body)
    transcript = data['transcript']
    # Do something with the transcript, such as store it in a database or process it
    return HttpResponse(status=200)
