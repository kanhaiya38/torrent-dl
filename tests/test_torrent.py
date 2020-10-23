import json
import os

import pytest

from torrent_dl.torrent import Torrent

BASE_DIR: str = os.path.dirname(__file__)


@pytest.mark.parametrize(
    "file_name, res_file",
    [
        (
            "./data/ubuntu-20.04.1-desktop-amd64.iso.torrent",
            "./data/ubuntu-20.04.1-desktop-amd64.iso.torrent.json",
        ),
        ("./data/torrent-dl.torrent", "./data/torrent-dl.torrent.json"),
    ],
)
def test_open_from_file(file_name: str, res_file: str) -> None:
    t = Torrent()
    t.open_from_file(os.path.join(BASE_DIR, file_name))
    with open(os.path.join(BASE_DIR, res_file), mode="r") as _file:
        res_data = json.load(_file)

    #### checklist ####
    # 1. name
    assert t.name == res_data["name"]

    # 2. total length of torrent
    assert t.total_length == res_data["length"]

    # 3. all files in torrent
    assert t.files == res_data["files"]

    # 4. trackers
    assert t.trackers == set(res_data["announce"])

    # 5. pieces
    assert "".join(res_data["pieces"]) == t.pieces.hex()

    # 6. piece length
    assert t.piece_length == res_data["pieceLength"]

    # 7. info hash
    assert t.info_hash.hex() == res_data["infoHash"]


if __name__ == "__main__":
    test_open_from_file(
        "./data/ubuntu-20.04.1-desktop-amd64.iso.torrent",
        "./data/ubuntu-20.04.1-desktop-amd64.iso.torrent.json",
    )
