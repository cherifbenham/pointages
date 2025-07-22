import os
import json
import requests
from openai import AzureOpenAI
from openai.types.beta import FunctionTool
from openai.types.beta.assistant import ToolDefinition
from openai.types.beta.threads import MessageContentText
from openai.types.beta.threads.runs import SubmitToolOutputsRequest
from openai.types.shared_params import FunctionDefinition

# === Azure OpenAI client setup ===
client = AzureOpenAI(
    api_key="YOUR_API_KEY",
    api_version="2024-03-01-preview",
    azure_endpoint="https://YOUR_RESOURCE_NAME.openai.azure.com/",
)

deployment_id = "YOUR_DEPLOYMENT_NAME"

# === Tool definition for submit_pointage ===
submit_pointage_tool = FunctionTool(
    function=FunctionDefinition(
        name="submit_pointage",
        description="Submit a time booking record.",
        parameters={
            "type": "object",
            "properties": {
                "start": {"type": "string", "description": "Start date/time in ISO format"},
                "name": {"type": "string", "description": "Full name of the person"},
                "type_sollicitation": {"type": "string", "description": "Booking type: activité, absence..."},
                "practice": {"type": "string"},
                "director": {"type": "string"},
                "client": {"type": "string"},
                "department": {"type": "string"},
                "kam": {"type": "string"},
                "business_manager": {"type": "string"},
                "description": {"type": "string"}
            },
            "required": ["name", "type_sollicitation"]
        }
    )
)

# === Create the assistant with the tool ===
assistant = client.beta.assistants.create(
    name="Pointage Assistant",
    instructions=(
        "You help users submit time bookings. Ask for missing details step-by-step. "
        "When you have all required information, use the `submit_pointage` tool."
    ),
    tools=[submit_pointage_tool],
    model=deployment_id,
)

# === Create thread ===
thread = client.beta.threads.create()

# === Initial user message ===
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="J’ai bossé sur GSK ce matin avec Marc."
)

# === Run the assistant ===
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# === Poll for completion & handle tool call ===
while True:
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for msg in messages.data:
            if msg.role == "assistant":
                for content in msg.content:
                    if isinstance(content, MessageContentText):
                        print("🤖", content.text.value)
        break

    elif run.status == "requires_action":
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print("🛠️ Tool call:", tool_name)
            print("📦 Arguments:", args)

            # Call your backend API
            response = requests.post("https://your.api/pointages", json=args)
            response.raise_for_status()

            # Reply to assistant with the result
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": "✅ Pointage submitted successfully!"
            })

        # Submit tool results back to assistant
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    else:
        import time
        time.sleep(1)