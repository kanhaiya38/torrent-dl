import logging
import math
import os
import select
from random import randint, choice
from threading import Thread
from typing import Dict, List, Set, Union

import bencodepy
import message
import requests
from peer import Peer
from math import ceil
from torrent import Torrent

BASE_DIR: str = os.path.dirname(__file__)
CLIENT_ID: str = "BT"
VERSION: tuple = (0, 0, 10)
MAX_PEERS: int = 50
MAX_CONNECTED_PEERS: int = 5
PeersType = List[Dict[bytes, Union[int, bytes]]]

# TODO
#  1. Limit number of peers to fetch
#  2. Add timeout for requests


class PeerManager(Thread):
    """Manage all peers"""

    def __init__(self, torrent: Torrent):
        super().__init__()
        self.peer_id: bytes = self.generate_peer_id()
        self.trackers: Set[str] = torrent.trackers
        self.raw_peers: PeersType = []
        self.info_hash: bytes = torrent.info_hash
        self.total_length: int = torrent.total_length
        self.bitfield_length = ceil(len(torrent.pieces) / 8)
        self.port: int = 6881
        self.is_active = True
        self.peers: List[Peer] = []

    def get_peers(self) -> None:
        """Get list of all peers from the given trackers"""

        params: Dict[str, Union[bytes, int]] = {
            "info_hash": self.info_hash,
            "peer_id": self.peer_id,
            "port": self.port,
            "uploaded": 0,
            "downloaded": 0,
            "left": self.total_length,
        }

        for tracker in self.trackers:
            if len(self.raw_peers) > MAX_PEERS:
                break

            try:
                data: requests.Response = requests.get(tracker, params=params)
                self.scrape_response(data.content)
                logging.debug(f"successfully connected to tracker: {tracker}")
            except Exception as e:
                logging.exception(f"Error in tracker: {tracker}")
                logging.exception(e)

        self.add_peers()

    def add_peers(self):
        for p in self.raw_peers:
            if len(self.peers) > MAX_CONNECTED_PEERS:
                break

            peer: Peer = Peer(
                p[b"peer id"],
                p[b"ip"],
                p[b"port"],
                self.info_hash,
                self.bitfield_length,
            )

            try:
                # if peer.connect() and self._do_handshake(peer):
                if peer.connect():
                    peer.send_handshake(self.peer_id)
                    # self.peers.add(peer)
                    self.peers.append(peer)
            except Exception as e:
                # self.raw_peers.remove(p)
                logging.error(e)

        logging.debug("added peers")

    def remove_peer(self, peer):
        try:
            peer.socket.close()
        except Exception as e:
            logging.exception(e)

        self.peers.remove(peer)
        logging.debug(f"Peer - {peer.ip} removed")

    def scrape_response(self, res):
        self.raw_peers += bencodepy.decode(res)[b"peers"]

    def run(self):
        while self.is_active:
            if len(self.peers) == 0:
                print("No peer")
                break

            read = [peer for peer in self.peers]
            write = [peer for peer in self.peers if peer.write_buffer != b""]
            read_list, write_list, err = select.select(read, write, [])

            for peer in write_list:
                if not peer.healthy:
                    self.remove_peer(peer)
                    continue

                try:
                    peer.send()
                except Exception as e:
                    self.remove_peer(peer)
                    logging.exception(e)
                    continue

            for peer in read_list:
                if not peer.healthy:
                    self.remove_peer(peer)
                    continue

                try:
                    peer.receive()
                except Exception as e:
                    self.remove_peer(peer)
                    logging.exception(e)
                    continue

                for msg in peer.get_messages():
                    self._process_new_message(msg, peer)

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

    def _process_new_message(self, new_message: message.Message, peer: Peer):
        if isinstance(new_message, message.Handshake) or isinstance(
            new_message, message.KeepAlive
        ):
            logging.error("Handshake or KeepALive should have already been handled")

        elif isinstance(new_message, message.Choke):
            peer.handle_choke()

        elif isinstance(new_message, message.UnChoke):
            peer.handle_unchoke()

        elif isinstance(new_message, message.Interested):
            peer.handle_interested()

        elif isinstance(new_message, message.NotInterested):
            peer.handle_not_interested()

        elif isinstance(new_message, message.Have):
            peer.handle_have(new_message)

        elif isinstance(new_message, message.Bitfield):
            peer.handle_bitfield(new_message)

        elif isinstance(new_message, message.Request):
            peer.handle_request(new_message)

        elif isinstance(new_message, message.Piece):
            peer.handle_piece(new_message)

        elif isinstance(new_message, message.Cancel):
            peer.handle_cancel()

        elif isinstance(new_message, message.Port):
            peer.handle_port_request()

        else:
            logging.error(f"Unknown message - {new_message}")

    def get_peer_having_piece(self, piece_index: int):
        ready_peers = []

        for peer in self.peers:
            if peer.is_ready and peer.is_eligible and peer.has_piece(piece_index):
                ready_peers.append(peer)

        return choice(ready_peers) if ready_peers else None

    @property
    def has_unchoked_peers(self) -> bool:
        for peer in self.peers:
            if not peer.peer_choking:
                return True
        return False


# TODO: 1. get trackers
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    file_name = "../tests/data/ubuntu-20.04.1-desktop-amd64.iso.torrent"
    #  file_name = "../tests/data/manjaro-gnome-20.1.2-201019-linux58.iso.torrent"
    #  file_name = "../tests/data/torrent-dl.torrent"
    torrent = Torrent()
    torrent.open_from_file(os.path.join(BASE_DIR, file_name))
    PeerManager(torrent)
