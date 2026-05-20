from dotenv import load_dotenv
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalyticsClient


def analyze_reviews():
    try:
        # Clear console
        os.system('cls' if os.name == 'nt' else 'clear')

        # Load environment variables
        load_dotenv()

        foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT")

        if not foundry_endpoint:
            raise ValueError("FOUNDRY_ENDPOINT is not set in the .env file")

        # Create Azure credential
        credential = DefaultAzureCredential()

        # Create Text Analytics client
        ai_client = TextAnalyticsClient(
            endpoint=foundry_endpoint,
            credential=credential
        )

        # Reviews folder path
        reviews_folder = "reviews"

        if not os.path.exists(reviews_folder):
            raise FileNotFoundError(
                f"Folder '{reviews_folder}' does not exist"
            )

        # Process each review file
        for file_name in os.listdir(reviews_folder):

            file_path = os.path.join(reviews_folder, file_name)

            # Skip non-files
            if not os.path.isfile(file_path):
                continue

            print("\n" + "-" * 40)
            print(f"File: {file_name}")

            # Read file content
            with open(file_path, encoding="utf8") as file:
                text = file.read()

            print("\nReview Text:")
            print(text)

            # -------------------------------
            # Detect Language
            # -------------------------------
            detected_language = ai_client.detect_language(
                documents=[text]
            )[0]

            print("\nDetected Language:")
            print(detected_language.primary_language.name)

            # -------------------------------
            # Recognize Entities
            # -------------------------------
            entity_result = ai_client.recognize_entities(
                documents=[text]
            )[0]

            entities = entity_result.entities

            if entities:
                print("\nEntities:")
                for entity in entities:
                    print(f" - {entity.text} ({entity.category})")

            # -------------------------------
            # Recognize PII Entities
            # -------------------------------
            pii_result = ai_client.recognize_pii_entities(
                documents=[text]
            )[0]

            pii_entities = pii_result.entities

            if pii_entities:
                print("\nPII Entities:")
                for pii_entity in pii_entities:
                    print(
                        f" - {pii_entity.text} "
                        f"({pii_entity.category})"
                    )

                print("\nRedacted Text:")
                print(pii_result.redacted_text)

    except Exception as ex:
        print(f"\nError: {ex}")


if __name__ == "__main__":
    analyze_reviews()