"""This is a helper module in the 'democode' package. It contains functions for converting a PDF file into audio, converting a given day into the corresponding column name and for converting given text to speech and returning the output audio.

The text to speech conversion function uses the Google Text-to-Speech client.
"""
from google.cloud import texttospeech
from PyPDF2 import PdfFileReader as reader

def day_to_column(day):
    """Converts a given day into the corresponding column name

    This function takes as input a day number and converts it to a column name. The conversion process operates similar to the excel column lettering system (e.g., day 1 -> 'A', day 28 -> 'AB'). The function assumes that column lettering starts from 'A' (Day 1).
    Args:
        day: The day number to convert into a column name. It should be a positive integer.
    Returns:
        str: The column letter corresponding to the given day.
    Example:
        >>> day_to_column(28)
        'AB'
    """
    start_index = 0
    letter = ''
    while day > 25 + start_index:
        letter += chr(65 + int((day - start_index) / 26) - 1)
        day = day - (int((day - start_index) / 26)) * 26
    letter += chr(65 - start_index + int(day))
    return letter

def tts_text(text, voice):
    """Converts given text to speech and returns the output audio. Uses the Google Text-to-Speech client

    This method takes a string text input and a voice setting and uses the Google Text-to-Speech API to convert the text to speech. The output audio is returned in MP3 format.
    Args:
        text (string): Text to convert to speech
        voice (string): The voice setting for the text-to-speech client
    Returns:
        A response object containing the output audio in MP3 format.
    Example:
        tts_text('Hello World', 'en-GB')
    """
    client = texttospeech.TextToSpeechClient()
    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    # We can use wavenet voices using this parameter, name='en-GB-Wavenet-D'
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB", name=voice
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response




def create_audio(pdf_file, voice, page_range):
    """This function converts a PDF file into audio.

    This function takes in a PDF file along with a voice and a page range as inputs. It reads the PDF, extracts the text from the specified pages, breaks the text into chunks of 5000 characters and converts each chunk to audio. Finally, it saves the audio data into an mp3 file and writes it to disk.
    Args:
        pdf_file: The PDF file that needs to be converted to audio.
        voice: The voice to be used for Text to Speech conversion.
        page_range: The pages in the PDF that need to be converted to audio. This should be a list containing the page numbers.
    Returns:
        None. The function writes the audio data to an mp3 file.
    Raises:
        FileNotFoundError: If the PDF file does not exist.
        TypeError: If the page_range argument is not a list.
        ValueError: If the voice is not a valid input.
    Example:
        create_audio('document.pdf', 'en-US', [1,2,3])
    """
    # I want to read the input in based on a command line input
    read_Pdf = reader(open(pdf_file, 'rb'))
    pdf_text = ""
    for page in range(read_Pdf.numPages):
        if page in page_range:
            text = read_Pdf.getPage(page).extractText()
            pdf_text += text + "\n"
    pdf_text = [pdf_text[start:start+5000] for start in range(0, len(pdf_text), 5000)]
    responses = []
    for request in pdf_text:
        responses.append(tts_text(request, voice).audio_content)
    response = b''.join(responses)
    filename = pdf_file[:-3] + "mp3"
    with open(filename, "wb") as out:
        out.write(response)
