import websockets
import asyncio
import json

async def main():
    uri = "wss://www.bitmex.com/realtime"
    async with websockets.connect(uri) as websocket:
            #message to sub to XBTUSD updates
        msg = {
            "op": "subscribe",
            "args": ["instrument:XBTUSD"]
        }
        await websocket.send(json.dumps(msg))

    #recieve message in loop and print
    while True:
        result = await websocket.recv()
        data = json.loads(result)
        print(data)

if __name__ == "__main__":
    #run main function in asyncio loop
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
