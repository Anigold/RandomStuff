from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable, List

from backend.app.ports import OrderRepository, TransferRepository, DownloadPort
from backend.domain.models import Transfer
from backend.domain.transformers.order_to_transfer import order_to_transfer
from backend.infra.logger import Logger
from backend.infra.config.settings import DEFAULT_TRANSFER_ORIGIN

# ========== QUERIES ==========

@Logger.attach_logger
@dataclass(frozen=True)
class CreateTransferFromOrder:
    transfer_repo: TransferRepository
    order_repo: OrderRepository
    default_origin: str = DEFAULT_TRANSFER_ORIGIN

    def __call__(self, order_id: str) -> Transfer:
        order = self.order_repo.get_by_id(order_id)
        transfer = order_to_transfer(order, default_origin=self.default_origin)
        self.transfer_repo.save(transfer)
        return transfer