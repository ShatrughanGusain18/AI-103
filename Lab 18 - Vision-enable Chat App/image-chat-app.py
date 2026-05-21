import os
import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider
)


def main():

    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Load environment variables
        load_dotenv()

        openai_endpoint = os.getenv("ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Validate environment variables
        if not openai_endpoint:
            raise ValueError(
                "ENDPOINT is not set in the .env file"
            )

        if not model_deployment:
            raise ValueError(
                "MODEL_DEPLOYMENT is not set in the .env file"
            )

        # Create Azure credential
        credential = DefaultAzureCredential()

        # Create token provider
        token_provider = get_bearer_token_provider(
            credential,
            "https://ai.azure.com/.default"
        )

        # Create OpenAI client
        client = OpenAI(
            base_url=openai_endpoint,
            api_key=token_provider()
        )

        # System message
        system_message = (
            "You are an AI assistant in a grocery store "
            "that sells fruit. You provide detailed "
            "answers to questions about produce."
        )

        # Image file configuration
        image_path = Path("mystery-fruit.jpeg")
        image_format = "jpeg"

        # Validate image file
        if not image_path.exists():
            raise FileNotFoundError(
                f"Image file not found: {image_path}"
            )

        # Convert image to Base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        # Create data URL
        data_url = (
            f"data:image/{image_format};base64,"
            f"{image_data}"
        )

        print("=" * 60)
        print("Fruit Vision Assistant")
        print("Type 'quit' to exit")
        print("=" * 60)

        # Main loop
        while True:

            # Get user input
            prompt = input(
                "\nAsk a question about the image:\n"
            ).strip()

            # Exit condition
            if prompt.lower() == "quit":
                print("\nExiting application...")
                break

            # Empty input validation
            if len(prompt) == 0:
                print("\nPlease enter a question.")
                continue

            print("\nGetting response...\n")

            # Send image + prompt to model
            response = client.responses.create(
                model=model_deployment,
                input=[
                    {
                        "role": "developer",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": prompt
                            },
                            {
                                "type": "input_image",
                                "image_url": data_url
                            }
                        ]
                    }
                ]
            )

            # Print response
            print("-" * 60)
            print(response.output_text)
            print("-" * 60)

    except Exception as ex:
        print(f"\nError: {ex}")


if __name__ == "__main__":
    main()