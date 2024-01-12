from PyPDF2 import PdfFileReader as reader
from .helper import create_audio
import argparse

def main():
    """A command line interface to convert pdf files into audiobooks

    This function enables the user to convert pdf files into audiobooks by providing an easy-to-use command line interface. The user can specify the page range for the conversion and select the voice for the audiobook from a list provided by Google Cloud Text-to-Speech API.

    Args:
        ifile - The input pdf to convert to an audiobook
        --voice/-v - The voice to use in this audio file.
        --start/-s - The page at which to start converting to an audio book. Inclusive.
        --end/-e - The page at which to end the audio book. Exclusive.
    Returns:
        None
    Raises:
        FileNotFoundError - If the input file does not exist
    Example:
        python3 main.py 'input.pdf' --voice 'en-US-Standard-B' --start 1 --end 5
    """
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
