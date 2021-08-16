from typing import List, Iterator, Tuple
import message
from piece import Piece
from torrent import Torrent
from bitstring import BitArray
from math import ceil


class PieceManager:
    def __init__(self, torrent: Torrent):
        self.total_pieces = ceil(len(torrent.pieces) / 8)
        self.bitfield: BitArray = BitArray(self.total_pieces)
        self.piece_length = torrent.piece_length
        self.last_piece_length = (
            torrent.total_length - (self.total_pieces - 1) * self.piece_length
        )
        self.pieces: List[Piece] = self._init_pieces(torrent.pieces)
        self.files = self._load_files(torrent)

    @property
    def all_pieces_completed(self) -> bool:
        for piece in self.pieces:
            if not piece.complete:
                return False
        return True

    def get_required_pieces(self) -> Iterator[int]:
        for piece in self.pieces:
            if not piece.complete:
                yield piece

    def _init_pieces(self, raw_pieces: List[bytes]) -> List[Piece]:
        pieces: List[Piece] = []

        for i in range(self.total_pieces - 1):
            pieces.append(Piece(i, self.piece_length, raw_pieces[i]))

        # last piece
        last_piece_index: int = self.total_pieces - 1
        pieces.append(
            Piece(
                last_piece_index, self.last_piece_length, raw_pieces[last_piece_index]
            )
        )

        return pieces

    def process_new_block(self, piece: Tuple[int, int, bytes]):
        piece_index: int
        block_begin: int
        block: bytes
        piece_index, block_begin, block = piece
        self.pieces[piece_index].set_block(block_begin, block)
        if self.pieces[piece_index].check_if_complete():
            # self.write_piece_on_disk(self.pieces[piece_index].raw_data)
            self.bitfield[piece_index] = True

    def _load_files(self, torrent: Torrent):
        files = []
        piece_offset = 0
        piece_size_used = 0

        for f in torrent.file_names:
            current_size_file = f["length"]
            file_offset = 0

            while current_size_file > 0:
                id_piece = int(piece_offset / self.torrent.piece_length)
                piece_size = self.pieces[id_piece].piece_size - piece_size_used

                if current_size_file - piece_size < 0:
                    file = {
                        "length": current_size_file,
                        "idPiece": id_piece,
                        "fileOffset": file_offset,
                        "pieceOffset": piece_size_used,
                        "path": f["path"],
                    }
                    piece_offset += current_size_file
                    file_offset += current_size_file
                    piece_size_used += current_size_file
                    current_size_file = 0

                else:
                    current_size_file -= piece_size
                    file = {
                        "length": piece_size,
                        "idPiece": id_piece,
                        "fileOffset": file_offset,
                        "pieceOffset": piece_size_used,
                        "path": f["path"],
                    }
                    piece_offset += piece_size
                    file_offset += piece_size
                    piece_size_used = 0

                files.append(file)
        return files