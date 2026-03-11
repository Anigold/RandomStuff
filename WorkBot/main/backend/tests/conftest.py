import tempfile
from pathlib import Path
import pytest

from backend.app.services.file_locator import FileLocator
from backend.app.services.services_emailer import EmailServices
from backend.app.services.services_order import OrderServices
from backend.app.services.services_vendor import VendorServices
from backend.adapters.repos.order_file_repository import OrderFileRepository
from backend.adapters.repos.vendor_file_repository import VendorFileRepository
from backend.adapters.downloads.threaded_download_adapter import ThreadedDownloadAdapter


@pytest.fixture
def temp_dirs():
    """Provide isolated temp dirs for repo IO."""
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        dirs = {
            "orders": base / "orders",
            "vendors": base / "vendors",
            "uploads": base / "uploads",
            "downloads": base / "downloads",
        }
        for d in dirs.values():
            d.mkdir(parents=True, exist_ok=True)
        yield dirs


@pytest.fixture
def order_services(temp_dirs):
    repo = OrderFileRepository(
        base_dir=temp_dirs["orders"], uploads_dir=temp_dirs["uploads"]
    )
    downloads = ThreadedDownloadAdapter(watch_dir=temp_dirs["downloads"])
    return OrderServices(repo=repo, downloads=downloads)


@pytest.fixture
def vendor_services(temp_dirs):
    repo = VendorFileRepository(base_dir=temp_dirs["vendors"])
    downloads = ThreadedDownloadAdapter(watch_dir=temp_dirs["downloads"])
    return VendorServices(repo=repo, downloads=downloads)


@pytest.fixture
def file_locator(order_services, vendor_services, temp_dirs):
    return FileLocator(
        orders_repo=order_services.repo,
        vendors_repo=vendor_services.repo,
    )


@pytest.fixture
def mock_emailer(mocker):
    """Mock Emailer that just records calls."""
    emailer = mocker.Mock()
    emailer.create_email.side_effect = lambda e: print(f"[MOCK] Created: {e.subject}")
    emailer.display_email.side_effect = lambda e: print(f"[MOCK] Displayed: {e.subject}")
    return emailer


@pytest.fixture
def email_services(mock_emailer, order_services, vendor_services, file_locator):
    return EmailServices(
        emailer=mock_emailer,
        orders=order_services,
        vendors=vendor_services,
        locator=file_locator,
    )

@pytest.fixture
def mock_order_repo(mocker):
    """Mock repository for order persistence."""
    repo = mocker.Mock()
    repo.list_by_vendor.return_value = []
    repo.list_all.return_value = []
    return repo


@pytest.fixture
def mock_download_adapter(mocker):
    """Mock for ThreadedDownloadAdapter."""
    return mocker.Mock()


@pytest.fixture
def order_services(mock_order_repo, mock_download_adapter):
    """Construct OrderServices with mocks."""
    return OrderServices(repo=mock_order_repo, downloads=mock_download_adapter)