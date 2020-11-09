#  TODO:
#      1. bitfield message
#      2. port message (used for dht tracekers)
import logging
from struct import pack, unpack

import bitstring


class MessageDispatcher:
    def __init__(self, payload):
        self.payload = payload

    def dispatch(self):
        length_prefix: int
        message_id: int

        map_id_to_message = {
            0: Choke,
            1: UnChoke,
            2: Interested,
            3: NotInterested,
            4: Have,
            5: Bitfield,
            6: Request,
            7: Piece,
            8: Cancel,
            9: Port,
        }

        try:
            (length_prefix,) = unpack(">I", self.payload[:4])

            if length_prefix == 0:
                # keep alive message
                return KeepAlive.from_bytes(self.payload)

            (message_id,) = unpack(">B", self.payload[4:5])
        except Exception as e:
            logging.exception(e)

        if message_id not in map_id_to_message.keys():
            raise Exception(f"Wrong message id {message_id}")

        return map_id_to_message[message_id].from_bytes(self.payload)


class Message:
    def to_bytes(self):
        raise NotImplementedError

    def from_bytes(self, payload: bytes):
        raise NotImplementedError


class Handshake(Message):
    """handshake: <pstrlen><pstr><reserved><info_hash><peer_id>

        pstrlen: string length of <pstr> (1 byte)
        pstr: string identifier of the protocol
        reserved: eight (8) reserved bytes. All current implementations use all zeroes (8 bytes)
        info_hash: 20-byte SHA1 hash of the info key in the metainfo file (20 bytes)
        peer_id: 20-byte string used as a unique ID for the client (20 bytes)

    In version 1.0 of the BitTorrent protocol, pstrlen = 19, and pstr = "BitTorrent protocol".
    """

    pstr: bytes = b"BitTorrent protocol"
    pstrlen: int = len(pstr)
    encoding_format: str = f">B{pstrlen}s8s20s20s"
    total_length: int = 68

    def __init__(self, info_hash: bytes, peer_id: bytes):
        super().__init__()
        self.info_hash: bytes = info_hash
        self.peer_id: bytes = peer_id

    def to_bytes(self):
        reserved: bytes = b"\x00" * 8

        return pack(
            self.encoding_format,
            self.pstrlen,
            self.pstr,
            reserved,
            self.info_hash,
            self.peer_id,
        )

    @classmethod
    def from_bytes(cls, payload: bytes):
        pstrlen: int
        pstr: str
        reserved: bytes
        info_hash: bytes
        peer_id: bytes

        pstrlen, pstr, reserved, info_hash, peer_id = unpack(
            cls.encoding_format, payload[: cls.total_length]
        )

        if pstr != cls.pstr:
            raise ValueError("Invalid pstr")

        return cls(info_hash, peer_id)


class KeepAlive(Message):
    """keep-alive: <len=0000>

    length prefix: 0 (4 bytes)
    message id: NO
    payload: NO
    """

    encoding_format: str = ">I"
    length_prefix: int = 0
    total_length: int = 4

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack(self.encoding_format, self.length_prefix)

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix: int

        (length_prefix,) = unpack(cls.encoding_format, payload[: cls.total_length])

        if length_prefix != cls.length_prefix:
            raise ValueError("Invalid KeepAlive message")

        return cls()


class Choke(Message):
    """choke: <len=0001><id=0>

    length prefix: 1 (4 bytes)
    message id: 0 (1 byte)
    payload: NO
    """

    length_prefix: int = 1
    encoding_format: str = ">IB"
    message_id: int = 0

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack(self.encoding_format, self.length_prefix, self.message_id)

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix: int
        message_id: int

        length_prefix, message_id = unpack(cls.encoding_format, payload)

        if length_prefix != cls.length_prefix:
            raise Exception("Invalid prefix length for Choke message")

        if message_id != cls.message_id:
            raise Exception("Invalid message id for Choke message")

        return cls()


