from dataclasses import dataclass
from typing import Optional, Dict, Any
from backend.adapters.downloads.local_download_manager import DownloadToken


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
    message: str = ""

    # raw scraped dict: { store, vendor, date, items[] }
    data: Optional[Dict[str, Any]] = None

    # Download token from DownloadManager
    download_token: Optional[DownloadToken] = None
