import logging
import os

from peer_manager import PeerManager
from torrent import Torrent
from piece_manager import PieceManager
from peer import Peer
from piece import Piece
import message
import time

BASE_DIR: str = os.path.dirname(__file__)


class DownloadManager:
    def __init__(self, torrent: Torrent):
        self.torrent: Torrent = torrent
        self.peer_manager: PeerManager = PeerManager(torrent)
        self.piece_manager: PieceManager = PieceManager(torrent)

    def start(self):
        self.peer_manager.get_peers()
        self.peer_manager.start()

        while not self.piece_manager.all_pieces_completed:
            if not self.peer_manager.has_unchoked_peers:
                time.sleep(1)
                logging.info("No unchoked peers")
                continue

            for piece in self.piece_manager.get_required_pieces():
                peer: Peer = self.peer_manager.get_peer_having_piece(piece.index)
                if not peer:
                    continue

                block = piece.get_required_block()
                if not block:
                    continue

                block_begin, block_length = block
                peer.send_request(piece.index, block_begin, block_length)

                while not peer.pieces.empty():
                    self.piece_manager.process_new_block(peer.pieces.get())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    file_name = "../tests/data/ubuntu-20.04.1-desktop-amd64.iso.torrent"
    #  file_name = "../tests/data/manjaro-gnome-20.1.2-201019-linux58.iso.torrent"
    #  file_name = "../tests/data/torrent-dl.torrent"
    torrent = Torrent()
    torrent.open_from_file(os.path.join(BASE_DIR, file_name))
    d = DownloadManager(torrent)
    d.start()
