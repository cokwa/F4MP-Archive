import ctypes
from F4MP import Librg


class Server:
    def __init__(self, address: str, port: int):
        self.host = Librg.Address(address, port)
        self.address = address
        self.port = port
        self._ctx = ctypes.POINTER(Librg.simple_classes.Context)(Librg.simple_classes.Context())
        Librg.init(self._ctx)

        self.call_map = {}
        self.callback_handler = Librg.CallbackHandler(self)

    def listener(self, name=None):
        def decorator(func):
            self.call_map[name or func.__name__].add(func)
            return func

        return decorator

    def start(self):
        Librg.network_start(self._ctx, self.address.encode(), self.port)

    def tick(self):
        Librg.tick(self._ctx)

    def run(self):
        self.start()
        while True:
            self.tick()
