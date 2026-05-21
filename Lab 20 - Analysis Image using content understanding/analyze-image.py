import sys
import os

from dotenv import load_dotenv

from azure.ai.contentunderstanding import (
    ContentUnderstandingClient
)
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    AnalysisResult
)
from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential


def main():

    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Load environment variables
        load_dotenv()

        endpoint = os.getenv("ENDPOINT")
        analyzer_id = os.getenv("ANALYZER")

        api_version = "2025-11-01"

        # Validate environment variables
        if not endpoint:
            raise ValueError(
                "ENDPOINT is not set in the .env file"
            )

        if not analyzer_id:
            raise ValueError(
                "ANALYZER is not set in the .env file"
            )

        # Create credential
        credential = DefaultAzureCredential()

        # Create Content Understanding client
        client = ContentUnderstandingClient(
            endpoint=endpoint,
            credential=credential,
            api_version=api_version
        )

        print("=" * 60)
        print("Azure Content Understanding")
        print("=" * 60)

        # Main loop
        while True:

            file_no = input(
                "\nChoose a file (1, 2, or 3)"
                "\nAny other key to exit: "
            ).strip()

            # Exit condition
            if file_no not in ["1", "2", "3"]:
                print("\nExiting application...")
                break

            # Example file mapping
            file_map = {
                "1": r"C:\Users\Admin\Desktop\R.jpg",
                "2": r"C:\Users\Admin\Desktop\R.jpg",
                "3": r"C:\Users\Admin\Desktop\R.jpg"
            }

            file_path = file_map[file_no]

            # Validate file existence
            if not os.path.exists(file_path):
                print(
                    f"\nFile does not exist:\n{file_path}"
                )
                continue

            # Read file bytes
            with open(file_path, "rb") as file:
                file_bytes = file.read()

            print("\nAnalyzing file...")
            print(f"Analyzer : {analyzer_id}")
            print(f"File     : {file_path}\n")

            try:
                # Submit analysis request
                poller = client.begin_analyze(
                    analyzer_id=analyzer_id,
                    inputs=[
                        AnalysisInput(
                            data=file_bytes
                        )
                    ],
                )

                # Get result
                result: AnalysisResult = poller.result()

            except AzureError as err:
                print(f"\n[Azure Error]: {err.message}")
                continue

            except Exception as ex:
                print(f"\n[Unexpected Error]: {ex}")
                continue

            # Process analysis results
            print("=" * 60)

            fields = result.contents[0].fields

            for field_name in fields:

                field_value = fields[field_name]

                # Description field
                if field_name == "Description":

                    print(
                        f"\n{field_name}:\n"
                        f"{field_value.value_string}\n"
                    )

                # Tags field
                elif field_name == "Tags":

                    print(f"\n{field_name}:")

                    for tag in field_value.value_array:
                        print(f"  - {tag.value_string}")

            print("=" * 60)

    except Exception as ex:
        print(f"\nError: {ex}")
        sys.exit(1)


if __name__ == "__main__":
    main()