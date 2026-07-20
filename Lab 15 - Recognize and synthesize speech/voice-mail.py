import os

from dotenv import load_dotenv
from playsound3 import playsound

# Import namespaces
from azure.identity import DefaultAzureCredential
import azure.cognitiveservices.speech as speech_sdk


def main():
    try:
        # Clear the console
        os.system("cls" if os.name == "nt" else "clear")

        # Get configuration settings
        load_dotenv()

        foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT")
        foundry_key = os.getenv("FOUNDRY_KEY")

        # Create SpeechConfig using Entra ID authentication
        credential = DefaultAzureCredential()

        speech_config = speech_sdk.SpeechConfig(
            token_credential=credential,
            endpoint=foundry_endpoint,
        )

        # Loop until user quits
        input_text = ""

        while input_text != "3":
            input_text = input(
                "Choose an option:\n"
                "1: Record a greeting\n"
                "2: Transcribe messages\n"
                "3: Exit\n"
            )

            if input_text == "1":
                record_greeting(speech_config)

            elif input_text == "2":
                transcribe_messages(speech_config)

            elif input_text == "3":
                print("Exiting...")
                return

            else:
                print("Invalid option, please try again.")

    except Exception as ex:
        print(ex)


def record_greeting(speech_config):
    """Record a greeting using Speech Synthesis."""

    print("Recording greeting...")

    # Get greeting message from the user
    greeting_message = input("Enter your greeting message: ")

    # Synthesize the greeting message to an audio file
    output_file = "greeting.wav"

    audio_config = speech_sdk.audio.AudioOutputConfig(
        filename=output_file
    )

    speech_config.speech_synthesis_voice_name = (
        "en-US-Jimmie:DragonHDFlashLatestNeural"
    )

    speech_synthesizer = speech_sdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = speech_synthesizer.speak_text_async(
        greeting_message
    ).get()

    if result.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Greeting recorded and saved to {output_file}")

        # Release synthesizer resources
        speech_synthesizer = None

    else:
        print(f"Error recording greeting: {result.reason}")


def transcribe_messages(speech_config):
    """Transcribe all WAV files in the messages folder."""

    print("Transcribing messages...")

    messages_folder = "messages"

    for file_name in os.listdir(messages_folder):
        if file_name.endswith(".wav"):

            print(f"\nTranscribing {file_name}...")

            file_path = os.path.join(messages_folder, file_name)

            # Play the audio file
            playsound(str(file_path))

            # Configure speech recognizer
            audio_config = speech_sdk.audio.AudioConfig(
                filename=file_path
            )

            speech_recognizer = speech_sdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
            )

            # Transcribe the audio
            result = speech_recognizer.recognize_once_async().get()

            if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
                print(f"Transcription: {result.text}")

            else:
                print(f"Error transcribing message: {result.reason}")


if __name__ == "__main__":
    main()
 