import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8765"  # Ensure this matches your server address
    try:
        async with websockets.connect(uri, ping_interval=300, ping_timeout=600) as websocket:  # Match server settings
            prompt = "Tell me your name"
            print("Sending prompt to server...")
            await websocket.send(prompt)
            response = await websocket.recv()
            print(f"Assistant: {response}")
    except asyncio.TimeoutError:
        print("Connection timed out. The server took too long to respond.")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"Failed to connect: {e.status_code} {e.reason}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed with error: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
