import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider,
)

# Load configuration settings
load_dotenv()

endpoint = os.getenv("OPENAI_BASE_URL")
model_deployment = os.getenv("MODEL_DEPLOYMENT") // Sora-2

# Get the token provider for Azure OpenAI authentication
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

# Initialize the OpenAI client
client = OpenAI(
    base_url=endpoint,
    api_key=token_provider,
)


def main():
    """Main entry point."""

    # Clear the console
    os.system("cls" if os.name == "nt" else "clear")

    try:
        print("=== Video Generation Application ===\n")

        # ------------------------------------------------------------------
        # Step 1: Generate a video from a text prompt
        # ------------------------------------------------------------------
        print("Step 1: Generating video from text prompt...")

        video = client.videos.create(
            model=model_deployment,
            prompt=(
                "A peaceful mountain lake at sunrise with mist rising "
                "from the water and a car driving"
            ),
            size="1024x1024",
            seconds="12",
        )

        video = poll_video_status(video.id)

        if video.status == "completed":
            download_video(video.id, "original_video.mp4")
            original_video_id = video.id

            # --------------------------------------------------------------
            # Step 2: Remix the generated video
            # --------------------------------------------------------------
            print("\nStep 2: Remixing the video with a new color palette...")

            remixed = remix_video(
                original_video_id,
                "Shift the color palette to warm sunset tones with golden light",
            )

            if remixed.status == "completed":
                download_video(remixed.id, "remixed_video.mp4")

        # ------------------------------------------------------------------
        # Step 3: Generate a video from a reference image
        # ------------------------------------------------------------------
        print("\nStep 3: Generating a video from a reference image...")

        video = generate_video_from_image(
            image_path="reference.png",
            prompt=(
                "The scene comes to life with gentle movement "
                "and ambient lighting"
            ),
            size="1024x1024",
            seconds="12",
        )

        if video.status == "completed":
            download_video(video.id, "image_based_video.mp4")

        print("\n=== Video generation complete ===")

    except Exception as ex:
        print(ex)


def poll_video_status(video_id):
    """
    Poll the video status every 20 seconds until it completes or fails.
    """

    video = client.videos.retrieve(video_id)

    while video.status not in ["completed", "failed", "cancelled"]:
        print(f"Status: {video.status}. Waiting 20 seconds...")
        time.sleep(20)
        video = client.videos.retrieve(video_id)

    if video.status == "completed":
        print("Video successfully completed!")
    else:
        print(f"Video creation ended with status: {video.status}")

    return video


def remix_video(video_id, prompt):
    """
    Create a remix of an existing video.
    """

    print(f"Starting video remix for: {video_id}")

    video = client.videos.remix(
        video_id=video_id,
        prompt=prompt,
    )

    print(f"Remix started. New video ID: {video.id}")
    print(f"Initial status: {video.status}")

    return poll_video_status(video.id)


def download_video(video_id, output_filename="output.mp4"):
    """
    Download a completed video.
    """

    print(f"Downloading video {video_id}...")

    content = client.videos.download_content(
        video_id,
        variant="video",
    )

    content.write_to_file(output_filename)

    print(f"Saved video to {output_filename}")


def generate_video_from_image(
    image_path,
    prompt,
    size="1024x1024",
    seconds=12,
):
    """
    Generate a video using a reference image.
    """

    print(f"Starting video generation from image: {image_path}")

    with open(image_path, "rb") as image_file:
        video = client.videos.create(
            model=model_deployment,
            prompt=prompt,
            size=size,
            seconds=seconds,
            input_reference=image_file,
        )

    print(f"Video creation started. ID: {video.id}")
    print(f"Initial status: {video.status}")

    return poll_video_status(video.id)


if __name__ == "__main__":
    main()