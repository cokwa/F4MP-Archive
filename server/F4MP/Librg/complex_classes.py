"""Pythonised versions of the Librg class objects"""
import ctypes
from .callback import Enum


class F4MPAbc:
    def __init__(self, *args, **kwargs):
        for arg, val in zip(self.__slots__, args):
            setattr(self, arg, val)

        for attrib, value in kwargs.items():
            self.__setattr__(attrib, value)


class Peer(F4MPAbc):
    class Host(F4MPAbc):
        __slots__ = ("_socket", "_address_host")

        @classmethod
        def from_struct(cls, data):
            self = cls.__new__(cls)
            self._socket = data.socket
            self._address_host = data.address_host

            return self

    __slots__ = ("_dispatch_list", "host")

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)
        self._dispatch_list = data.dispatch_list
        self.host(Peer.Host.from_struct(data.host.contents))

        return self


class Data(F4MPAbc):
    __slots__ = ("capacity", "read_pos", "write_pos", "_rawptr", "_allocator")

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)
        self.capacity = int(data.capacity)
        self.read_pos = int(data.read_pos)
        self.write_pos = int(data.write_pos)
        self._rawptr = data.rawptr
        self._allocator = data.allocator

        return self


class Entity:
    __slots__ = ("id", "type", "flags", "position", "stream_range", "_user_data", "_stream_branch",
                 "_visibility", "virtual_world", "_last_snapshot", "client_peer", "control_peer",
                 "control_generation", "last_query")

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)
        self.id = int(data.id)
        self.type = int(data.type)
        self.flags = int(data.flags)
        self.position = list(map(lambda x: float(x), data.position))
        self.stream_range = float(data.stream_range)
        self.virtual_world = int(data.virtual_world)
        self.client_peer = Peer.from_struct(data.client_peer.contents)
        self.control_peer = Peer.from_struct(data.control_peer.contents)
        self.control_generation = int(data.control_generation)
        self.last_query = int(data.last_query.contents)

        for attr in ("user_data", "stream_branch", "visibility", "last_snapshot"):
            try:
                value = data.__getattr__(attr)
                if isinstance(value, ctypes.pointer):
                    value = value.contents
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self


class Address(F4MPAbc):
    __slots__ = ("host", "port")

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)
        self.port = int(data.port)
        self.host = str(data.host)

        return self


class _StreamsSubC(F4MPAbc):
    __slots__ = ("stream_input", "stream_output", "stream_upd_reliable", "stream_upd_unreliable")

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)
        self.stream_input = Data.from_struct(data.stream_input)
        self.stream_output = Data.from_struct(data.stream_output)
        self.stream_upd_reliable = Data.from_struct(data.stream_upd_reliable)
        self.stream_upd_unreliable = Data.from_struct(data.stream_upd_unreliable)

        return self


class Context(F4MPAbc):
    class Network(F4MPAbc):
        __slots__ = ("peer", "host", "connected_peers", "last_address", "created", "connected")

        @classmethod
        def from_struct(cls, data):
            self = cls.__new__(cls)
            self.peer = Peer.from_struct(data.peer.content)
            self.last_address = Address.from_struct(data.last_address)
            self.created = int(data.created)
            self.connected = int(data.connected)

            for attr in ("host", "connected_peers", "created", "connected"):
                try:
                    value = data.__getattr__(attr)
                except KeyError:
                    continue
                else:
                    setattr(self, "_" + attr, value)

            return self

    class Entity(F4MPAbc):
        __slots__ = ("count", "cursor", "_visibility", "list", "remove_queue", "_add_control_queue")

        @classmethod
        def from_struct(cls, data):
            self = cls.__new__(cls)
            self.count = int(data.count)
            self.cursor = int(data.cursor)
            self.list = Entity.from_struct(data.list.contents)
            self.remove_queue = int(data.remove_queue.contents)

            for attr in ("visibility", "add_control_queue"):
                try:
                    value = data.__getattr__(attr)
                    if isinstance(value, ctypes.pointer):
                        value = value.contents
                except KeyError:
                    continue
                else:
                    setattr(self, "_" + attr, value)
            return self

    class Streams(F4MPAbc):
        __slots__ = ("struct", "streams")

        @classmethod
        def from_struct(cls, data):
            self = cls.__new__(cls)
            self.struct = _StreamsSubC.from_struct(data.struct)
            self.streams = list(map(lambda x: Data.from_struct(x), data.streams))
            return self

    __slots__ = ("mode", "tick_delay", "max_connections", "max_entities",
                 "world_size", "min_branch_size", "last_update", "_user_data",
                 "network", "entity", "streams", "_timesync", "buffer_size",
                 "_buffer_timer", "_buffer", "_messages", "_allocator", "_timers",
                 "_events", "_world")

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)
        self.mode = int(data.mode)
        self.tick_delay = float(data.tick_delay)
        self.max_connections = int(data.max_connections)
        self.max_entities = int(data.max_entities)
        self.world_size = tuple(map(lambda x: float(x), data.world_size))
        self.min_branch_size = tuple(map(lambda x: float(x), data.min_branch_size))
        self.last_update = float(data.last_update)
        self.network = Context.Network.from_struct(data.network)
        self.entity = Context.Entity.from_struct(data.entity)
        self.streams = Context.Streams.from_struct(data.streams)
        self.buffer_size = int(data.buffer_size)

        for attr in ("user_data", "timesync", "buffer_timer", "buffer",
                     "messages", "allocator", "timers", "events", "world"):
            try:
                value = data.__getattr__(attr)
                if isinstance(value, ctypes.pointer):
                    value = value.contents
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self


class Event(F4MPAbc):
    __slots__ = (
        "id", "ctx", "data", "entity", "peer", "_flags", "_user_data"
    )

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)

        self.id = data.id
        self.type = Enum.reverse[data.id]
        self.ctx = Context.from_struct(data.ctx.content)
        self.data = Data.from_struct(data.data.content)
        self.entity = Entity.from_struct(data.entity.content)
        self.peer = Peer.from_struct(data.peer.content)

        for attr in ("flags", "user_data"):
            try:
                value = data.__getattr__(attr)
                if isinstance(value, ctypes.pointer):
                    value = value.contents
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self


class Message(F4MPAbc):
    __slots__ = (
        "id", "ctx", "data", "peer", "_packet", "_user_data"
    )

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)

        self.id = int(data.id)
        self.ctx = Context.from_struct(data.ctx.content)
        self.data = Data.from_struct(data.data.content)
        self.peer = Peer.from_struct(data.peer.content)

        for attr in ("packet", "user_data"):
            try:
                value = data.__getattr__(attr)
                if isinstance(value, ctypes.pointer):
                    value = value.contents
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self
