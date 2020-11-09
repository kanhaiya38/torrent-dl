import logging
import math
import os

import bitstring
from peer_manager import PeerManager
from torrent import Torrent

BASE_DIR: str = os.path.dirname(__file__)


class DownloadManager:
    def __init__(self, torrent: Torrent):
        self.torrent = torrent
        self.pm = PeerManager(torrent)
        self.bitfield = bitstring.BitArray(math.ceil(len(self.torrent.pieces) / 8))

    def conn(self):
        self.pm.get_peers()
        self.pm.start()
        # print(self.torrent.pieces)
        # p = self.pm.peers[0]
        # pr = Peer(
        #  p[b"peer id"], p[b"ip"], p[b"port"], self.info_hash, len(self.bitfield)
        # )
        # if pr.connect():
        # self.connected.append(pr)
        # m = multiprocessing.Process(target=pr.connect)
        # m.start()
        # print(self.bitfield)
        # p.connect()
        # p.send()
        # p.receive()
        # print(p.read_buffer)
        # p.handle_handshake()
        # p.receive()
        # print(p.read_buffer)
        # p.handle_bitfield()
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
