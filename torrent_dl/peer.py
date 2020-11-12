import logging
import socket
import struct
from time import time
from typing import Final, List, Tuple
from queue import Queue

import message
from bitstring import BitArray

MAX_BUFFER: Final[int] = 4096
PEER_REQUEST_TIME: Final[float] = 0.2


class Peer:
    def __init__(self, peer_id, ip, port, info_hash, bitfield_length):
        self.peer_id: bytes = peer_id
        self.info_hash: bytes = info_hash
        self.ip: bytes = ip
        self.port: int = port
        self.bitfield: BitArray = BitArray(bitfield_length)
        # self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.pieces: Queue[Tuple[int, int, bytes]] = Queue()
        self.socket = None
        self.am_choking: bool = True
        self.am_interested: bool = False
        self.peer_choking: bool = True
        self.peer_interseted: bool = False
        self.handshaked: bool = False
        self.read_buffer: bytes = b""
        self.write_buffer: bytes = b""
        self.healthy: bool = False
        self.last_ping: float = 0.0
        self.requested: bool = False

    @property
    def is_ready(self) -> bool:
        return self.am_interested and (not self.peer_choking)

    @property
    def is_eligible(self) -> bool:
        return (time() - self.last_ping) > PEER_REQUEST_TIME

    def has_piece(self, piece_index: int):
        return self.bitfield[piece_index]

    def fileno(self):
        return self.socket.fileno()

    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip, self.port), timeout=2)
            self.socket.setblocking(False)
            self.healthy = True
            logging.debug(f"connected to peer - {self.ip}:{self.port}")
        except Exception as e:
            logging.error(e)
            return False
        return True

    def send(self):
        try:
            msg: bytes = self.write_buffer
            totalsent: int = 0
            while totalsent < len(msg):
                sent: int = self.socket.send(msg[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken while sending")
                totalsent = totalsent + sent
                self.write_buffer = b""
        except Exception as e:
            logging.error(e)

    def receive(self):
        data = b""

        while True:
            try:
                chunk: bytes = self.socket.recv(MAX_BUFFER)
                if len(chunk) <= 0:
                    break

                data += chunk
            except Exception as e:
                logging.exception(e)
                break

        self.read_buffer += data

    def send_handshake(self, peer_id):
        handshake: message.Handshake = message.Handshake(self.info_hash, peer_id)
        self.write_buffer += handshake.to_bytes()
        logging.info("new peer added : %s" % self.ip)

    def send_request(self, piece_index: int, block_begin: int, block_length: int):
        request: message.Request = message.Request(
            piece_index, block_begin, block_length
        )
        self.write_buffer += request.to_bytes()

    def send_interested(self):
        interested: message.Interested = message.Interested()
        self.write_buffer += interested.to_bytes()

    def handle_handshake(self):
        try:
            hs_recd: message.Handshake = message.Handshake.from_bytes(self.read_buffer)
            self.read_buffer = self.read_buffer[hs_recd.total_length :]

            if hs_recd.info_hash != self.info_hash:
                raise ValueError("Infohash of handshake doesn't match")
            if hs_recd.peer_id != self.peer_id:
                raise ValueError("Peer ID of handshake doesn't match")

            logging.debug(
                f"Handshake successful with peer - {self.peer_id}:{self.port}"
            )
            self.handshaked = True

        except Exception as e:
            logging.exception(e)
            self.healthy = False
            return False

        return True

    def handle_bitfield(self, bitfield: message.Bitfield):
        self.bitfield = bitfield.bitfield
        logging.debug(f"Bitfield - {self.bitfield}")
        self.send_interested()

    def handle_unchoke(self):
        self.am_interested = True
        self.peer_choking = False
        logging.debug(f"Peer - {self.ip} has unchocked")

    def handle_choke(self):
        self.peer_choking = True
        logging.debug(f"Peer - {self.ip} is choking")

    def handle_interested(self):
        self.peer_interseted = True
        if self.am_choking:
            self.write_buffer += message.UnChoke().to_bytes()
        logging.debug(f"Peer - {self.ip} is interested")

    def handle_not_interested(self):
        self.peer_interseted = False
        logging.debug(f"Peer - {self.ip} is not interested")

    def handle_have(self, have: message.Have):
        self.bitfield[have.piece_index] = True
        logging.debug(f"Peer - {str(self.ip)} sent have message")

    def handle_request(self, request: message.Request):
        # if self.peer_interseted and not self.am_choking:
        pass

    def handle_piece(self, piece: message.Piece):
        self.pieces.put((piece.piece_index, piece.block_begin, piece.block))

    def handle_cancel(self):
        pass

    def handle_port_request(self):
        pass

    def handle_keep_alive(self):
        try:
            keep_alive = message.KeepAlive.from_bytes(self.read_buffer)
            logging.debug(f"handle_keep_alive - {self.ip}")
        except Exception as e:
            logging.exception(e)
            return False
        self.read_buffer = self.read_buffer[keep_alive.total_length :]
        return True

    def get_messages(self):
        while len(self.read_buffer) > 4 and self.healthy:
            if not self.handshaked and self.handle_handshake():
                continue

            (payload_length,) = struct.unpack(">I", self.read_buffer[:4])
            total_length = payload_length + 4

            if len(self.read_buffer) < total_length:
                break
            else:
                payload = self.read_buffer[:total_length]
                self.read_buffer = self.read_buffer[total_length:]

            try:
                received_message = message.MessageDispatcher(payload).dispatch()
                if received_message:
                    yield received_message
            except Exception as e:
                logging.exception(e)
