from dotenv import load_dotenv
import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def main():
    try:
        # Clear console
        os.system('cls' if os.name == 'nt' else 'clear')

        # Load environment variables
        load_dotenv()

        foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT")
        agent_name = os.getenv("AGENT_NAME")

        # Validate environment variables
        if not foundry_endpoint:
            raise ValueError(
                "FOUNDRY_ENDPOINT is not set in the .env file"
            )

        if not agent_name:
            raise ValueError(
                "AGENT_NAME is not set in the .env file"
            )

        # Create Azure AI Project client
        project_client = AIProjectClient(
            endpoint=foundry_endpoint,
            credential=DefaultAzureCredential(),
        )

        # Get OpenAI client
        openai_client = project_client.get_openai_client()

        # Take user input
        prompt = input("User Prompt: ")

        # Send request to agent
        response = openai_client.responses.create(
            input=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            extra_body={
                "agent_reference": {
                    "name": agent_name,
                    "type": "agent_reference"
                }
            },
        )

        # Print response
        print("\n" + "=" * 50)
        print(f"{agent_name} Response:\n")
        print(response.output_text)

        # Print detailed response
        print("\n" + "=" * 50)
        print("Response Details:\n")
        print(response.model_dump_json(indent=2))

    except Exception as ex:
        print(f"\nError: {ex}")


if __name__ == "__main__":
    main()