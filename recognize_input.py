import argparse
import requests
import tempfile
import os
import subprocess
import json
from pydub import AudioSegment

class Recognizer():

  def __init__(self, language = "en-US", key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"):

    self.key = key
    self.language = language
    self.url = 'http://www.google.com/speech-api/v2/recognize?client=chromium&lang=%s&key=%s' % (self.language, self.key)

  def recognize(self, audio_segment):
    assert isinstance(audio_segment, AudioSegment)

#    import pdb; pdb.set_trace()
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

    res = res[0]
    alternative = res['alternative']
    best_res = alternative[0]
    print(best_res['transcript'])
    os.remove(tmp_file_name)

def main():
    parser = argparse.ArgumentParser(description = 'simple recognizer')
    parser.add_argument('-i', '--input', default = 'in.wav', help = 'input file name')

    args = parser.parse_args()

    r = Recognizer()
    audio_segment = AudioSegment.from_file(args.input, 'wav')
    r.recognize(audio_segment)

    return 0

    r = sr.Recognizer(language = 'en-US', key = 'AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw')

    with sr.WavFile(args.input) as source:
        audio = r.record(source,True)
    try:
        list = r.recognize(audio, True)
        print('Possible transcriptions:')
        for prediction in list:
            print(' ' + prediction['text'] + ' (' + str(prediction['confidence']*100) + '%)')
    except LookupError:
        print("Could not understand audio")

if __name__ == '__main__':
    main()
