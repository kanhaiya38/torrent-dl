class Piece:
    def __init__(self, piece_size: int, piece_hash: bytes):
        self.piece_size: int = piece_size
        self.piece_hash: bytes = piece_hash
        self.raw_data: bytes = b""
        self.is_complete: bool = False
