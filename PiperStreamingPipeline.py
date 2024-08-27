from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import subprocess
import os
import uuid

app = FastAPI()

# Set up the Jinja2 templates directory
templates = Jinja2Templates(directory=".")

# Path to your model file and Piper executable
piper_executable = r"path_for_piper_executable"
model_path = r"model_path.onnx"
config_path = r"model_config_path.onnx.json"
output_file = "output_path"


@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "audio_url": None})

@app.post("/synthesize/")
async def synthesize(request: Request):
    form_data = await request.form()
    input_text = form_data.get('text')

    if not input_text:
        raise HTTPException(status_code=400, detail="Text input is required")
    print(input_text)

    try:
        
        # Define the command to run Piper
        command = [
            piper_executable,
            "-m", model_path,
            "-c", config_path,
            "-f", output_file
        ]

        # Run the command using subprocess
        subprocess.run(command, input=input_text,text=True, capture_output=True)
        print("done")
        print(output_file)
        # Check if the output file was created
        #if not os.path.exists(output_file):
        #    raise HTTPException(status_code=500, detail="Audio file was not generated")

        # Generate the audio URL and pass it to the HTML template
        audio_url = f"/stream_audio/{output_file}"
        return templates.TemplateResponse("index.html", {"request": request, "audio_url": audio_url})

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Subprocess error: {e.stderr}")

@app.get("/stream_audio/{file_name}")
async def stream_audio(file_name: str):
    file_path = os.path.join(os.getcwd(), file_name)
    if os.path.isfile(file_path):
        return StreamingResponse(iterfile(file_path), media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="File not found")

def iterfile(file_path: str):
    with open(file_path, "rb") as f:
        yield from f
