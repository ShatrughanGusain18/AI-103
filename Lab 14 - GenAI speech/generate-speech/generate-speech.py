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

        # Output speech file path
        speech_file_path = (
            Path(__file__).parent / "speech.mp3"
        )

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

        print("Generating speech...\n")

        # Generate speech and save to file
        with client.audio.speech.with_streaming_response.create(
            model=model_deployment,
            voice="alloy",
            input="My voice is my passport!",
            instructions="Speak in a serious tone.",
        ) as response:

            response.stream_to_file(speech_file_path)

        print(f"Speech saved to: {speech_file_path}")

        # Play generated audio
        print("\nPlaying speech...\n")
        playsound(str(speech_file_path))

    except Exception as ex:
        print(f"\nError: {ex}")


if __name__ == "__main__":
    main()
 