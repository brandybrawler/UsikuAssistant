import asyncio
import websockets

async def send_message(message):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(message)
        print(f"Sent: {message}")

        async for response in websocket:
            print(f"Received: {response}")

if __name__ == "__main__":
    message = "Your message here"
    asyncio.get_event_loop().run_until_complete(send_message(message))
