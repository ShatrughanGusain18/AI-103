import os

from dotenv import load_dotenv

# Import namespaces
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalyticsClient


def main():
    try:
        # Clear the console
        os.system("cls" if os.name == "nt" else "clear")

        # Get configuration settings
        load_dotenv()
        foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT")

        # Create client using endpoint
        credential = DefaultAzureCredential()

        ai_client = TextAnalyticsClient(
            endpoint=foundry_endpoint,
            credential=credential,
        )

        # Analyze each text file in the reviews folder
        reviews_folder = "reviews"

        for file_name in os.listdir(reviews_folder):

            # Read the file contents
            print("\n-------------")
            print(file_name)

            file_path = os.path.join(reviews_folder, file_name)

            with open(file_path, encoding="utf-8") as file:
                text = file.read()

            print(f"\n{text}")

            # Detect language
            detected_language = ai_client.detect_language(
                documents=[text]
            )[0]

            print(
                f"\nLanguage: "
                f"{detected_language.primary_language.name}"
            )

            # Recognize entities
            entities = ai_client.recognize_entities(
                documents=[text]
            )[0].entities

            if entities:
                print("\nEntities")

                for entity in entities:
                    print(
                        f"\t{entity.text} ({entity.category})"
                    )

            # Recognize PII
            pii_result = ai_client.recognize_pii_entities(
                documents=[text]
            )[0]

            pii_entities = pii_result.entities

            if pii_entities:
                print("\nPII Entities")

                for pii_entity in pii_entities:
                    print(
                        f"\t{pii_entity.text} "
                        f"({pii_entity.category})"
                    )

                print(
                    "\nRedacted Text:\n"
                    f"{pii_result.redacted_text}"
                )

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
 