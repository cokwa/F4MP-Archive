from .complex_classes import *
from . import simple_classes
from .callback import CallbackHandler

from .interface import Interface
interface = Interface(r"bin\librg.dll")
del Interface


def __getattr__(name):
    return getattr(interface, name)
