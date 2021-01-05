from pyxll import xl_func, get_event_loop, RTD
from bitmex import BitMex


class BitMexRTD(RTD):

    # Use a single BitMex object for all RTD functions
    _bitmex = BitMex(loop=get_event_loop())

    def __init__(self, symbol, field):
        super().__init__(value="Waiting...")
        self.__symbol = symbol
        self.__field = field

    async def connect(self):
        # Subscribe to BitMix updates when Excel connects to the RTD object
        await self._bitmex.subscribe(self.__symbol, self.__field, self.__update)

    async def disconnect(self):
        # Unsubscribe to BitMix updates when Excel disconnects from the RTD object
        await self._bitmex.unsubscribe(self.__symbol, self.__field, self.__update)

    async def __update(self, symbol, field, value, timestamp):
        # Update the value in Excel
        self.value = value


@xl_func("string symbol, string field: rtd")
def bitmex_rtd(symbol, field):
    return BitMexRTD(symbol, field)