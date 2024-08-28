import subprocess
import pyaudio
import threading
import queue
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse

CHUNK_SIZE = 1024
SAMPLE_RATE = 22050
SAMPLE_WIDTH = 2
CHANNELS = 1

app=FastAPI()
templates = Jinja2Templates(directory="templates")

def generate_audio_stream(text, model_path, config_path, audio_queue):
    command = [
        r"piper.exe_path",
        "-m", model_path,
        "-c", config_path,
        "--output-raw"
    ]
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    def stream_stderr():
        for line in process.stderr:
            print(line.decode().strip())

    stderr_thread = threading.Thread(target=stream_stderr)
    stderr_thread.start()

    process.stdin.write(text.encode())
    process.stdin.close()

    while True:
        chunk = process.stdout.read(CHUNK_SIZE)
        if not chunk:
            break
        audio_queue.put(chunk)

    audio_queue.put(None)  # Signal end of stream
    process.wait()
    stderr_thread.join()

def play_audio_stream(audio_queue):
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(SAMPLE_WIDTH),
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    output=True)

    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break
        stream.write(chunk)

    stream.stop_stream()
    stream.close()
    p.terminate()

def main():
    model_path = r"model_path.onnx"
    config_path = r"config_path.onnx.json"

    try:
        while True:
            text = input("Enter text to speak (or 'q' to quit): ")
            if text.lower() == 'q':
                break

            audio_queue = queue.Queue()
            
            generate_thread = threading.Thread(target=generate_audio_stream, 
                                               args=(text, model_path, config_path, audio_queue))
            play_thread = threading.Thread(target=play_audio_stream, args=(audio_queue,))

            generate_thread.start()
            play_thread.start()

            generate_thread.join()
            play_thread.join()

    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()
