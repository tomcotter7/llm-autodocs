from PyPDF2 import PdfFileReader as reader
from .helper import create_audio
import argparse

def main():
    parser = argparse.ArgumentParser("A program to convert pdf files into audiobooks")
    parser.add_argument("ifile", help="The input pdf to convert to an audiobook")
    parser.add_argument('--voice', '-v', help="The voice to use in this audio file. \
        Voices list here: https://cloud.google.com/text-to-speech/docs/voices", default='en-GB-Standard-A')
    parser.add_argument("--start", '-s', help="The page at which to start converting to an audio book. Inclusive.",
                        default=0)
    parser.add_argument("--end", '-e', help="The page at which to end the audio book. Exclusive.", default=-1)
    args = vars(parser.parse_args())

    if args['end'] == -1:
        read_Pdf = reader(open(args['ifile'], 'rb'))
        args['end'] = read_Pdf.numPages
    create_audio(args['ifile'], args['voice'], range(args['start'], args['end']))


if __name__ == "__main__":
    main()
