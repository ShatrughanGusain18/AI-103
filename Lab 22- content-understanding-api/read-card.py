from dotenv import load_dotenv
import os
import sys
import json

from azure.ai.contentunderstanding import (
    ContentUnderstandingClient
)
from azure.core.credentials import AzureKeyCredential


def main():

    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Default business card image
        image_file = "biz-card-2.png"

        # Allow command-line image input
        if len(sys.argv) > 1:
            image_file = sys.argv[1]

        # Load environment variables
        load_dotenv()

        ai_svc_endpoint = os.getenv("ENDPOINT")
        ai_svc_key = os.getenv("KEY")
        analyzer = os.getenv("ANALYZER_NAME")

        # Validate environment variables
        if not ai_svc_endpoint:
            raise ValueError(
                "ENDPOINT is not set in the .env file"
            )

        if not ai_svc_key:
            raise ValueError(
                "KEY is not set in the .env file"
            )

        if not analyzer:
            raise ValueError(
                "ANALYZER_NAME is not set in the .env file"
            )

        # Validate image file
        if not os.path.exists(image_file):
            raise FileNotFoundError(
                f"Image file not found: {image_file}"
            )

        # Analyze business card
        analyze_card(
            image_file=image_file,
            analyzer=analyzer,
            endpoint=ai_svc_endpoint,
            key=ai_svc_key
        )

        print("\nAnalysis completed successfully.\n")

    except Exception as ex:
        print(f"\nError: {ex}")


# ----------------------------------------
# Analyze Business Card
# ----------------------------------------
def analyze_card(
    image_file,
    analyzer,
    endpoint,
    key
):

    print("=" * 60)
    print(f"Analyzing Business Card: {image_file}")
    print("=" * 60)

    # Create Content Understanding client
    client = ContentUnderstandingClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Read image data
    with open(image_file, "rb") as file:
        image_data = file.read()

    print("\nSubmitting analysis request...\n")

    # Submit image for analysis
    poller = client.begin_analyze_binary(
        analyzer_id=analyzer,
        binary_input=image_data
    )

    # Wait for result
    result = poller.result()

    print("Analysis succeeded.\n")

    # Save JSON output
    output_file = "results.json"

    with open(output_file, "w") as json_file:

        json.dump(
            dict(result),
            json_file,
            indent=4,
            default=str
        )

    print(f"Response saved to: {output_file}\n")

    # Extract fields from results
    for content in result.contents:

        if hasattr(content, "fields") and content.fields:

            print("=" * 60)
            print("Extracted Fields")
            print("=" * 60)

            for field_name, field_data in (
                content.fields.items()
            ):

                # Safely extract value
                value = (
                    field_data.value
                    if hasattr(field_data, "value")
                    else None
                )

                print(f"{field_name}: {value}")

            print("=" * 60)


if __name__ == "__main__":
    main()