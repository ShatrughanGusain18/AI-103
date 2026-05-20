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

        # Create AI Project client
        project_client = AIProjectClient(
            endpoint=foundry_endpoint,
            credential=DefaultAzureCredential(),
        )

        # Get OpenAI client
        openai_client = project_client.get_openai_client()

        print("=" * 60)
        print(f"{agent_name} Chat Application Started")
        print("Type 'quit' to exit")
        print("=" * 60)

        # Main conversation loop
        while True:

            # Get user input
            prompt = input("\nUser Prompt: ").strip()

            # Exit conditions
            if prompt.lower() == "quit" or len(prompt) == 0:
                print("\nExiting application...")
                break

            # Generate response using agent
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
            print("\n" + "-" * 60)
            print(f"{agent_name}:\n")
            print(response.output_text)
            print("-" * 60)

    except Exception as ex:
        print(f"\nError: {ex}")


if __name__ == "__main__":
    main()