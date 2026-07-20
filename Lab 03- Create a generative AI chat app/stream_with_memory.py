import os
from dotenv import load_dotenv

# Import namespaces
from openai import OpenAI
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider,
)


def main():
    # Clear the console
    os.system("cls" if os.name == "nt" else "clear")

    try:
        # Get configuration settings
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Initialize the OpenAI client
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://ai.azure.com/.default",
        )

        openai_client = OpenAI(
            base_url=azure_openai_endpoint,
            api_key=token_provider,
        )

        # Conversation history
        messages = []

        # Track response ID
        last_response_id = None

        # Loop until the user wants to quit
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')

            if input_text.lower() == "quit":
                break

            if not input_text.strip():
                print("Please enter a prompt.")
                continue

            # Add user message
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": input_text,
                        }
                    ],
                }
            )

            # Stream response
            stream = openai_client.responses.create(
                model=model_deployment,
                instructions="You are a helpful AI assistant that answers questions and provides information.",
                input=messages,
                previous_response_id=last_response_id,
                stream=True,
            )

            response_text = ""

            for event in stream:
                if event.type == "response.output_text.delta":
                    print(event.delta, end="", flush=True)
                    response_text += event.delta

                elif event.type == "response.completed":
                    last_response_id = event.response.id

            print()

            # Store assistant response
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": response_text,
                        }
                    ],
                }
            )

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()