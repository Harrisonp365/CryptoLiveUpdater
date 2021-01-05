from pyxll import xl_func, get_event_loop, RTD
from bitmex import BitMex

class BitMexRTD(RTD):
    #use single Bitmex obj for all func
    _bitmex = BitMex(loop=get_event_loop())

    def __init__(self, symbol, field):
        super().__init__(value="Waiting...")
        self.__symbol = symbol
        self.__field = field

    async def connect(self):
        await self.bitmex.subscribe(self.__symbol, self.__field, self.__update)

    async def disconnect(self):
        await self._bitmex.unsubscribe(self.__symbol, self.__field, self.__update)

        async def __update(self, symbol, field, value, timestamp):
            self.value = value

@xl_func("string symbol, string field: rtd")
def bitmex_rtd(symbol, field):
    return BitMexRTD(symbol, field)