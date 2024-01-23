"""This module, 'democode.audio_main', contains a method 'main' for converting a provided PDF file into an audiobook.

This function reads a PDF file and generates an audiobook. It leverages text extraction and text-to-speech functionalities.

Usage:
	The 'main' function can be initiated by running 'democode.audio_main' from the command line.
"""
from PyPDF2 import PdfFileReader as reader
from .helper import create_audio
import argparse

def main():
    """A function to convert a given PDF file into an audiobook

    This function takes input arguments such as input file name, voice type, start and end page. It parses these arguments to perform the conversion operation from pdf file to audio file.
    Args:
        'ifile': The input PDF to convert into an audiobook
        'voice': The voice to use in the audio file
        start: The page at which to start converting to an audiobook
        end: The page at which to end the audio book
    Returns:
        None
    Raises:
        IOError: If the input file is not found or not a valid PDF
        ValueError: If the start or end page are not valid
    Example:
        main('--ifile my_file.pdf', '--voice en-GB-Standard-A', '-s 0', '-e -1')
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
