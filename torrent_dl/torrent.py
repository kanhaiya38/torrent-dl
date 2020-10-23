import os
from hashlib import sha1
from typing import Any, Dict, List, Set, Union

from bencodepy import Bencode

MetainfoType = Dict[str, Any]
FilesType = List[Dict[str, Union[int, str]]]


class Torrent:
    def __init__(self):
        self.metainfo: MetainfoType = {}
        self.name: str = ""
        self.total_length: int = 0
        self.files: FilesType = []
        self.trackers: Set[str] = set()
        self.pieces: bytes = b""
        self.piece_length: int = 0
        self.info_hash: bytes = b""

    def open_from_file(self, file_name: str) -> None:
        """open torrent from a file"""
        bc = Bencode(encoding="utf-8", encoding_fallback="value")
        try:
            with open(file_name, mode="rb") as _file:
                self.metainfo = bc.decode(_file.read())
        except Exception as e:
            print(e)

        metainfo = self.metainfo

        raw_info_hash = bc.encode(metainfo["info"])
        self.info_hash = sha1(raw_info_hash).digest()
        self.name = metainfo["info"]["name"]
        self.piece_length = metainfo["info"]["piece length"]
        self.pieces = metainfo["info"]["pieces"]
        self.parse_files()
        self.parse_trackers()

    def parse_files(self) -> None:
        """parse all file paths and length from the metainfo"""
        path: str = ""
        length: int = 0
        if "files" in self.metainfo["info"]:
            for _file in self.metainfo["info"]["files"]:
                path = "/".join(_file["path"])
                length = _file["length"]
                self.total_length += length
                self.files.append({"path": path, "length": length})
        else:
            path = self.metainfo["info"]["name"]
            length = self.metainfo["info"]["length"]
            self.total_length = length
            self.files.append({"path": path, "length": length})

    def parse_trackers(self) -> None:
        """parse list of all the trackers from metainfo"""
        if "announce-list" in self.metainfo:
            for trackers_list in self.metainfo["announce-list"]:
                self.trackers.update(trackers_list)
        else:
            self.trackers.add(self.metainfo["announce"])

    def __repr__(self) -> str:
        res: str = ""
        res += f"name: {self.name}\n"
        res += f"total_length: {self.total_length}\n"
        res += "files:\n"
        for f in self.files:
            res += f"- path: {f['path']}\n  length: {f['length']}\n"
        res += "trackers:\n"
        for t in self.trackers:
            res += f"- {t}\n"
        #  res += "pieces: {}\n".format(self.pieces)
        res += f"piece_length: {self.piece_length}\n"
        res += f"info_hash: {self.info_hash.hex()}\n"
        return res


if __name__ == "__main__":
    file_name: str = ""
    _dir = os.path.dirname(__file__)
    file_name = "../tests/data/ubuntu-20.04.1-desktop-amd64.iso.torrent"
    file_name = "../tests/data/torrent-dl.torrent"
    t = Torrent()
    t.open_from_file(os.path.join(_dir, file_name))
    print(t)
