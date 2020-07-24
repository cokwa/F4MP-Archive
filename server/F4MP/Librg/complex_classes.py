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

    __slots__ = ("_dispatch_list", "_host_ptr")

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)
        self._dispatch_list = data.dispatch_list
        self._host_ptr = data.host

        return self

    @property
    def host(self):
        return Peer.Host.from_struct(self.host.contents)


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
                 "_visibility", "virtual_world", "_last_snapshot", "_client_peer_ptr", "_control_peer_ptr",
                 "control_generation", "_last_query_ptr")

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)
        self.id = int(data.id)
        self.type = int(data.type)
        self.flags = int(data.flags)
        self.position = list(map(lambda x: float(x), data.position))
        self.stream_range = float(data.stream_range)
        self.virtual_world = int(data.virtual_world)
        self._client_peer_ptr = data.client_peer
        self._control_peer_ptr = data.control_peer
        self.control_generation = int(data.control_generation)
        self._last_query_ptr = data.last_query

        for attr in ("user_data", "stream_branch", "visibility", "last_snapshot"):
            try:
                value = getattr(self, attr)
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self

    @property
    def client_peer(self):
        return Peer.from_struct(self._client_peer_ptr.contents)

    @property
    def control_peer(self):
        return Peer.from_struct(self._control_peer_ptr.contents)

    @property
    def last_query(self):
        return int(self._last_query_ptr.contents)


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
        __slots__ = ("_peer_ptr", "host", "connected_peers", "last_address", "created", "connected")

        @classmethod
        def from_struct(cls, data):
            self = cls.__new__(cls)
            self._peer_ptr = data.peer
            self.last_address = Address.from_struct(data.last_address)
            self.created = int(data.created)
            self.connected = int(data.connected)

            for attr in ("host", "connected_peers", "created", "connected"):
                try:
                    value = getattr(self, attr)
                except KeyError:
                    continue
                else:
                    setattr(self, "_" + attr, value)

            return self

        @property
        def peer(self):
            return Peer.from_struct(self._peer_ptr.content)

    class Entity(F4MPAbc):
        __slots__ = ("count", "cursor", "_visibility", "_list_ptr", "remove_queue", "_add_control_queue")

        @classmethod
        def from_struct(cls, data):
            self = cls.__new__(cls)
            self.count = int(data.count)
            self.cursor = int(data.cursor)
            self._list_ptr = data.list
            self.remove_queue = int(data.remove_queue.contents)

            for attr in ("visibility", "add_control_queue"):
                try:
                    value = getattr(self, attr)
                except KeyError:
                    continue
                else:
                    setattr(self, "_" + attr, value)
            return self

        @property
        def list(self):
            return Entity.from_struct(self._list_ptr.contents)

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
                value = getattr(self, attr)
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self


class Event(F4MPAbc):
    __slots__ = (
        "id", "_ctx_ptr", "_data_ptr", "_entity_ptr", "_peer_ptr", "_flags", "_user_data"
    )

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)

        self.id = data.id
        self.type = Enum.reverse[data.id]
        self._ctx_ptr = data.ctx
        self._data_ptr = data.data
        self._entity_ptr = data.entity
        self._peer_ptr = data.peer

        for attr in ("flags", "user_data"):
            try:
                value = getattr(data, attr)
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self

    @property
    def ctx(self):
        return Context.from_struct(self._ctx_ptr.contents)

    @property
    def data(self):
        return Data.from_struct(self._data_ptr.contents)

    @property
    def entity(self):
        return Entity.from_struct(self._entity_ptr.contents)

    @property
    def peer(self):
        return Peer.from_struct(self._peer_ptr.content)


class Message(F4MPAbc):
    __slots__ = (
        "id", "_ctx_ptr", "_data_ptr", "_peer_ptr", "_packet", "_user_data"
    )

    @classmethod
    def from_struct(cls, data):
        self = cls.__new__(cls)

        self.id = int(data.id)
        self._ctx_ptr = data.ctx
        self._data_ptr = data.data
        self._peer_ptr = data.peer

        for attr in ("packet", "user_data"):
            try:
                value = getattr(self, attr)
            except KeyError:
                continue
            else:
                setattr(self, "_" + attr, value)

        return self

    @property
    def ctx(self):
        try:
            return Context.from_struct(self._ctx_ptr.contents)
        except ValueError:
            return None

    @property
    def data(self):
        try:
            return Data.from_struct(self._data_ptr.contents)
        except ValueError:
            return None

    @property
    def peer(self):
        try:
            return Peer.from_struct(self._peer_ptr.contents)
        except ValueError:
            return None
