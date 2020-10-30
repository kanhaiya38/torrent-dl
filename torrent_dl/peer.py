from messages import Handshake
import logging
import threading
from threading import Thread
import socket


class Peer(Thread):
    def __init__(self, peer_id, ip, port):
        super().__init__()
        self.peer_id = peer_id
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()
        self.lock1 = threading.Lock()
        self.client_choking = True
        self.client_interested = False
        self.peer_choking = True
        self.peer_interseted = False
        self.write_buffer = b""
        self.read_buffer = b""
        self.handshake = False

    def connect(self):
        try:
            self.sock.connect((self.ip, self.port))
            #  self.sock.setblocking(False)
            logging.debug(f"connected to peer - {self.ip}:{self.port}")
            #  send_thread = threading.Thread(target=self.send)
            #  recv_thread = threading.Thread(target=self.receive)
            #  send_thread.start()
            #  recv_thread.start()
            #  send_thread.join()
            #  recv_thread.join()
            #  print("here")
        except Exception as e:
            logging.exception(e)
            return False
        return True

    def send(self):
        while True:
            if not self.write_buffer == b"":
                print(self.write_buffer)
                with self.lock:
                    print("fuck")
                    try:
                        msg = self.write_buffer
                        totalsent = 0
                        while totalsent < len(msg):
                            sent = self.sock.send(msg[totalsent:])
                            if sent == 0:
                                raise RuntimeError("socket connection broken")
                            totalsent = totalsent + sent
                            self.write_buffer = b""
                    except Exception as e:
                        logging.error(e)

    def receive(self):
        while True:
            if self.read_buffer == b"":
                with self.lock1:
                    try:
                        chunk = self.sock.recv(1024)
                        print("got", chunk)
                        if chunk == b"":
                            raise RuntimeError("socket connection broken")
                        self.read_buffer = chunk
                    except Exception as e:
                        logging.error(e)

    def handle_handshake(self, info_hash, peer_id):
        hs_sent = Handshake(info_hash, peer_id)
        #  self.send(hs_sent.to_bytes())
        with self.lock:
            self.write_buffer = hs_sent.to_bytes()
        #  hs_recv = self.receive(Handshake.total_length)
        #  self.read_buffer =
        #  if hs_recv.info_hash != hs_sent.info_hash:
        #      raise ValueError("Infohash of handshake doesn't match")
        #  if hs_recv.peer_id != self.peer_id:
        #      raise ValueError("Peer ID of handshake doesn't match")
        #  logging.debug(f"Handshake successful with peer - {self.peer_id}:{self.port}")
