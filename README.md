

FastAPI Audio Streaming Server
Overview
This project sets up a FastAPI server for streaming audio files and handling WebSocket connections. It includes endpoints for:

Streaming audio files via HTTP GET requests.
Streaming audio data through WebSocket connections.
Receiving user input as text.
Shutting down the server gracefully.
Features
WebSocket Endpoint: Streams audio data in real-time to clients over WebSocket.
HTTP GET Endpoint: Streams audio files in chunks over HTTP.
User Input Endpoint: Receives and returns user-provided text.
Shutdown Endpoint: Allows for graceful shutdown of the server.
Requirements
Python 3.7 or higher
FastAPI
Uvicorn
