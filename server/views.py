from django.shortcuts import render
from django.http import JsonResponse
import os
import whisper

model = whisper.load_model("base")


def index(request):
    ''' Initial page render '''
    return render(request, 'index.html')


def wishper_json_api(request):
    ''' Wishper speach to text '''

    # load audio and pad/trim it to fit 30 seconds
    audio = os.path.join('assets/audio/wh.mp4')
    result = model.transcribe(audio, language='urdu')

    return JsonResponse(result['text'], safe=False)
