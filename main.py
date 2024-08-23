from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse,PlainTextResponse,RedirectResponse,StreamingResponse
from pydantic import BaseModel
import signal
import os
import uvicorn
import time

#main entry point for our api
app=FastAPI()
audio_path=r"c:\Users\Hp\Documents\Sound recordings\Recording (5).m4a"

#websocket endpoint
@app.websocket("/ws")
async def websocket_streaming(websocket:WebSocket):
    await websocket.accept()
    try:
        with open(audio_path,mode='rb') as audio:
            while chunk:=audio.read(4096):
                await websocket.send_bytes(chunk)
            await websocket.close()
    except Exception as e:
        await websocket.close()
        print(f"Error: {e}")
#root function for streaming data in bytes   
@app.get("/")
def get_root():
    #measuring start time
    start=time.time()
    #generator function
    def get_file_iter():
        with open(audio_path,mode='rb') as sample_audio:
            # streaming the audio in chunk of 4KB each, size can be modified
            while chunk:=sample_audio.read(40960):
                yield chunk
    response=StreamingResponse(get_file_iter(),media_type='audio/x-m4a')
    
    end=time.time()
    latency=end-start
    print(f'latency:{latency:0.6f} seconds')
    return response
        
#function to pass in input text
@app.get("/userInput/{inputText}")
def UserText(inputText:str):
    return {"User input":inputText}

@app.get("/shutdown")
def shutdown():
    # Sending a signal to terminate the process
    os.kill(os.getpid(), signal.SIGTERM)
    return {"message": "Shutting down"}
#initialization
if __name__ == '__main__':
    uvicorn.run(app, port=8909, host='0.0.0.0')
    print('Success')
