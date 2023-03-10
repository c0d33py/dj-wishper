import os
import io
import argparse
from queue import Queue
from sys import platform
from tempfile import NamedTemporaryFile

import speech_recognition as sr


def mic_hardware():
    # The last time a recording was retreived from the queue.
    phrase_time = None
    # Current raw audio bytes.
    last_sample = bytes()
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feauture where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = 1000  # energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramtically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    if 'linux' in platform:

        source = sr.Microphone(sample_rate=16000)
        record_timeout = 2  # record_timeout
        phrase_timeout = 3  # phrase_timeout

        temp_file = NamedTemporaryFile().name
        transcription = ['']

        with source:
            recorder.adjust_for_ambient_noise(source)

        def record_callback(_, audio: sr.AudioData) -> None:
            """
            Threaded callback function to recieve audio data when recordings finish.
            audio: An AudioData containing the recorded bytes.
            """
            # Grab the raw bytes and push it into the thread safe queue.
            data = audio.get_raw_data()
            data_queue.put(data)

        # Create a background thread that will pass us raw audio bytes.
        # We could do this manually but SpeechRecognizer provides a nice helper.
        recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

        # Cue the user that we're ready to go.
        print("Model loaded.\n")
