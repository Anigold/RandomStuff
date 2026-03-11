from dataclasses import dataclass
from backend.adapters.downloads.local_download_manager import StagedFile
from typing import Any



@dataclass
class BotOrderResult:
    """
    Returned by CraftableBot.download_orders().
    Contains:
      - raw scraped order data (not domain Order yet)
      - the vendor/store/date
      - the token for downloaded files
      - success/failure state
      - a message for logging
    """

    store: str
    vendor: str
    date: str

    success: bool
    artifacts: list[StagedFile]

    message: str = ""
    
    data: list[dict] = None


@dataclass
class BotAuditResult:
    success: bool
    message: str
    artifacts: list[StagedFile]
    hints: dict[str, Any]  
  
