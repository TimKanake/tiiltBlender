# Adapted from https://github.com/Uberi/speech_recognition/blob/master/examples/audio_transcribe.py

from __future__ import print_function

import speech_recognition as sr
import api
import time
from pocketsphinx.pocketsphinx import *
import os

# obtain path to "speech_sample.wav" in the same folder as this script
from os import path
AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "sample_speech.wav")

# use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source) # read the entire audio file

begin = time.time()
try:
    MODELDIR = "libraries/pocketsphinx/model"
    config = Decoder.default_config()
    config.set_string('-logfn', '/dev/null')
    config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
    config.set_string('-lm', os.path.join(MODELDIR,'en-us/en-us.lm.bin'))
    config.set_string('-dict', os.path.join(MODELDIR,'en-us/cmudict-en-us.dict'))
    decoder = Decoder(config)
    decoder.start_utt()
    stream = open(AUDIO_FILE, "rb")
    while True:
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
        else:
            break
    decoder.end_utt()
    words = []
    # [words.append(seg.word) for seg in self.decoder.seg()]
    hypothesis = decoder.hyp()
    for best, i in zip(decoder.nbest(), range(1)):
        words.append(best.hypstr + ' -- model score: ' + str(best.score))
    print("Pocketsphinx thinks you said " + words[0])
except:
    print("Pocketsphinx error")
print("It took ", (time.time() - begin), " seconds")

begin = time.time()
# recognize speech using Sphinx
try:
    print("Sphinx thinks you said " + r.recognize_sphinx(audio))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))
print("It took ", (time.time() - begin), " seconds")

begin = time.time()
# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))
print("It took ", (time.time() - begin), " seconds")

begin = time.time()
# recognize speech using Google Cloud Speech
GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
try:
    print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS))
except sr.UnknownValueError:
    print("Google Cloud Speech could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Cloud Speech service; {0}".format(e))
print("It took ", (time.time() - begin), " seconds")

begin = time.time()
# recognize speech using Wit.ai
WIT_AI_KEY = "INSERT WIT.AI API KEY HERE" # Wit.ai keys are 32-character uppercase alphanumeric strings
try:
    print("Wit.ai thinks you said " + r.recognize_wit(audio, key=WIT_AI_KEY))
except sr.UnknownValueError:
    print("Wit.ai could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Wit.ai service; {0}".format(e))
print("It took ", (time.time() - begin), " seconds")

begin = time.time()
# recognize speech using Microsoft Bing Voice Recognition
BING_KEY = "INSERT BING API KEY HERE" # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
try:
    print("Microsoft Bing Voice Recognition thinks you said " + r.recognize_bing(audio, key=api.MICROSOFT_APIKEY))
except sr.UnknownValueError:
    print("Microsoft Bing Voice Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))
print("It took ", (time.time() - begin), " seconds")

begin = time.time()
# recognize speech using IBM Speech to Text
IBM_USERNAME = "INSERT IBM SPEECH TO TEXT USERNAME HERE" # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
IBM_PASSWORD = "INSERT IBM SPEECH TO TEXT PASSWORD HERE" # IBM Speech to Text passwords are mixed-case alphanumeric strings
try:
    print("IBM Speech to Text thinks you said " + r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD))
except sr.UnknownValueError:
    print("IBM Speech to Text could not understand audio")
except sr.RequestError as e:
    print("Could not request results from IBM Speech to Text service; {0}".format(e))
print("It took ", (time.time() - begin), " seconds")
