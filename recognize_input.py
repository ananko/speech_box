import argparse
import speech_recognition as sr

def main():
    parser = argparse.ArgumentParser(description = 'simple recognizer')
    parser.add_argument('-i', '--input', default = 'in.wav', help = 'input file name')

    args = parser.parse_args()

    r = sr.Recognizer()
    with sr.WavFile(args.input) as source:
        audio = r.record(source,True)
    try:
        list = r.recognize(audio,True)
        print('Possible transcriptions:')
        for prediction in list:
            print(' ' + prediction['text'] + ' (' + str(prediction['confidence']*100) + '%)')
    except LookupError:
        print("Could not understand audio")

if __name__ == '__main__':
    main()
