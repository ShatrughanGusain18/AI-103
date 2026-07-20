import os

from dotenv import load_dotenv

# Import namespaces
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def main():
    try:
        # Clear the console
        os.system("cls" if os.name == "nt" else "clear")

        # Get configuration settings
        load_dotenv()

        foundry_endpoint = os.getenv("FOUNDRY_ENDPOINT")
        agent_name = os.getenv("AGENT_NAME")

        # Create the AI Project client
        project_client = AIProjectClient(
            endpoint=foundry_endpoint,
            credential=DefaultAzureCredential(),
        )

        # Get the OpenAI client
        openai_client = project_client.get_openai_client()

        # Main conversation loop
        while True:
            # Get user input
            prompt = input("User prompt (or 'quit'): ")

            if prompt.lower() == "quit" or len(prompt) == 0:
                break

            # Use the agent to generate a response
            response = openai_client.responses.create(
                input=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                extra_body={
                    "agent_reference": {
                        "name": agent_name,
                        "type": "agent_reference",
                    }
                },
            )

            print(f"{agent_name}: {response.output_text}")

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()