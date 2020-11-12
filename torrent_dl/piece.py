from hashlib import sha1
from time import time
from typing import List, Final, Tuple, Union
import logging
from block import Block
from block import BLOCK_LENGTH
from block import Status

BLOCK_REQUEST_TIMEOUT: Final[int] = 5


class Piece:
    def __init__(self, piece_index: int, piece_size: int, piece_hash: bytes):
        self.index: int = piece_index
        self.size: int = piece_size
        self.hash: bytes = piece_hash
        self.blocks: List[Block] = self._init_blocks()
        self.raw_data: bytes = b""
        self.complete: bool = False

    def _init_blocks(self) -> List[Block]:
        blocks: List[Block] = []
        normal_block, last_block = divmod(self.size, BLOCK_LENGTH)
        for i in range(normal_block):
            blocks.append(Block())
        # handling last piece
        if last_block:
            blocks.append(Block(last_block))
        return blocks

    def update_block_status(self) -> None:
        for i, block in enumerate(self.blocks):
            if (
                block.status == Status.PENDING
                and (time() - block.last_ping) > BLOCK_REQUEST_TIMEOUT
            ):
                self.blocks[i].status = Block()

    def get_required_block(self) -> Union[Tuple[int, int], None]:
        if self.complete:
            return None

        for block_index, block in enumerate(self.blocks):
            if block.status == Status.FREE:
                block.status = Status.PENDING
                block.last_ping = time()
                return (block_index * BLOCK_LENGTH, block.length)

        return None

    def check_if_complete(self) -> bool:
        if self.are_all_blocks_complete:
            self.raw_data = self.merge_all_blocks()
            if self.validate_piece():
                self.complete = True
                return True
        return False

    def merge_all_blocks(self) -> bytes:
        data: bytes = b""

        for block in self.blocks:
            data += block.data

        return data

    @property
    def are_all_blocks_complete(self) -> bool:
        for block in self.blocks:
            if block.status == Status.COMPLETE:
                return True
        return False

    def validate_piece(self) -> bool:
        hash: bytes = sha1(self.raw_data).digest()

        if hash == self.hash:
            return True

        raise (Exception("Invalid piece"))
        logging.warning("Invalid piece")
        logging.debug(f"{hash} : {self.hash}")
        return False

    def set_block(self, block_begin: int, block: bytes) -> None:
        block_index: int = block_begin // BLOCK_LENGTH
        if not self.complete and not self.blocks[block_index].status == Status.COMPLETE:
            self.blocks[block_index].status = Status.COMPLETE
            self.blocks[block_index].data = block

    def write_on_disk(self) -> None:
        pass
