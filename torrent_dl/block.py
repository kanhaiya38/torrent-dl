from typing import Final

BLOCK_LENGTH: Final[int] = 2 ** 14


class Status:
    FREE: Final[int] = 0
    PENDING: Final[int] = 1
    COMPLETE: Final[int] = 2


class Block:
    def __init__(
        self,
        block_size: int = BLOCK_LENGTH,
    ) -> None:
        self.status: int = Status.FREE
        self.length: int = block_size
        self.data: bytes = b""
        self.last_ping: float = 0.0
