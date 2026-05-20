from dotenv import load_dotenv
import os

from playsound3 import playsound
from azure.identity import DefaultAzureCredential
import azure.cognitiveservices.speech as speech_sdk


def main():
    try:
        # Clear console
        os.system('cls' if os.name == 'nt' else 'clear')

        # Load environment variables
        load_dotenv()

        foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT")

        # Validate endpoint
        if not foundry_endpoint:
            raise ValueError(
                "FOUNDRY_ENDPOINT is not set in the .env file"
            )

        # Create credential
        credential = DefaultAzureCredential()

        # Create speech configuration
        speech_config = speech_sdk.SpeechConfig(
            token_credential=credential,
            endpoint=foundry_endpoint
        )

        # Menu loop
        while True:

            print("\n" + "=" * 50)
            choice = input(
                "Choose an option:\n"
                "1: Record a greeting\n"
                "2: Transcribe messages\n"
                "3: Exit\n\n"
                "Enter choice: "
            )

            if choice == "1":
                record_greeting(speech_config)

            elif choice == "2":
                transcribe_messages(speech_config)

            elif choice == "3":
                print("\nExiting application...")
                break

            else:
                print("\nInvalid option. Please try again.")

    except Exception as ex:
        print(f"\nError: {ex}")


# ----------------------------------------
# Record Greeting Function
# ----------------------------------------
def record_greeting(speech_config):

    print("\nRecording greeting...\n")

    # Get greeting text from user
    greeting_message = input(
        "Enter your greeting message: "
    )

    # Output audio file
    output_file = "greeting.wav"

    # Configure audio output
    audio_config = speech_sdk.audio.AudioOutputConfig(
        filename=output_file
    )

    # Set voice
    speech_config.speech_synthesis_voice_name = (
        "en-US-Serena:DragonHDLatestNeural"
    )

    # Create synthesizer
    speech_synthesizer = speech_sdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    # Convert text to speech
    result = speech_synthesizer.speak_text_async(
        greeting_message
    ).get()

    # Check result
    if (
        result.reason
        == speech_sdk.ResultReason.SynthesizingAudioCompleted
    ):
        print(
            f"\nGreeting recorded successfully "
            f"and saved as '{output_file}'"
        )

    else:
        print(
            f"\nError recording greeting: "
            f"{result.reason}"
        )


# ----------------------------------------
# Transcribe Messages Function
# ----------------------------------------
def transcribe_messages(speech_config):

    print("\nTranscribing messages...\n")

    messages_folder = "messages"

    # Check folder exists
    if not os.path.exists(messages_folder):
        print(
            f"Folder '{messages_folder}' does not exist."
        )
        return

    # Process WAV files
    for file_name in os.listdir(messages_folder):

        if file_name.endswith(".wav"):

            print("\n" + "-" * 50)
            print(f"Transcribing: {file_name}")

            file_path = os.path.join(
                messages_folder,
                file_name
            )

            # Play audio file
            print("\nPlaying audio...")
            playsound(file_path)

            # Configure audio input
            audio_config = speech_sdk.audio.AudioConfig(
                filename=file_path
            )

            # Create recognizer
            speech_recognizer = speech_sdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )

            # Perform transcription
            result = (
                speech_recognizer
                .recognize_once_async()
                .get()
            )

            # Print result
            if (
                result.reason
                == speech_sdk.ResultReason.RecognizedSpeech
            ):
                print(f"\nTranscription:\n{result.text}")

            else:
                print(
                    f"\nError transcribing message: "
                    f"{result.reason}"
                )


if __name__ == "__main__":
    main()