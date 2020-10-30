import logging
import os
from random import randint
import requests

from typing import List, Set, Dict, Union
import bencodepy
from torrent import Torrent

BASE_DIR: str = os.path.dirname(__file__)
CLIENT_ID: str = "BT"
VERSION: tuple = (0, 0, 10)
MAX_PEERS: int = 50
PeersType = List[Dict[bytes, Union[int, bytes]]]

# TODO
#  1. Limit number of peers to fetch
#  2. Add timeout for requests


class PeerManager:
    """Manage all peers"""

    def __init__(self, torrent: Torrent):
        self.peer_id: bytes = self.generate_peer_id()
        self.trackers: Set[str] = torrent.trackers
        self.info_hash: bytes = torrent.info_hash
        self.total_length: int = torrent.total_length
        self.port: int = 6881
        self.peers: PeersType = []

    def get_peers(self) -> None:
        """Get list of all peers from the given trackers"""
        params = {
            "info_hash": self.info_hash,
            "peer_id": self.peer_id,
            "port": self.port,
            "uploaded": 0,
            "downloaded": 0,
            "left": self.total_length,
        }
        for tracker in self.trackers:
            try:
                data = requests.get(tracker, params=params)
                self.scrape_response(data.content)
            except Exception as err:
                print(err)
            else:
                logging.debug(f"successfully connected to tracker: {tracker}")

    def scrape_response(self, res):
        self.peers += bencodepy.decode(res)[b"peers"]

    @staticmethod
    def generate_peer_id() -> bytes:
        """generate a unique peer id for client using azureus-style"""
        peer_id: str = (
            "-"
            + CLIENT_ID
            + "".join(map(str, VERSION))
            + "-"
            + "".join(str(randint(0, 9)) for i in range(12))
        )
        logging.info(f"peer id of client is {peer_id}")
        return peer_id.encode()

    def __repr__(self):
        res: str = ""
        res += f"peer id: {self.peer_id}\n"
        res += "trackers:\n"
        for t in self.trackers:
            res += f"- {t}\n"
        res += "peers:\n"
        for peer in self.peers:
            res += f"- ip: {peer[b'ip']}\n  peer id: {peer[b'peer id']}\n  port: {peer[b'port']}\n"
        return res


# TODO: 1. get trackers
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    file_name = "../tests/data/ubuntu-20.04.1-desktop-amd64.iso.torrent"
    #  file_name = "../tests/data/manjaro-gnome-20.1.2-201019-linux58.iso.torrent"
    #  file_name = "../tests/data/torrent-dl.torrent"
    torrent = Torrent()
    torrent.open_from_file(os.path.join(BASE_DIR, file_name))
    PeerManager(torrent)
