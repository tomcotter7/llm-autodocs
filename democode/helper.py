from google.cloud import texttospeech
from PyPDF2 import PdfFileReader as reader

def day_to_column(day):
    """
    Converts a day number to a column label similar to Excel column naming convention.
    
    Args:
        day (int): The day number to be converted into a column label.
    
    Returns:
        str: The corresponding column label for the given day number.
    """
    start_index = 0
    letter = ''
    while day > 25 + start_index:
        letter += chr(65 + int((day - start_index) / 26) - 1)
        day = day - (int((day - start_index) / 26)) * 26
    letter += chr(65 - start_index + int(day))
    return letter

def tts_text(text, voice):
    """
    Converts text to speech using Google's Text-to-Speech API.
    
    Args:
        text (str): The text to be converted to speech.
        voice (str): The name of the voice model to be used for the speech synthesis, e.g., 'en-GB-Wavenet-D'.
    
    Returns:
        texttospeech.types.SynthesizeSpeechResponse: An object containing the synthesized audio data.
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
    """
    Converts a range of pages from a PDF file into an audio file using text-to-speech.
    
    Args:
        pdf_file (str): The path to the PDF file to be converted.
        voice (str): The voice setting to be used for the text-to-speech conversion.
        page_range (list of int): A list of page numbers to be included in the conversion.
    
    Returns:
        None: The function writes the audio content to an MP3 file with the same name as the PDF file.
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

