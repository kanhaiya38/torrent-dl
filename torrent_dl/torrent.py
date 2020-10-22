import os
from hashlib import sha1
from typing import List, Dict, Any, Union
from bencodepy import Bencode

metainfo_type = Dict[str, Any]
files_type = List[Dict[str, Union[int, str]]]


class Torrent:
    def __init__(self):
        self.metainfo: metainfo_type = {}
        self.name: str = ""
        self.total_length: int = 0
        self.files: files_type = []
        self.trackers: List[str] = []
        self.pieces: bytes = b""
        self.piece_length: int = 0
        self.info_hash: bytes = b""

    def open_from_file(self, file_name: str) -> None:
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

    def parse_files(self):
        if "files" in self.metainfo["info"]:
            #  self.files = self.metainfo["info"]["files"]
            for _file in self.metainfo["info"]["files"]:
                path: str = "/".join(_file["path"])
                length: int = _file["length"]
                self.total_length += length
                self.files.append({"path": path, "length": length})
        else:
            path: str = self.metainfo["info"]["name"]
            length: int = self.metainfo["info"]["length"]
            self.total_length = length
            self.files.append({"path": path, "length": length})

    def parse_trackers(self):
        if "announce-list" in self.metainfo:
            for trackers_list in self.metainfo["announce-list"]:
                self.trackers += trackers_list
        else:
            self.trackers.append(self.metainfo["announce"])

    def __repr__(self):
        res: str = ""
        res += "name: {}\n".format(self.name)
        res += "total_length: {}\n".format(self.total_length)
        res += "files:\n"
        for i in self.files:
            res += "- path: {}\n  length: {}\n".format(i["path"], i["length"])
        res += "trackers:\n"
        for i in self.trackers:
            res += "- {}\n".format(i)
        #  res += "pieces: {}\n".format(self.pieces)
        res += "piece_length: {}\n".format(self.piece_length)
        res += "info_hash: {}\n".format(self.info_hash)
        return res


if __name__ == "__main__":
    file_name: str = ""
    _dir = os.path.dirname(__file__)
    file_name = "../tests/data/ubuntu-20.04.1-desktop-amd64.iso.torrent"
    file_name = "../tests/data/torrent-dl.torrent"
    t = Torrent()
    t.open_from_file(os.path.join(_dir, file_name))
    print(t)
