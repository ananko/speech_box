import argparse
import tempfile
import subprocess
import os
from gtts import gTTS
from pydub import AudioSegment
from nltk.chat import eliza
import pyaudio
import wave
import collections
import math
import audioop
import json
import requests

class Recognizer():

  def __init__(self, language = "en-US", key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"):

    self.key = key
    self.language = language
    self.url = 'http://www.google.com/speech-api/v2/recognize?client=chromium&lang=%s&key=%s' % (self.language, self.key)

  def recognize(self, audio_segment):
    assert isinstance(audio_segment, AudioSegment)

    level, tmp_file_name = tempfile.mkstemp()
    res = audio_segment.export(tmp_file_name, format = 'wav')
    res = subprocess.call('flac %s -s -f -o %s' %(tmp_file_name, tmp_file_name), shell = True)

    headers = {"Content-Type": "audio/x-flac; rate=%s" % audio_segment.frame_rate}
    with open(tmp_file_name, 'rb') as f:
      data = f.read()
    response = requests.post(self.url, headers = headers, data = data)
    res = []
    for line in response.text.strip('\n').split('\n'):
      jres = json.loads(line)['result']
      if len(jres) == 0:
        continue
      res.extend(jres)

    if not res:
      return None
    res = res[0]
    alternative = res['alternative']
    best_res = alternative[0]
    #print(best_res['transcript'])
    os.remove(tmp_file_name)
    return best_res['transcript']

class Microphone():

  def __init__(self):
    self.CHUNK = 1024
    self.FORMAT = pyaudio.paInt16
    self.CHANNELS = 2
    self.RATE = 44100
    self.SAMPLE_WIDTH = pyaudio.get_sample_size(self.FORMAT)

    self.energy_threshold = 1500
    self.pause_threshold = 0.8
    self.quiet_duration = 0.5

    self.seconds_per_buffer = self.CHUNK / self.RATE
    self.pause_buffer_count = math.ceil(self.pause_threshold / self.seconds_per_buffer)
    self.quiet_buffer_count = math.ceil(self.quiet_duration / self.seconds_per_buffer)

  def listen(self, file_name = 'output.wav'):
    p = pyaudio.PyAudio()
    stream = p.open(format = self.FORMAT,
                    channels = self.CHANNELS,
                    rate = self.RATE,
                    input = True,
                    frames_per_buffer = self.CHUNK)

    frames = collections.deque()

    while True:
      buf = stream.read(self.CHUNK)
      if len(buf) == 0:
        break
      frames.append(buf)

      energy = audioop.rms(buf, self.SAMPLE_WIDTH)
      print(energy)
      if energy > self.energy_threshold:
        break
      if len(frames) > self.quiet_buffer_count:
        frames.popleft()

    print('Energy is above the threshold')

    pause_count = 0
    while True:
      buf = stream.read(self.CHUNK)
      if len(buf) == 0:
        break
      frames.append(buf)

      energy = audioop.rms(buf, self.SAMPLE_WIDTH)
      print (energy)
      if energy > self.energy_threshold:
        pause_count = 0
      else:
        pause_count += 1
      if pause_count > self.pause_buffer_count:
        break

    for i in range(self.quiet_buffer_count, self.pause_buffer_count):
      frames.pop()
    frame_data = b"".join(list(frames))

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(file_name, 'wb')
    wf.setnchannels(self.CHANNELS)
    wf.setsampwidth(p.get_sample_size(self.FORMAT))
    wf.setframerate(self.RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

r = Recognizer()
mic = Microphone()

def listen():
  level, tmp_file_name = tempfile.mkstemp(suffix = '.wav')
  mic.listen(tmp_file_name)
  audio_segment = AudioSegment.from_file(tmp_file_name, 'wav')
  resp = r.recognize(audio_segment)
  print(resp)
  return resp

  return input('--> ')

def say(text = None):
  if not text:
    return
  tts = gTTS(text = text, lang = 'en')
  level, tmp_response_from_tts = tempfile.mkstemp(suffix = '.mp3')
  tts.save(tmp_response_from_tts)
  res = subprocess.call('play -V1 %s' %(tmp_response_from_tts),
                        shell = True,
                        stdout = subprocess.DEVNULL,
                        stderr = subprocess.DEVNULL)
  os.remove(tmp_response_from_tts)

def main():
    parser = argparse.ArgumentParser(description = 'input wav generator')

    args = parser.parse_args()

    silence_duration_ms = 1000
    silence = AudioSegment.silent(silence_duration_ms)

    chatbot = eliza.eliza_chatbot
    chatbot_input = ''
    chatbot_response = 'hello'
    while chatbot_input not in ('bye', 'goodbye'):
      say(chatbot_response)

      chatbot_input = listen()
      if not chatbot_input:
        chatbot_response = None
        continue
      chatbot_response = chatbot.respond(chatbot_input)


    say('see you')

def main1():
  mic.listen()

if __name__ == '__main__':
    main()
