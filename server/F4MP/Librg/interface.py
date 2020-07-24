"""Librg function bridge and entry point to the dll"""
import os
import ctypes
import logging
from .simple_classes import Address, Context
from typing import Dict, Callable

log = logging.getLogger(__name__)


class Interface:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    func_map: Dict[str, Callable] = {
        "tick": None
    }  # TODO: This should contain functions which return anything other than a bool

    def __init__(self, dll):
        self.dll = ctypes.cdll.LoadLibrary(os.path.join(self.BASE_DIR, dll))
        for k, v in self.func_map.items():
            try:
                self.func_map[k] = self.dll_func(self.dll.__getattr__("librg_" + k), cast=v)
            except AttributeError as e:
                log.error(f"Tried generating non existent func librg_{k}", exc_info=e)
                raise

    def __getattr__(self, item):
        """Check if func exists in func map, otherwise send call to dll as fail over."""
        try:
            return self.func_map[item]
        except KeyError:
            return self.dll.__getattr__("librg_" + item)

    def dll_func(self, func, cast=bool):
        """Returns a function wrapper which casts a return value to a given type.
        Arguments:
            func(callable):
            cast(callable):
        Returns:
            callable - The wrapped function which will cast on return
        """
        assert callable(cast) or cast is None

        def predicate(*args, **kwargs):
            if cast is not None:
                return cast(self.dll.__getattr__(func.__name__)(*args, **kwargs))
            else:
                return self.dll.__getattr__(func.__name__)(*args, **kwargs)
        return predicate

    def network_start(self, ctx: Context, address: bytes, port: int):
        """Start network on given address and port bind.
        Arguments:
            ctx(Context): Server context object
            address(bytes): Address to listen to, e.g: "localhost" or "192.168.0.10" etc
            port(int): Valid port number, must not be in use.
        Returns:
            Context: Should be stored in the server object for use
        Raises:
            Exception: Starting the network failed.
        """

        if bool(ret := self.dll.librg_network_start(ctx, Address(port, address))):
            raise Exception(f"Network Start Failed, return {ret}")  # TODO: Use custom exception class
