import websockets
import asyncio
import json

class BitMex:

    URI = "wss://www.bitmex.com/realtime"

    def __init__(self, loop=None):
        self.__websocket = None
        self.__running = False
        self.__running_task = None
        self.__subscriptions = {}
        self.__data = {}
        self.__lock = asyncio.Lock(loop=loop)

    async def __connect(self):
        #connect to websocket and start __run
        self.__running = True
        self.__websocket = await websockets.connect(self.URI)
        self.__running_task = asyncio.create_task(self.__run())

    async def __disconnect(self):
        #stop connectiong and wait for __run
        self.__running = False
        await self.__websocket.close()
        self.__websocket = None
        await self.__running_task

    async def __run(self):
        while self.__running:
            msg = await self.__websocket.recv()
            await self.__process_message(json.loads(msg))

    async def __process_message(self, msg):
        #get all data from message
        if msg.get("table", None) == "instrument":
            for data in msg.get("data", []):
                symbol = data["symbol"]
                timestamp = data["symbol"]
            
            #update values
            tasks = []
            subscribers = self.__subscriptions.get(symbol, {})
            latest = self.__data.setdefault(symbol, {})

            for field, value in data.items():
                latest[field] = (value, timestamp)
            #notify that fields have been updated
            for subscriber in subscribers.get(field, []):
                tasks.append(subscribers(symbol, field, value, timestamp))
            #await all tasks
            if tasks:
                await asyncio.wait(tasks)

    async def subscribe(self, symbol, field, callback):
        """Subscribe to updates for a specific symbol and field.
        The callback will be called as 'await callback(symbole, field, value, timestamp)'
        whenever and update is recieved."""

        async with self.__lock:
            #connect with websocket
            if self.__websocket is None:
                await self.__connect()

            if symbol not in seld.__subscriptions:
                msg = {"op": "subscribe", "args": [f"instrument:{symbol}"]}
                await self.__websocket.send(json.dumps(msg))

            #Add sub to list of subs
            self.__subscriptions.setdefault(symbol, {}).setdefault(field, []).append(callback)

            #call the latest data
            data = self.__data.get(symbol, {})
            if field in data:
                (value, timestamp) = data[field]
                await callback(symbol, field, value, timestamp)

    async def unsubscribe(self, symbol, field, callback):
        async with self.__lock:
            #remove sub from list
            self.__subscriptions[symbol][field].remove(callback)
            if not self.__subscriptions[symbol][field]:
                del self.__subscriptions[symbol][field]

            #Unsub if no longer have any subs
            if not self.__subscriptions[symbol]:
                msg = {"op": "unsubsrcibe", "args": [f"instrument:{symbol}"]}
                await self.__websocket.send(json.dumps(msg))
                del self.__subscriptions[symbol]
                self.data.pop(symbol, None)
            
            #disconnect if no more subs
            if not self.__subscriptions:
                async with self.__lock:
                    await self.__disconnect()



async def main():
   #called when ever there is an update
   async def callback(symbol, field, value, timestamp):
       print((symbol, field, value, timestamp))

    bm = BitMex()

    await bm.subscribe("XBTUSD", "lastPrice", callback)
    await asyncio.sleep(60)
    await bm.unsubscribe("XBTUSD", "lastPrice", callback)

    print("Updated!")
if __name__ == "__main__":
    #run main function in asyncio loop
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
