import websockets
import asyncio


async def connect(uri):
    async with websockets.connect(uri) as websocket:
        while True:
            msg = await websocket.recv()
            print(msg)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(
        connect("ws://172.16.14.49:30971/api/v1/trend-logs")
    )
    asyncio.get_event_loop().run_forever()


"ws://172.16.14.49:30971/api/v1/trend-logs"
