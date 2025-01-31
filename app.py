import asyncio
import websockets
import whisper
import sounddevice as sd
import numpy as np
import queue
import threading

# Initialize Faster Whisper model
model = whisper.load_model("tiny")

# Setup WebSocket queue for real-time processing
message_queue = queue.Queue()

# Define audio sampling rate and buffer size
SAMPLE_RATE = 16000
BUFFER_SIZE = 1024

def audio_callback(indata, frames, time, status):
    """Capture audio in chunks and put into the message queue."""
    if status:
        print(status, file=sys.stderr)
    message_queue.put(indata.copy())

def transcribe_audio():
    """Process the audio chunks in real-time and transcribe."""
    while True:
        # Get audio chunk from queue
        audio_chunk = message_queue.get()

        # Convert the chunk to a format suitable for transcription
        audio_array = np.mean(audio_chunk, axis=1).astype(np.float32)
        
        # Perform the transcription
        result = model.transcribe(audio_array)
        print(f"Transcription: {result['text']}")
        
        # Send transcription to WebSocket client
        if websocket_connection:
            asyncio.run(websocket_connection.send(result['text']))

# Set up WebSocket server to handle real-time transcription
async def websocket_handler(websocket, path):
    global websocket_connection
    websocket_connection = websocket

    while True:
        await websocket.recv()  # Keep the WebSocket open for messages

# Set up the audio stream to capture live audio
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=BUFFER_SIZE)
stream.start()

# Start WebSocket server
start_server = websockets.serve(websocket_handler, "0.0.0.0", 8765)

# Run the WebSocket server and transcription in parallel
async def main():
    await asyncio.gather(start_server, asyncio.to_thread(transcribe_audio))

asyncio.run(main())
