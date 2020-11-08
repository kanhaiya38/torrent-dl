import struct
import message
import logging
import threading
from threading import Thread
import bitstring
import socket
from struct import pack, unpack

MAX_BUFFER: int = 4096


class Peer:
    def __init__(self, peer_id, ip, port, info_hash, bitfield_length):
        self.peer_id = peer_id
        self.info_hash = info_hash
        self.ip = ip
        self.port = port
        self.bitfield = bitstring.BitArray(bitfield_length)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #  self.socket = None
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interseted = False
        self.has_handshaked = False
        self.read_buffer = b""
        self.write_buffer = message.Handshake(self.info_hash, self.peer_id).to_bytes()
        self.is_healthy = False

    def fileno(self):
        return self.socket.fileno()

    def connect(self):
        self.socket = self.socket.connect((self.ip, self.port))
        #  self.socket.setblocking(False)
        self.is_healthy = True
        logging.debug(f"connected to peer - {self.ip}:{self.port}")

    def send(self):
        try:
            msg = self.write_buffer
            totalsent = 0
            while totalsent < len(msg):
                sent = self.socket.send(msg[totalsent:])
                if sent == 0:
                    raise RuntimeError("socket connection broken while sending")
                totalsent = totalsent + sent
                self.write_buffer = b""
        except Exception as e:
            logging.error(e)

    def receive(self):
        try:
            #  while True:
            chunk = self.socket.recv(MAX_BUFFER)
            print("got", chunk)
            if chunk == b"":
                raise RuntimeError("socket connection broken while recieving")
            self.read_buffer += chunk
        #  return chunk
        except Exception as e:
            logging.error(e)

    def send_handshake(self):
        hs_sent = message.Handshake(self.info_hash, self.peer_id)
        self.send(hs_sent.to_bytes())

    def handle_handshake(self):
        #  hs_recv = self.receive(Handshake.total_length)
        #  self.receive()
        hs_recd = message.Handshake.from_bytes(self.read_buffer)
        self.read_buffer = self.read_buffer[hs_recd.total_length :]
        self.has_handshaked = True
        if hs_recd.info_hash != self.info_hash:
            raise ValueError("Infohash of handshake doesn't match")
        if hs_recd.peer_id != self.peer_id:
            raise ValueError("Peer ID of handshake doesn't match")
        logging.debug(f"Handshake successful with peer - {self.peer_id}:{self.port}")

    def handle_bitfield(self):
        bitfield_recd = message.Bitfield.from_bytes(self.read_buffer)
        self.read_buffer = self.read_buffer[bitfield_recd.total_length :]
        self.bitfield = bitfield_recd.bitfield
        logging.debug(f"Got bitfield - {self.bitfield}")

    #  def handle_interested(self):
    # check if peer has unchoked
    # if peer has unchoked client already then dont send this message
    # if peer has not sent unchoked message send this message
    #  if len(self.read_buffer)

    def handle_keep_alive(self):
        keep_alive_recd = message.KeepAlive(self.read_buffer)
        self.read_buffer = self.read_buffer[: keep_alive_recd.total_length]
        logging.debug(f"Keep Alive message")

    def get_messages(self):
        while len(self.read_buffer) > 4 and self.is_healthy:
            if not self.has_handshaked:
                self.handle_handshake()
                continue
            else:
                self.handle_keep_alive()
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
            except message.WrongMessageException as e:
                logging.exception(e)
