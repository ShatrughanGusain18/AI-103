import base64
import os

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

endpoint = "https://project63578298-resource.services.ai.azure.com/openai/v1"
deployment_name = "gpt-image-2"
api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Create the OpenAI client
client = OpenAI(
    base_url=endpoint,
    api_key=api_key,
)

# Generate an image
img = client.images.generate(
    model=deployment_name,
    prompt="A cute baby polar bear",
    n=1,
    size="1024x1024",
)

# Decode the Base64 image and save it
image_bytes = base64.b64decode(img.data[0].b64_json)

with open("output.png", "wb") as f:
    f.write(image_bytes)

print("Image saved as output.png")