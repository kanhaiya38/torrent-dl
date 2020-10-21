import os
import pytest
import json
from torrent_dl.torrent import Torrent


_dir: str = os.path.dirname(__file__)


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
    t.open_from_file(os.path.join(_dir, file_name))
    with open(os.path.join(_dir, res_file), mode="r") as _file:
        res_data = json.load(_file)

    #  props = "name", "files", "trackers", "pieces", "piece_length", "info_hash"
    assert t.name == res_data["name"]
    t.files.sort(key=lambda x: x["path"])
    res_data["files"].sort(key=lambda x: x["path"])
    for i in range(len(t.files)):
        assert t.name + "/" + t.files[i]["path"] == res_data["files"][i]["path"]
        assert t.files[i]["length"] == res_data["files"][i]["length"]

    for i in t.trackers:
        for j in i:  # type: ignore
            assert j in res_data["announce"]

    assert "".join(res_data["pieces"]) == t.pieces.hex()
    assert t.piece_length == res_data["pieceLength"]
    assert t.info_hash.hex() == res_data["infoHash"]


if __name__ == "__main__":
    test_open_from_file(
        "./data/ubuntu-20.04.1-desktop-amd64.iso.torrent",
        "./data/ubuntu-20.04.1-desktop-amd64.iso.torrent.json",
    )
