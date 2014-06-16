import argparse
from gtts import gTTS

def main():
    parser = argparse.ArgumentParser(description = 'input wav generator')
    parser.add_argument('text', help = 'text to convert into wav')
    parser.add_argument('-o', '--output', default = 'out.mp3', help = 'output file name')

    args = parser.parse_args()

    tts = gTTS(text=args.text, lang='en', debug = True)
    tts.save(args.output)
    silence = [0 for i in range(100 * 1024)]
    silence = bytes(byte for byte in silence)
    with open(args.output, 'ab') as f:
        f.write(silence)

if __name__ == '__main__':
    main()
