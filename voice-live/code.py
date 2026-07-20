import os
import asyncio
import base64
import queue

from dotenv import load_dotenv
import pyaudio

# Import namespaces
from azure.identity.aio import AzureCliCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    AgentConfig,
    AudioEchoCancellation,
    AudioNoiseReduction,
    AzureSemanticVadMultilingual,
    InputAudioFormat,
    Modality,
    OutputAudioFormat,
    RequestSession,
    ServerEventType,
)


def main():
    """Main entry point."""

    try:
        # Clear the console
        os.system("cls" if os.name == "nt" else "clear")

        # Get required configuration from environment variables
        load_dotenv()

        endpoint = os.environ.get("AZURE_VOICELIVE_ENDPOINT")
        agent_name = os.environ.get("AZURE_VOICELIVE_AGENT_ID")
        project_name = os.environ.get("AZURE_VOICELIVE_PROJECT_NAME")

        agent_config = AgentConfig(
            {
                "agent_name": agent_name,
                "project_name": project_name,
            }
        )

        # Create credential for authentication
        credential = AzureCliCredential()

        # Create and start the voice assistant
        assistant = VoiceAssistant(
            endpoint=endpoint,
            credential=credential,
            agent_config=agent_config,
        )

        try:
            asyncio.run(assistant.start())
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")


class VoiceAssistant:
    """
    Main voice assistant that coordinates the conversation flow.

    This class demonstrates the essential pattern for Azure VoiceLive:
    1. Connect to the service
    2. Configure the session
    3. Start audio capture/playback
    4. Process events from the service
    """

    def __init__(self, endpoint, credential, agent_config):
        self.endpoint = endpoint
        self.credential = credential
        self.agent_config = agent_config

    async def start(self):
        """Start the voice assistant."""

        print("\n" + "=" * 60)
        print("🎙️  AZURE VOICELIVE VOICE AGENT")
        print("=" * 60)

        try:
            # STEP 1: Connect Azure VoiceLive to the agent
            async with connect(
                endpoint=self.endpoint,
                credential=self.credential,
                api_version="2026-01-01-preview",
                agent_config=self.agent_config,
            ) as connection:

                self.connection = connection

                # STEP 2: Initialize audio processor
                self.audio_processor = AudioProcessor(connection)

                # STEP 3: Configure the session
                await self.setup_session()

                # STEP 4: Start audio systems
                self.audio_processor.start_playback()

                print("\n✅ Ready! Start speaking...")
                print("Press Ctrl+C to exit\n")

                # STEP 5: Process events
                await self.process_events()

        finally:
            if hasattr(self, "audio_processor"):
                self.audio_processor.shutdown()

    async def setup_session(self):
        """Configure the session with audio settings."""

        session_config = RequestSession(
            # Enable both text and audio
            modalities=[Modality.TEXT, Modality.AUDIO],

            # Audio format
            input_audio_format=InputAudioFormat.PCM16,
            output_audio_format=OutputAudioFormat.PCM16,

            # Voice Activity Detection
            turn_detection=AzureSemanticVadMultilingual(),

            # Echo cancellation
            input_audio_echo_cancellation=AudioEchoCancellation(),

            # Noise reduction
            input_audio_noise_reduction=AudioNoiseReduction(
                type="azure_deep_noise_suppression"
            ),
        )

        await self.connection.session.update(session=session_config)
        print("⚙️ Session configured")

    async def process_events(self):
        """Process events from the VoiceLive service."""

        async for event in self.connection:
            await self.handle_event(event)

    async def handle_event(self, event):
        """Handle events from the VoiceLive service."""

        if event.type == ServerEventType.SESSION_UPDATED:
            print(f"📡 Connected to agent: {event.session.agent.name}")
            self.audio_processor.start_capture()

        elif (
            event.type
            == ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED
        ):
            print(f'👤 You: {event.get("transcript", "")}')

        elif event.type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
            print(f'🤖 Agent: {event.get("transcript", "")}')

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
            self.audio_processor.clear_playback_queue()
            print("🎤 Listening...")

        elif event.type == ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED:
            print("🤔 Thinking...")

        elif event.type == ServerEventType.RESPONSE_AUDIO_DELTA:
            self.audio_processor.queue_audio(event.delta)

        elif event.type == ServerEventType.RESPONSE_AUDIO_DONE:
            print("✓ Response complete\n")

        elif event.type == ServerEventType.ERROR:
            print(f"❌ Error: {event.error.message}")


class AudioProcessor:
    """
    Handles microphone input and speaker output.

    Responsibilities:
    - Capture microphone audio
    - Send audio to VoiceLive
    - Play audio returned by VoiceLive
    """

    def __init__(self, connection):
        self.connection = connection
        self.audio = pyaudio.PyAudio()

        # Audio settings
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 24000
        self.chunk_size = 1200

        self.input_stream = None
        self.output_stream = None
        self.playback_queue = queue.Queue()

    def start_capture(self):
        """Start microphone capture."""

        def capture_callback(in_data, frame_count, time_info, status):
            audio_base64 = base64.b64encode(in_data).decode("utf-8")

            asyncio.run_coroutine_threadsafe(
                self.connection.input_audio_buffer.append(audio=audio_base64),
                self.loop,
            )

            return (None, pyaudio.paContinue)

        self.loop = asyncio.get_event_loop()

        self.input_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=capture_callback,
        )

        print("🎤 Microphone started")

    def start_playback(self):
        """Start speaker playback."""

        remaining = bytes()

        def playback_callback(in_data, frame_count, time_info, status):
            nonlocal remaining

            bytes_needed = (
                frame_count
                * pyaudio.get_sample_size(pyaudio.paInt16)
            )

            output = remaining[:bytes_needed]
            remaining = remaining[bytes_needed:]

            while len(output) < bytes_needed:
                try:
                    audio_data = self.playback_queue.get_nowait()

                    if audio_data is None:
                        break

                    output += audio_data

                except queue.Empty:
                    output += bytes(bytes_needed - len(output))
                    break

            if len(output) > bytes_needed:
                remaining = output[bytes_needed:]
                output = output[:bytes_needed]

            return (output, pyaudio.paContinue)

        self.output_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=playback_callback,
        )

        print("🔊 Speakers ready")

    def queue_audio(self, audio_data):
        """Queue received audio."""
        self.playback_queue.put(audio_data)

    def clear_playback_queue(self):
        """Clear queued playback audio."""

        while not self.playback_queue.empty():
            try:
                self.playback_queue.get_nowait()
            except queue.Empty:
                break

    def shutdown(self):
        """Release audio resources."""

        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()

        if self.output_stream:
            self.playback_queue.put(None)
            self.output_stream.stop_stream()
            self.output_stream.close()

        self.audio.terminate()
        print("🔇 Audio stopped")


if __name__ == "__main__":
    main()