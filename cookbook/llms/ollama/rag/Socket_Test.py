import asyncio
import websockets

async def test_websocket():
    uri = "ws://0.0.0.0:8765"
    async with websockets.connect(uri) as websocket:
        prompt = "Tell me your name"
        await websocket.send(prompt)
        response = await websocket.recv()
        print(f"Assistant: {response}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
