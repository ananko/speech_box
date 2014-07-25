import argparse
from gtts import gTTS
from pydub import AudioSegment

def main():
    parser = argparse.ArgumentParser(description = 'input wav generator')
    parser.add_argument('text', help = 'text to convert into wav')
    parser.add_argument('-o', '--output', default = 'data', help = 'output file name')

    args = parser.parse_args()

    tts = gTTS(text=args.text, lang='en', debug = True)
    tts.save(args.output + '.mp3')

    data = AudioSegment.from_file(args.output + '.mp3', 'mp3')
    silence_duration_ms = 3000
    silence = AudioSegment.silent(silence_duration_ms)
    new_data = data + silence
    new_data.export(args.output + '.wav', 'wav')

if __name__ == '__main__':
    main()