class UnChoke(Message):
    """unchoke: <len=0001><id=1>

    length prefix: 1 (4 bytes)
    message id: 1 (1 byte)
    payload: NO
    """

    length_prefix: int = 1
    encoding_format: str = ">IB"
    message_id: int = 1

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack(self.encoding_format, self.length_prefix, self.message_id)

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix: int
        message_id: int

        length_prefix, message_id = unpack(cls.encoding_format, payload)

        if length_prefix != cls.length_prefix:
            raise Exception("Invalid prefix length for Unchoke message")

        if message_id != cls.message_id:
            raise Exception("Invalid message id for Unchoke message")

        return cls()


class Interested(Message):
    """interested: <len=0001><id=2>

    length prefix: 1 (4 bytes)
    message id: 2 (1 byte)
    payload: NO
    """

    length_prefix: int = 1
    encoding_format: str = ">IB"
    message_id: int = 2

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack(self.encoding_format, self.length_prefix, self.message_id)

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix: int
        message_id: int

        length_prefix, message_id = unpack(cls.encoding_format, payload)

        if length_prefix != cls.length_prefix:
            raise Exception("Invalid prefix length for Interested message")

        if message_id != cls.message_id:
            raise Exception("Invalid message id for Interested message")

        return cls()


class NotInterested(Message):
    """not interested: <len=0001><id=3>

    length prefix: 1 (4 bytes)
    message id: 3 (1 byte)
    payload: NO
    """

    length_prefix: int = 1
    encoding_format: str = ">IB"
    message_id: int = 3

    def __init__(self):
        super().__init__()

    def to_bytes(self):
        return pack(self.encoding_format, self.length_prefix, self.message_id)

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix: int
        message_id: int

        length_prefix, message_id = unpack(cls.encoding_format, payload)

        if length_prefix != cls.length_prefix:
            raise Exception("Invalid prefix length for NotInterested message")

        if message_id != cls.message_id:
            raise Exception("Invalid message id for NotInterested message")

        return cls()


class Have(Message):
    """have: <len=0005><id=4><piece index>

    length prefix: 5 (4 bytes)
    message id: 4 (1 byte)
    payload: (4 bytes)
        piece index: zero-based index of a piece that has just been successfully downloaded and verified via the hash (4 bytes)
    """

    length_prefix: int = 5
    encoding_format: str = ">IBI"
    message_id: int = 4

    def __init__(self, piece_index):
        super().__init__()
        self.piece_index: int = piece_index

    def to_bytes(self):
        return pack(
            self.encoding_format, self.length_prefix, self.message_id, self.piece_index
        )

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix: int
        message_id: int
        piece_index: int

        length_prefix, message_id, piece_index = unpack(cls.encoding_format, payload)

        if length_prefix != cls.length_prefix:
            raise Exception("Invalid prefix length for Have message")

        if message_id != cls.message_id:
            raise Exception("Invalid message id for Have message")

        return cls(piece_index)


class Bitfield(Message):
    """bitfield: <len=0001+X><id=5><bitfield>

    length prefix: 1 + bitfield length (4 bytes)
    message id: 5 (1 byte)
    payload: (X bytes)
        bitfield: bitfield representing the pieces that have been successfully downloaded (X bytes)
    """

    message_id: int = 5

    def __init__(self, bitfield: bitstring.BitArray):
        super().__init__()
        self.bitfield: bitstring.BitArray = bitfield
        self.bitfield_length: int = len(self.bitfield)
        self.length_prefix: int = 1 + self.bitfield_length
        self.encoding_format: str = f">IB{self.bitfield_length}s"
        self.total_length = self.length_prefix + 4

    def to_bytes(self):

        return pack(
            self.encoding_format, self.length_prefix, self.message_id, self.bitfield
        )

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix: int
        message_id: int
        raw_bitfield: bytes
        bitfield: bitstring.BitArray

        length_prefix, message_id = unpack(
            ">IB", payload[:5]
        )  # length_prefix + message_id = 5 bytes

        if message_id != cls.message_id:
            raise Exception("Invalid message id for Bitfield message")

        bitfield_length = length_prefix - 1
        total_length = length_prefix + 4
        (raw_bitfield,) = unpack(f">{bitfield_length}s", payload[5:total_length])

        bitfield = bitstring.BitArray(raw_bitfield)

        return cls(bitfield)


