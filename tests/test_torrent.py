import os
import pytest
import json
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

    #### checklist
    # 1. name
    assert t.name == res_data["name"]

    # 2. total length of torrent
    assert t.total_length == res_data["length"]

    # 3. all files in torrent
    # sort all files by their pathname so as to check both dictionaty values
    t.files.sort(key=lambda x: x["path"])
    res_data["files"].sort(key=lambda x: x["path"])
    for i in range(len(t.files)):
        curr_file = t.files[i]
        curr_res_file = res_data["files"][i]
        assert "{}/{}".format(t.name, curr_file["path"]) == curr_res_file["path"]
        assert curr_file["length"] == curr_res_file["length"]

    # 4. trackers
    for tracker in t.trackers:
        assert tracker in res_data["announce"]

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
