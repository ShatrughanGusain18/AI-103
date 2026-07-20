import os
from dotenv import load_dotenv

# Add references
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    MCPTool,
)
from openai.types.responses.response_input_param import (
    McpApprovalResponse,
    ResponseInputParam,
)

# Load environment variables
load_dotenv()

project_endpoint = os.getenv("PROJECT_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

# Connect to the Agents client
with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
    ) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # Initialize MCP Tool
    mcp_tool = MCPTool(
        server_label="api-specs",
        server_url="https://learn.microsoft.com/api/mcp",
        require_approval="always",
    )

    # Create a new agent with the MCP tool
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=model_deployment,
            instructions=(
                "You are a helpful agent that can use MCP tools to assist "
                "users. Use the available MCP tools to answer questions "
                "and perform tasks."
            ),
            tools=[mcp_tool],
        ),
    )

    print(
        f"Agent created "
        f"(id: {agent.id}, "
        f"name: {agent.name}, "
        f"version: {agent.version})"
    )

    # Create a conversation
    conversation = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation.id})")

    # Send initial request
    response = openai_client.responses.create(
        conversation=conversation.id,
        input="Give me the Azure CLI commands to create an Azure Foundry project.",
        extra_body={
            "agent_reference": {
                "name": agent.name,
                "type": "agent_reference",
            }
        },
    )

    # Process MCP approval requests
    while True:

        input_list: ResponseInputParam = []

        for item in response.output:

            if (
                item.type == "mcp_approval_request"
                and item.server_label == "api-specs"
                and item.id
            ):
                input_list.append(
                    McpApprovalResponse(
                        type="mcp_approval_response",
                        approve=True,
                        approval_request_id=item.id,
                    )
                )

        # No more approvals required
        if not input_list:
            break

        # Send approvals back to the model
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

    # Print final response
    print(f"\nAgent response:\n{response.output_text}")

    # Clean up
    project_client.agents.delete_version(
        agent_name=agent.name,
        agent_version=agent.version,
    )

    print("Agent deleted")
 