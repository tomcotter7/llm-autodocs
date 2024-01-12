from google.cloud import texttospeech
from PyPDF2 import PdfFileReader as reader

def day_to_column(day):
    """Converts a day number into corresponding Excel column index.

    The function takes a day number as a parameter and converts it into the corresponding Excel column index (letters). It starts from 0 index and converts the day count into ASCII representation in A-Z format (columns in Excel sheet), repeating from AA, AB and so on as the count goes beyond 26.

    Args:
        day: Integer representing the day number.
    Returns:
        A string representing corresponding Excel column index.
    Example:
        day_to_column(30) --> 'AD'
    """
    start_index = 0
    letter = ''
    while day > 25 + start_index:
        letter += chr(65 + int((day - start_index) / 26) - 1)
        day = day - (int((day - start_index) / 26)) * 26
    letter += chr(65 - start_index + int(day))
    return letter

def tts_text(text, voice):
    """Converts text to speech.

    This function takes a string of text and a voice name as input, and uses Google Text-to-Speech service to convert the given text into speech. The speech is synthesized with the requested voice and the audio is encoded as MP3.

    Args:
        text - The text string that needs to be converted into speech
        voice - The name of the voice to be used for speech synthesis
    Returns:
        Google Text-to-Speech service response with the synthesized speech
    Example:
        tts_text('Hello, world!', 'en-GB-Wavenet-D')
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
    """Generates an audio file from a PDF.

    This function takes as input a PDF file, a voice setting, and a range of pages, and creates an audio file from these data. The PDF is read page by page within the specified range, and the text is extracted. The extracted text is split into chunks of 5000 characters, each of which is processed by the tts_text function to convert it into audio. All these audio clips are then concatenated to form the final audio file, which is saved in the same location as the input PDF.

    Args:
        pdf_file: The path to the PDF file to be converted to audio.
        voice: The voice setting to be used for the text-to-speech conversion.
        page_range: The range of pages in the PDF to be included in the audio.
    Returns:
        None: The function writes the result directly to a file and does not return anything.
    Raises:
        IOError: If the PDF file cannot be opened for reading.
    Example:
        create_audio('path/to/pdf', 'en-US', range(1, 5))
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

