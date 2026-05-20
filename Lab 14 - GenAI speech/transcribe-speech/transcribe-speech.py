import os
from pathlib import Path

from playsound3 import playsound
from dotenv import load_dotenv

from openai import AzureOpenAI
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider
)


def main():
    try:
        # Clear console
        os.system('cls' if os.name == 'nt' else 'clear')

        # Load environment variables
        load_dotenv()

        endpoint = os.getenv("MODEL_ENDPOINT")
        model_deployment = os.getenv("MODEL_NAME")

        # Validate environment variables
        if not endpoint:
            raise ValueError(
                "MODEL_ENDPOINT is not set in the .env file"
            )

        if not model_deployment:
            raise ValueError(
                "MODEL_NAME is not set in the .env file"
            )

        # Audio file path
        file_path = Path(__file__).parent / "speech.wav"

        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {file_path}"
            )

        # Play the speech file
        print("Playing audio file...\n")
        playsound(str(file_path))

        # Create Azure credential token provider
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://ai.azure.com/.default"
        )

        # Create Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version="2025-03-01-preview"
        )

        # Transcribe audio file
        print("\nTranscribing audio...\n")

        with open(file_path, "rb") as audio_file:

            transcription = client.audio.transcriptions.create(
                model=model_deployment,
                file=audio_file,
                response_format="text"
            )

        # Print transcription
        print("=" * 50)
        print("Transcription:\n")
        print(transcription)

    except Exception as ex:
        print(f"\nError: {ex}")


if __name__ == "__main__":
    main()