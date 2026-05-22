from dotenv import load_dotenv
import os
import json

from azure.ai.contentunderstanding import (
    ContentUnderstandingClient
)
from azure.core.credentials import AzureKeyCredential


def main():

    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Load schema file
        schema_file = "biz-card.json"

        if not os.path.exists(schema_file):
            raise FileNotFoundError(
                f"Schema file not found: {schema_file}"
            )

        # Read schema JSON
        with open(schema_file, "r") as file:
            schema_json = json.load(file)

        card_schema = json.dumps(schema_json)

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

        # Create analyzer
        create_analyzer(
            schema=card_schema,
            analyzer=analyzer,
            endpoint=ai_svc_endpoint,
            key=ai_svc_key
        )

        print("\nAnalyzer setup completed.\n")

    except Exception as ex:
        print(f"\nError: {ex}")


# ----------------------------------------
# Create Analyzer Function
# ----------------------------------------
def create_analyzer(
    schema,
    analyzer,
    endpoint,
    key
):

    print("=" * 60)
    print(f"Creating Analyzer: {analyzer}")
    print("=" * 60)

    # Create Content Understanding client
    client = ContentUnderstandingClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Convert schema string to dictionary
    analyzer_definition = json.loads(schema)

    print("\nSubmitting analyzer creation request...\n")

    # Create analyzer
    poller = client.begin_create_analyzer(
        analyzer_id=analyzer,
        resource=analyzer_definition,
        allow_replace=True
    )

    # Wait for completion
    result = poller.result()

    print("Analyzer created successfully.\n")

    # Print status
    status = (
        result["status"]
        if isinstance(result, dict)
        and "status" in result
        else "Succeeded"
    )

    print(f"Analyzer Name : {analyzer}")
    print(f"Status        : {status}")

    print("=" * 60)


if __name__ == "__main__":
    main()