from google.cloud import texttospeech
from PyPDF2 import PdfFileReader as reader

def day_to_column(day):
    """Converts a given day into an Excel column letter

    The function takes a day of the month as an input and converts this day into a corresponding Excel column letter. The conversion is done by using the ASCII values of the alphabet. If the day number is greater than 25, it adds the corresponding letter to the start index and subtracts 1 from it to get an ASCII value that corresponds to a letter. If the day is less than 26, it simply adds the day to the start index to get a corresponding letter.
    Args:
        day
    Returns:
        string
    Example:
        day_to_column(28) -> 'AB'
    """
    """Converts the given day number to its corresponding Excel column character.

    This function takes a day number, and converts it to an Excel column character by calculating the equivalent ASCII value of the day. If the day number is larger than 25 (the number of alphabets), it will extract the corresponding character from the next round of alphabets. For example, a day number of 28 would translate to 'AB'; first round of 26 gives 'A' and the remaining 2 gives 'B'.
    Args:
        day: An integer representing the day number
    Returns:
        A string representing the corresponding Excel column character
    Example:
        day_to_column(28) -> 'AB'
    """
    """Converts a given day into an Excel column letter.

    The function takes a day of the month as an input and converts this day into a corresponding Excel column letter. The conversion is done by using the ASCII values of the alphabet. If the day number is greater than 25, it adds the corresponding letter to the start index and subtracts 1 from it to get an ASCII value that corresponds to a letter. If the day is less than 26, it simply adds the day to the start index to get a corresponding letter.
    Args:
        day
    Returns:
        string
    Example:
        day_to_column(28) -> 'AB'
    """
    start_index = 0
    letter = ''
    while day > 25 + start_index:
        letter += chr(65 + int((day - start_index) / 26) - 1)
        day = day - (int((day - start_index) / 26)) * 26
    letter += chr(65 - start_index + int(day))
    return letter

def tts_text(text, voice):
    """Converts the given text to speech.

    The function takes text and voice type as input and uses Google's text to speech client to convert the provided text into speech. The result is returned as an audio response.
    Args:
        text: The string of text to be converted into speech
        voice: The voice type for the speech
    Returns:
        audio response which contains the converted speech
    Raises:
        google.api_core.exceptions.GoogleAPIError if the request fails for any reason
    Example:
        tts_text('Hello world!', 'en-GB-standard-a')
    """
    """Converts input text to speech.

    This function takes in text and a voice parameter, converts the text to speech using Google's TextToSpeech API and returns an audio response.
    Args:
        text: The text to be converted to speech
        voice: The specific voice to be used in the conversion
    Returns:
        Google Cloud Text-to-Speech API response, audio data
    Example:
        tts_text('Hello World', 'en-GB-Standard-B')
    """
    """Converts the given text to speech.

    The function takes text and voice type as input and uses Google's text to speech client to convert the provided text into speech. The result is returned as an audio response.
    Args:
        text: The string of text to be converted into speech
        voice: The voice type for the speech
    Returns:
        audio response which contains the converted speech
    Raises:
        google.api_core.exceptions.GoogleAPIError if the request fails for any reason
    Example:
        tts_text('Hello world!', 'en-GB-standard-a')
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
    """Creates an audio file from a given PDF file.

    This function reads a PDF file, extracts the text from given pages, converts the text into speech using Google Text-to-Speech (TTS), and saves the audio output as an mp3 file. The voice for the TTS can be customized.
    Args:
        pdf_file: Name of the PDF file.
        voice: Information for Google TTS to customize the voice.
        page_range: List of page numbers to convert into audio.
    Returns:
        None. The function writes output to a file.
    Raises:
        FileNotFoundError: If the PDF file does not exist.
        PdfFileReaderError: If there is any issue with reading the PDF file.
        TTSRequestError: If there is a problem with the TTS request.
    Example:
        create_audio('sample.pdf', 'en-US', [1,2,3])
    """
    """Converts a range of pages from a PDF to an audio file using text-to-speech.

    This function reads the provided PDF file and extracts the text from the specified range of pages. It then uses text-to-speech to convert this text into audio, which is saved as an MP3 file with the same name as the PDF file.
    Args:
        pdf_file: The path to the PDF file to convert.
        voice: The voice to use for the text-to-speech conversion.
        page_range: The range of pages to convert.
    Returns:
        None
    Raises:
        IOError: If the PDF file cannot be opened or the MP3 file cannot be written.
    Example:
        create_audio('sample.pdf', 'en-US', range(1, 5))
    """
    """Creates an audio file from a given PDF file.

    This function reads a PDF file, extracts the text from given pages, converts the text into speech using Google Text-to-Speech (TTS), and saves the audio output as an mp3 file. The voice for the TTS can be customized.
    Args:
        pdf_file: Name of the PDF file.
        voice: Information for Google TTS to customize the voice.
        page_range: List of page numbers to convert into audio.
    Returns:
        None. The function writes output to a file.
    Raises:
        FileNotFoundError: If the PDF file does not exist.
        PdfFileReaderError: If there is any issue with reading the PDF file.
        TTSRequestError: If there is a problem with the TTS request.
    Example:
        create_audio('sample.pdf', 'en-US', [1,2,3])
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

