import asyncio
import websockets
from rag_assistant_ui import RAGAssistantApp

async def handle_message(websocket, path, app: RAGAssistantApp):
    async for message in websocket:
        prompt = message
        response = ""
        try:
            if app.rag_assistant is None:
                await websocket.send("Assistant not initialized.")
                continue
            # Collect the entire response
            for delta in app.rag_assistant.run(prompt):
                response += delta  # type: ignore
            await websocket.send(response)  # Send the complete response
        except Exception as e:
            await websocket.send(f"Error: {str(e)}")

async def start_websocket_server(app: RAGAssistantApp):
    try:
        async with websockets.serve(lambda ws, path: handle_message(ws, path, app), "localhost", 8765, ping_interval=100, ping_timeout=200):
            await asyncio.Future()  # run forever
    except Exception as e:
        print(f"Failed to start WebSocket server: {e}")

def start_websocket_thread(app: RAGAssistantApp):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server(app))
