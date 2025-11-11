from __future__ import annotations
from dataclasses import dataclass

from backend.app.ports import (
    TransferRepository, 
    DownloadPort
)

from backend.app.application.transfers import *


@dataclass
class TransferServices:

    repo:                 TransferRepository
    order_repo:           OrderRepository
    default_origin_store: str

    def __post_init__(self) -> None:
        
        self.list_transfers = ListTransfers(self.repo)
        self.save_transfer  = SaveTransfer(self.repo)
        
        self.convert_order_to_transfer = CreateTransferFromOrder(
            self.repo,
            self.order_repo,
            self.default_origin_store
        )
        