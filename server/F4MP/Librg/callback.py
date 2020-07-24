from ctypes import CFUNCTYPE
from F4MP import Librg
from F4MP.Librg import simple_classes

class Enum:
    LIBRG_CONNECTION_INIT = 0
    LIBRG_CONNECTION_REQUEST = 1
    LIBRG_CONNECTION_REFUSE = 2
    LIBRG_CONNECTION_ACCEPT = 3
    LIBRG_CONNECTION_DISCONNECT = 4
    LIBRG_CONNECTION_TIMEOUT = 5
    LIBRG_CONNECTION_TIMESYNC = 6

    LIBRG_ENTITY_CREATE = 7
    LIBRG_ENTITY_UPDATE = 8
    LIBRG_ENTITY_REMOVE = 9
    LIBRG_CLIENT_STREAMER_ADD = 10
    LIBRG_CLIENT_STREAMER_REMOVE = 11
    LIBRG_CLIENT_STREAMER_UPDATE = 12

    LIBRG_EVENT_LAST = 13

    Hit = LIBRG_EVENT_LAST + 1
    FireWeapon = LIBRG_EVENT_LAST + 2
    SpawnEntity = LIBRG_EVENT_LAST + 3
    SyncEntity = LIBRG_EVENT_LAST + 4
    SpawnBuilding = LIBRG_EVENT_LAST + 5
    RemoveBuilding = LIBRG_EVENT_LAST + 6
    Speak = LIBRG_EVENT_LAST + 7

    dict = {
        "on_connection_request": LIBRG_CONNECTION_REQUEST,
        "on_connection_accepted": LIBRG_CONNECTION_ACCEPT,
        "on_connection_refused": LIBRG_CONNECTION_REFUSE,
        "on_disconnect": LIBRG_CONNECTION_DISCONNECT,
        "on_entity_create": LIBRG_ENTITY_CREATE,
        "on_entity_delete": LIBRG_ENTITY_REMOVE,
        "on_entity_update": LIBRG_ENTITY_UPDATE,
        "on_client_update": LIBRG_CLIENT_STREAMER_UPDATE
    }
    reverse = {v: k for k, v in dict.items()}

    def __getitem__(self, item):
        return self.dict[item]


class CallbackHandler:
    def __init__(self, server):
        self.server = server
        self.callback_enum = Enum
        self.callback_func = CFUNCTYPE(None, simple_classes.Event)(self.callback_reception)

        for func_name, enum in self.callback_enum.dict.items():
            self.server.call_map[func_name] = set()
            Librg.event_add(server._ctx, enum, self.callback_func)

    def callback_reception(self, event):
        event = Librg.Event.from_struct(event)
        for callback in self.server.call_map[event.type]:
            callback(event)
