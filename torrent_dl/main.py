import os
import socket
import struct
import logging
from torrent import Torrent
from peer_manager import PeerManager
from peer import Peer
from messages import Handshake, Interested
import bitstring
import multiprocessing

BASE_DIR: str = os.path.dirname(__file__)


class DownloadManager:
    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        self.pm = PeerManager(torrent)
        self.pm.get_peers()
        self.connected = []

    def conn(self):
        p = self.pm.peers[0]
        pr = Peer(p[b"peer id"], p[b"ip"], p[b"port"])
        #  if pr.connect():
            #  self.connected.append(pr)
        #  m = multiprocessing.Process(target=pr.connect)
        #  m.start()
        pr.connect()
        info_hash = self.torrent.info_hash
        peer_id = self.pm.peer_id
        pr.handle_handshake(info_hash, peer_id)
        #  pr.write_buffer = .to_bytes()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    file_name = "../tests/data/ubuntu-20.04.1-desktop-amd64.iso.torrent"
    #  file_name = "../tests/data/manjaro-gnome-20.1.2-201019-linux58.iso.torrent"
    #  file_name = "../tests/data/torrent-dl.torrent"
    torrent = Torrent()
    torrent.open_from_file(os.path.join(BASE_DIR, file_name))
    d = DownloadManager(torrent)
    d.conn()
