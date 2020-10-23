import logging
import os
from random import randint
import asyncio
from yarl import URL
from aiohttp import ClientSession

from typing import List, Set, Dict, Union
import bencodepy
from torrent import Torrent
import urllib

BASE_DIR: str = os.path.dirname(__file__)
CLIENT_ID: str = "BT"
VERSION: tuple = (0, 0, 10)
MAX_PEERS: int = 50
PeersType = List[Dict[str, Union[str, int, bytes]]]


class PeerManager:
    """Manage all peers"""

    def __init__(self, torrent: Torrent):
        self.peer_id: str = self.generate_peer_id()
        self.trackers: Set[str] = torrent.trackers
        self.info_hash: bytes = torrent.info_hash
        self.total_length: int = torrent.total_length
        self.port: int = 6881
        self.peers: PeersType = []
        asyncio.run(self.get_peers())
        logging.debug(self)

    async def _get_peers_from_tracker(self, url: str, session: ClientSession) -> None:
        try:
            async with session.get(url) as res:
                t = await res.read()
                self.scrape_response(t)
        except Exception as e:
            logging.error(e)

    async def get_peers(self):
        """Get list of all peers from the given trackers"""
        params = urllib.parse.urlencode(
            {
                "info_hash": self.info_hash,
                "peer_id": self.peer_id,
                "port": self.port,
                "uploaded": 0,
                "downloaded": 0,
                "left": self.total_length,
            }
        )
        async with ClientSession() as session:
            tasks = []
            for tracker in self.trackers:
                url = URL(f"{tracker}?{params}", encoded=True)
                print(url)
                tasks.append(self._get_peers_from_tracker(url, session))
            await asyncio.gather(*tasks)

    def scrape_response(self, res):
        bc = bencodepy.Bencode(encoding="utf-8", encoding_fallback="value")
        print(bc.decode(res)["peers"])
        self.peers += bc.decode(res)["peers"]
        print(self.peers)

    @staticmethod
    def generate_peer_id() -> str:
        """generate a unique peer id for client using azureus-style"""
        peer_id: str = (
            "-"
            + CLIENT_ID
            + "".join(map(str, VERSION))
            + "-"
            + "".join(str(randint(0, 9)) for i in range(12))
        )
        logging.info(f"peer id of client is {peer_id}")
        return peer_id

    def __repr__(self):
        res: str = ""
        res += f"peer id: {self.peer_id}\n"
        res += "trackers:\n"
        for t in self.trackers:
            res += f"- {t}\n"
        res += "peers:\n"
        for peer in self.peers:
            res += f"- ip: {peer['ip']}\n  peer id: {peer['peer id']}\n  port: {peer['port']}\n"
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
