from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.shortcuts import render
from django.http import JsonResponse
import os
import whisper


model = whisper.load_model("base")


def index(request):
    ''' Initial page render '''
    return render(request, 'index.html')


# def wishper_json_api(request):
#     ''' Wishper speach to text '''
#     # load audio and pad/trim it to fit 30 seconds
#     audio = os.path.join('assets/files/sample.mp3')
#     result = model.transcribe(audio)

#     return JsonResponse(result['text'], safe=False)


# @csrf_exempt
# @require_POST
# def transcription(request):
#     data = json.loads(request.body)
#     transcript = data['transcript']
#     # Do something with the transcript, such as store it in a database or process it
#     return HttpResponse(status=200)
