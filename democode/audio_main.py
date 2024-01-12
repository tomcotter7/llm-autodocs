from PyPDF2 import PdfFileReader as reader
from .helper import create_audio
import argparse

def main():
 """A main function to convert pdf files into audiobooks.

 This function parses command-line arguments, sets default values if necessary, and calls the function 'create_audio' to convert a specified range of pages from a PDF file into an audio file using a specified voice.

 Args:
  None, it does not take any explicit parameters. All necessary data is provided through command-line arguments.
 Returns:
  None, it doesn't return anything.
 Raises:
  ResourceError: if the specified PDF file cannot be opened or read.
  ValueError: if the specified range of pages is invalid.
  TypeError: if any input argument is of an inappropriate type.
 Example:
  python3 main.py input.pdf --voice 'en-US-Wavenet-F' --start 5 --end 10
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
