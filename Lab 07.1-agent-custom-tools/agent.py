import os
import json
from dotenv import load_dotenv

# Add references
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FunctionTool,
    PromptAgentDefinition,
)
from azure.identity import DefaultAzureCredential

from openai.types.responses.response_input_param import (
    FunctionCallOutput,
    ResponseInputParam,
)

from functions import (
    next_visible_event,
    calculate_observation_cost,
    generate_observation_report,
)


def main():
    # Clear the console
    os.system("cls" if os.name == "nt" else "clear")

    # Load environment variables
    load_dotenv()

    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    # Connect to the project client
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=project_endpoint,
            credential=credential,
        ) as project_client,
        project_client.get_openai_client() as openai_client,
    ):

        # -----------------------------
        # Define Function Tools
        # -----------------------------

        event_tool = FunctionTool(
            name="next_visible_event",
            description="Get the next visible astronomical event in a given location.",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": (
                            "Continent to search for the next visible event "
                            "(e.g. 'north_america', 'south_america', 'australia')."
                        ),
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
            strict=True,
        )

        cost_tool = FunctionTool(
            name="calculate_observation_cost",
            description="Calculate the observation cost based on telescope tier, hours, and priority.",
            parameters={
                "type": "object",
                "properties": {
                    "telescope_tier": {
                        "type": "string",
                        "description": (
                            "Telescope tier "
                            "(standard, advanced, premium)."
                        ),
                    },
                    "hours": {
                        "type": "number",
                        "description": "Observation duration in hours.",
                    },
                    "priority": {
                        "type": "string",
                        "description": (
                            "Priority level "
                            "(low, normal, high)."
                        ),
                    },
                },
                "required": [
                    "telescope_tier",
                    "hours",
                    "priority",
                ],
                "additionalProperties": False,
            },
            strict=True,
        )

        report_tool = FunctionTool(
            name="generate_observation_report",
            description="Generate an astronomical observation report.",
            parameters={
                "type": "object",
                "properties": {
                    "event_name": {
                        "type": "string",
                        "description": "Astronomical event name.",
                    },
                    "location": {
                        "type": "string",
                        "description": "Observer location.",
                    },
                    "telescope_tier": {
                        "type": "string",
                        "description": "Telescope tier.",
                    },
                    "hours": {
                        "type": "number",
                        "description": "Observation duration in hours.",
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority level.",
                    },
                    "observer_name": {
                        "type": "string",
                        "description": "Observer's name.",
                    },
                },
                "required": [
                    "event_name",
                    "location",
                    "telescope_tier",
                    "hours",
                    "priority",
                    "observer_name",
                ],
                "additionalProperties": False,
            },
            strict=True,
        )

        # -----------------------------
        # Create Agent
        # -----------------------------

        agent = project_client.agents.create_version(
            agent_name="astronomy-agent",
            definition=PromptAgentDefinition(
                model=model_deployment,
                instructions="""
You are an astronomy observations assistant that helps users find
information about astronomical events, calculate telescope rental
costs, and generate observation reports.

Always use the available tools whenever appropriate.
                """,
                tools=[
                    event_tool,
                    cost_tool,
                    report_tool,
                ],
            ),
        )

        # -----------------------------
        # Create Conversation
        # -----------------------------

        conversation = openai_client.conversations.create()

        # Function outputs returned to the model
        input_list: ResponseInputParam = []

        # -----------------------------
        # Chat Loop
        # -----------------------------

        while True:

            user_input = input(
                "Enter a prompt for the astronomy agent.\n"
                "Use 'quit' to exit.\nUSER: "
            ).strip()

            if user_input.lower() == "quit":
                print("Exiting chat.")
                break

            # Add user message
            openai_client.conversations.items.create(
                conversation_id=conversation.id,
                items=[
                    {
                        "type": "message",
                        "role": "user",
                        "content": user_input,
                    }
                ],
            )

            # Clear previous tool outputs
            input_list.clear()

            # Ask the agent
            response = openai_client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={
                    "agent_reference": {
                        "name": agent.name,
                        "type": "agent_reference",
                    }
                },
            )

            if response.status == "failed":
                print(f"Response failed: {response.error}")
                continue

            # -----------------------------
            # Execute Function Calls
            # -----------------------------

            for item in response.output:

                if item.type != "function_call":
                    continue

                if item.name == "next_visible_event":
                    result = next_visible_event(
                        **json.loads(item.arguments)
                    )

                elif item.name == "calculate_observation_cost":
                    result = calculate_observation_cost(
                        **json.loads(item.arguments)
                    )

                elif item.name == "generate_observation_report":
                    result = generate_observation_report(
                        **json.loads(item.arguments)
                    )

                else:
                    result = "Unknown function."

                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=result,
                    )
                )

            # -----------------------------
            # Send Function Outputs
            # -----------------------------

            if input_list:
                response = openai_client.responses.create(
                    input=input_list,
                    previous_response_id=response.id,
                    extra_body={
                        "agent_reference": {
                            "name": agent.name,
                            "type": "agent_reference",
                        }
                    },
                )

            print(f"\nAGENT: {response.output_text}\n")

        # -----------------------------
        # Cleanup
        # -----------------------------

        project_client.agents.delete_version(
            agent_name=agent.name,
            agent_version=agent.version,
        )

        print("Deleted agent.")


if __name__ == "__main__":
    main()