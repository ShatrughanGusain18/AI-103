import os
import json
import base64

from dotenv import load_dotenv
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider
)
from openai import OpenAI


def main():

    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Load environment variables
        load_dotenv()

        endpoint = os.getenv("ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Validate environment variables
        if not endpoint:
            raise ValueError(
                "ENDPOINT is not set in the .env file"
            )

        if not model_deployment:
            raise ValueError(
                "MODEL_DEPLOYMENT is not set in the .env file"
            )

        # Create Azure token provider
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_managed_identity_credential=True
            ),
            "https://cognitiveservices.azure.com/.default"
        )

        # Create OpenAI client
        client = OpenAI(
            base_url=endpoint,
            api_key=token_provider(),
        )

        print("=" * 60)
        print("AI Image Generator")
        print("Type 'quit' to exit")
        print("=" * 60)

        image_number = 0

        # Main loop
        while True:

            # Get user prompt
            input_text = input(
                "\nEnter image prompt: "
            ).strip()

            # Exit condition
            if input_text.lower() == "quit":
                print("\nExiting application...")
                break

            # Empty input validation
            if len(input_text) == 0:
                print("\nPlease enter a prompt.")
                continue

            print("\nGenerating image...\n")

            # Generate image
            img = client.images.generate(
                model=model_deployment,
                prompt=input_text,
                n=1
            )

            # Convert response to JSON
            json_response = json.loads(
                img.model_dump_json()
            )

            # Extract Base64 image
            image_data = json_response["data"][0].get(
                "b64_json"
            )

            if not image_data:
                raise ValueError(
                    "No image data returned from model."
                )

            # Decode image
            image_data_in_bytes = base64.b64decode(
                image_data
            )

            # Increment image counter
            image_number += 1

            # File name
            file_name = f"image_{image_number}.png"

            # Save image
            save_image(
                image_data_in_bytes,
                file_name
            )

    except Exception as ex:
        print(f"\nError: {ex}")


# ----------------------------------------
# Save Image Function
# ----------------------------------------
def save_image(image_data, file_name):

    # Create images directory
    image_dir = os.path.join(
        os.getcwd(),
        "images"
    )

    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    # Create image path
    image_path = os.path.join(
        image_dir,
        file_name
    )

    # Save image file
    with open(image_path, "wb") as image_file:
        image_file.write(image_data)

    print(f"Image saved as:\n{image_path}")


if __name__ == "__main__":
    main()