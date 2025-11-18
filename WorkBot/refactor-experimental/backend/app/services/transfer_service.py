from __future__ import annotations
from dataclasses import dataclass

from backend.app.ports import (
    TransferRepository, 
    DownloadPort
)


from dataclasses import dataclass
from typing import Optional, Callable, List

from backend.app.ports import OrderRepository, TransferRepository, DownloadPort
from backend.domain.models import Transfer, Order
from backend.domain.transformers.order_to_transfer import order_to_transfer
from backend.infra.logger import Logger
from backend.infra.config.settings import DEFAULT_TRANSFER_ORIGIN

# ========== QUERIES ==========

@Logger.attach_logger
@dataclass(frozen=True)
class ListTransfers:

    repo: TransferRepository

    def __call__(self) -> List[Transfer]:
        self.logger.info('Listing all transfers.')
        return self.repo.list_all()


@Logger.attach_logger
@dataclass(frozen=True)
class CreateTransferFromOrder:

    transfer_repo: TransferRepository
    order_repo: OrderRepository
    default_origin: str = DEFAULT_TRANSFER_ORIGIN

    def __call__(self, order: Order) -> Transfer:
        order = self.order_repo.get(order.store, order.vendor, order.date)
        transfer = order_to_transfer(order, default_origin=self.default_origin)
        self.transfer_repo.save(transfer)
        return transfer
    
@Logger.attach_logger
@dataclass(frozen=True)
class SaveTransfer:

    repo: TransferRepository

    def __call__(self, transfer: Transfer) -> Transfer:
        return self.repo.save(transfer)
    

@Logger.attach_logger
@dataclass(frozen=True)
class ArchiveTransfer:

    repo: TransferRepository

    def __call__(self, transfer: Transfer) -> None:
        self.logger.info(f'Archiving transfer: {transfer}')
        self.repo.archive_transfer(transfer)

@dataclass
class TransferServices:

    repo:                 TransferRepository
    order_repo:           OrderRepository
    default_origin_store: str

    def __post_init__(self) -> None:
        
        self.list_transfers = ListTransfers(self.repo)
        self.save_transfer  = SaveTransfer(self.repo)
        self.archive_transfer = ArchiveTransfer(self.repo)
        
        self.convert_order_to_transfer = CreateTransferFromOrder(
            self.repo,
            self.order_repo,
            self.default_origin_store
        )
        