class Request(Message):
    """request: <len=0013><id=6><index><begin><length>

    length prefix: 13 (4 bytes)
    message id: 6 (1 byte)
    payload: (12 bytes)
        index: integer specifying the zero-based piece index (4 bytes)
        begin: integer specifying the zero-based byte offset within the piece (4 bytes)
        length: integer specifying the requested length (4 bytes)
    """

    length_prefix: int = 13
    message_id: int = 6
    encoding_format: str = ">IB4s4s4s"

    def __init__(self, index, begin, length):
        super().__init__()
        self.piece_index = index
        self.block_begin = begin
        self.block_length = length

    def to_bytes(self):
        return pack(
            self.encoding_format,
            self.length_prefix,
            self.message_id,
            self.piece_index,
            self.block_begin,
            self.block_length,
        )

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix, message_id, piece_index, block_begin, block_length = unpack(
            cls.encoding_format, payload
        )

        if length_prefix != cls.length_prefix:
            raise Exception("Invalid prefix length for Request message")

        if message_id != cls.message_id:
            raise Exception("Invalid message id for Request message")

        return cls(piece_index, block_begin, block_length)


class Piece(Message):
    """piece: <len=0009+X><id=7><index><begin><block>

    length prefix: 9 + block length (4 bytes)
    message id: 7 (1 bytes)
    payload: (X bytes)
        index: integer specifying the zero-based piece index (4 bytes)
        begin: integer specifying the zero-based byte offset within the piece (4 bytes)
        block: block of data, which is a subset of the piece specified by index (block length bytes)
    """

    message_id = 7

    def __init__(self, index, begin, block):
        super().__init__()
        self.piece_index = index
        self.block_begin = begin
        self.block = block
        self.block_length: int = len(block)
        self.length_prefix: int = 9 + self.block_length
        self.encoding_format: str = f">IB4s4s{self.block_length}s"

    def to_bytes(self):
        return pack(
            self.encoding_format,
            self.length_prefix,
            self.message_id,
            self.piece_index,
            self.block_begin,
            self.block,
        )

    @classmethod
    def from_bytes(cls, payload: bytes):
        block_length = len(payload) - 13

        length_prefix, message_id, piece_index, block_begin, block = unpack(
            f">IB4s4s{block_length}s", payload
        )

        if message_id != cls.message_id:
            raise Exception("Invalid message id for Piece message")

        return cls(piece_index, block_begin, block)


class Cancel(Message):
    """cancel: <len=0013><id=8><index><begin><length>

    length prefix: 13 (4 bytes)
    message id: 8 (1 byte)
    payload: (12 bytes)
        index: integer specifying the zero-based piece index (4 bytes)
        begin: integer specifying the zero-based byte offset within the piece (4 bytes)
        length: integer specifying the requested length (4 bytes)
    """

    length_prefix = 13
    message_id = 8
    encoding_format = ">IB4s4s4s"

    def __init__(self, index, begin, length):
        super().__init__()
        self.piece_index = index
        self.block_begin = begin
        self.block_length = length

    def to_bytes(self):
        return pack(
            self.encoding_format,
            self.length_prefix,
            self.message_id,
            self.piece_index,
            self.block_begin,
            self.block_length,
        )

    @classmethod
    def from_bytes(cls, payload: bytes):
        length_prefix, message_id, piece_index, block_begin, block_length = unpack(
            cls.encoding_format, payload
        )

        if length_prefix != cls.length_prefix:
            raise Exception("Invalid prefix length for Cancel message")

        if message_id != cls.message_id:
            raise Exception("Invalid message id for Cancel message")

        return cls(piece_index, block_begin, block_begin)


class Port(Message):
    pass
