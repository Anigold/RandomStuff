from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from decimal import Decimal

import httpx

from ..session import CliSession
from .item_models import ItemWritePayload, ItemStoreInfoWritePayload, ItemStoreInfoUpdatePayload
from .store_models import StoreResult

# ============================================================
# API results
# ============================================================

@dataclass(slots=True)
class ItemResult:
    id: str
    name: str
    category: str | None = None
    subcategory: str | None = None
    is_active: bool = True


@dataclass(slots=True)
class LoginResult:
    access_token: str
    user: dict[str, Any]


@dataclass(slots=True)
class StoreScopeResult:
    id: str
    name: str
    type: str

    @property
    def is_supervisor(self) -> bool:
        return self.type == "supervisor"

    @property
    def is_store(self) -> bool:
        return self.type == "store"

    
# ============================================================
# API exceptions
# ============================================================

class WorkBotApiError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class WorkBotConnectionError(WorkBotApiError):
    pass


class WorkBotUnauthorizedError(WorkBotApiError):
    pass


# ============================================================
# API client
# ============================================================


class WorkBotApiClient:
    def __init__(
        self,
        *,
        base_url: str,
        session: CliSession,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
        )

    # ========================================================
    # Public HTTP methods
    # ========================================================

    def get(self, path: str, *,  params: dict[str, Any] | None = None) -> Any:
        return self._request(
            "GET",
            path,
            params=params,
        )

    def post(
        self,
        path: str,
        *,
        json: Any = None,
    ) -> Any:
        return self._request(
            "POST",
            path,
            json=json,
        )

    def put(
        self,
        path: str,
        *,
        json: Any = None,
    ) -> Any:
        return self._request(
            "PUT",
            path,
            json=json,
        )

    def patch(
        self,
        path: str,
        *,
        json: Any = None,
    ) -> Any:
        return self._request(
            "PATCH",
            path,
            json=json,
        )

    def delete(
        self,
        path: str,
    ) -> Any:
        return self._request(
            "DELETE",
            path,
        )

    # ========================================================
    # Scoped HTTP methods
    # ========================================================

    def scoped_get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self.get(
            path,
            params=self._with_scope(params),
        )

    def scoped_post(
        self,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self._request(
            "POST",
            path,
            params=self._with_scope(params),
            json=json,
        )

    def scoped_put(
        self,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self._request(
            "PUT",
            path,
            params=self._with_scope(params),
            json=json,
        )

    def scoped_delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self._request(
            "DELETE",
            path,
            params=self._with_scope(params),
        )

    # ========================================================
    # General API endpoints
    # ========================================================

    def health(self) -> Any:
        return self.get("/api/health")

    def me(self) -> Any:
        return self.get("/api/me")


    # ITEMS
    def list_store_scopes(
        self,
    ) -> list[StoreScopeResult]:
        result = self.get(
            "/api/store-scopes"
        )

        if not isinstance(result, list):
            raise WorkBotApiError(
                "Invalid store scope response from WorkBot API."
            )

        scopes: list[StoreScopeResult] = []

        for entry in result:
            if not isinstance(entry, dict):
                raise WorkBotApiError(
                    "Invalid store scope entry from WorkBot API."
                )

            scope_id = entry.get("id")
            name = entry.get("name")
            scope_type = entry.get("type")

            if (
                not isinstance(scope_id, str)
                or not scope_id
                or not isinstance(name, str)
                or not name
                or not isinstance(scope_type, str)
                or not scope_type
            ):
                raise WorkBotApiError(
                    "Invalid store scope entry from WorkBot API."
                )

            scopes.append(
                StoreScopeResult(
                    id=scope_id,
                    name=name,
                    type=scope_type,
                )
            )

        return scopes

    def list_items(
        self,
        *,
        search: str | None = None,
        include_inactive: bool = False,
    ) -> list[ItemResult]:
        params: dict[str, Any] = {
            "include_inactive": include_inactive,
        }

        if search:
            params["search"] = search

        result = self.scoped_get(
            "/api/items",
            params=params,
        )

        if not isinstance(result, list):
            raise WorkBotApiError(
                "Invalid items response from WorkBot API."
            )

        items: list[ItemResult] = []

        for entry in result:
            if not isinstance(entry, dict):
                raise WorkBotApiError(
                    "Invalid item entry from WorkBot API."
                )

            item_id = entry.get("id")
            name = entry.get("name")

            if (
                not isinstance(item_id, str)
                or not item_id
                or not isinstance(name, str)
                or not name
            ):
                raise WorkBotApiError(
                    "Invalid item entry from WorkBot API."
                )

            items.append(
                ItemResult(
                    id=item_id,
                    name=name,
                    category=entry.get("category"),
                    subcategory=entry.get("subcategory"),
                    is_active=bool(
                        entry.get("is_active", True)
                    ),
                )
            )

        return items

    def get_item(
        self,
        item_id: str,
    ) -> dict[str, Any]:
        result = self.scoped_get(
            f"/api/items/{item_id}"
        )

        if not isinstance(result, dict):
            raise WorkBotApiError(
                "Invalid item detail response from WorkBot API."
            )

        return result

    def find_item_by_name(
        self,
        name: str,
        *,
        include_inactive: bool = False,
    ) -> ItemResult | None:
        items = self.list_items(
            search=name,
            include_inactive=include_inactive,
        )

        normalized_name = name.casefold()

        matches = [
            item
            for item in items
            if item.name.casefold() == normalized_name
        ]

        if not matches:
            return None

        if len(matches) > 1:
            raise WorkBotApiError(
                f'Multiple items matched the name "{name}".'
            )

        return matches[0]

    def create_item(
        self,
        payload: ItemWritePayload,
    ) -> dict[str, Any]:
        result = self.scoped_post(
            "/api/items",
            json=payload.to_dict(),
        )

        if not isinstance(result, dict):
            raise WorkBotApiError(
                "Invalid create item response from WorkBot API."
            )

        return result

    def update_item(
        self,
        item_id: str,
        payload: ItemWritePayload,
    ) -> dict[str, Any]:
        result = self.scoped_put(
            f"/api/items/{item_id}",
            json=payload.to_dict(),
        )

        if not isinstance(result, dict):
            raise WorkBotApiError(
                "Invalid update item response from WorkBot API."
            )

        return result

    def deactivate_item(
        self,
        item_id: str,
    ) -> dict[str, Any]:
        result = self.scoped_delete(
            f"/api/items/{item_id}"
        )

        if not isinstance(result, dict):
            raise WorkBotApiError(
                "Invalid deactivate item response from WorkBot API."
            )

        return result

    def add_item_store_info(
        self,
        item_id: str,
        payload: ItemStoreInfoWritePayload,
    ) -> dict[str, Any]:
        result = self.scoped_post(
            f"/api/items/{item_id}/store-info",
            json=payload.to_dict(),
        )

        if not isinstance(result, dict):
            raise WorkBotApiError(
                "Invalid item store-info response from WorkBot API."
            )

        return result

    def update_item_store_info(
        self,
        item_id: str,
        info_id: str,
        payload: ItemStoreInfoUpdatePayload,
    ) -> dict[str, Any]:
        result = self.scoped_put(
            f"/api/items/{item_id}/store-info/{info_id}",
            json=payload.to_dict(),
        )

        if not isinstance(result, dict):
            raise WorkBotApiError(
                "Invalid item store-info update response from WorkBot API."
            )

        return result

    # STORES
    def list_stores(
        self,
        *,
        search: str | None = None,
        include_inactive: bool = False,
    ) -> list[StoreResult]:
        params: dict[str, Any] = {
            "include_inactive": include_inactive,
        }

        if search:
            params["search"] = search

        result = self.scoped_get(
            "/api/stores",
            params=params,
        )

        if not isinstance(result, list):
            raise WorkBotApiError(
                "Invalid stores response from WorkBot API."
            )

        stores: list[StoreResult] = []

        for entry in result:
            if not isinstance(entry, dict):
                raise WorkBotApiError(
                    "Invalid store entry from WorkBot API."
                )

            try:
                stores.append(
                    StoreResult.from_dict(entry)
                )

            except (KeyError, TypeError) as exc:
                raise WorkBotApiError(
                    "Invalid store entry from WorkBot API."
                ) from exc

        return stores

    def find_store_by_name(
        self,
        name: str,
        *,
        include_inactive: bool = False,
    ) -> StoreResult | None:
        stores = self.list_stores(
            search=name,
            include_inactive=include_inactive,
        )

        normalized_name = name.casefold()

        matches = [
            store
            for store in stores
            if store.name.casefold()
            == normalized_name
        ]

        if not matches:
            return None

        if len(matches) > 1:
            raise WorkBotApiError(
                f'Multiple stores matched the name "{name}".'
            )

        return matches[0]

    # ========================================================
    # Authentication
    # ========================================================

    def login(
        self,
        *,
        username: str,
        password: str,
    ) -> LoginResult:
        result = self._request(
            "POST",
            "/api/auth/login",
            json={
                "username": username,
                "password": password,
            },
            authenticated=False,
            retry_on_unauthorized=False,
        )

        auth_result = self._parse_auth_response(result)

        self.session.login(
            auth_result.access_token
        )

        return auth_result

    def refresh(self) -> LoginResult:
        return self._refresh_access_token()

    def logout(self) -> Any:
        try:
            return self._request(
                "POST",
                "/api/auth/logout",
                authenticated=False,
                retry_on_unauthorized=False,
            )
        finally:
            # Dedicated HTTP client, so clearing all cookies here is fine.
            # This ensures the locally-held refresh cookie disappears even
            # if the logout request fails.
            self._client.cookies.clear()

    # ========================================================
    # Request handling
    # ========================================================

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        authenticated: bool = True,
        retry_on_unauthorized: bool = True,
    ) -> Any:
        response = self._send_request(
            method,
            path,
            params=params,
            json=json,
            authenticated=authenticated,
        )

        if (
            response.status_code == 401
            and authenticated
            and retry_on_unauthorized
            and self.session.is_authenticated
        ):
            self._refresh_access_token()

            response = self._send_request(
                method,
                path,
                params=params,
                json=json,
                authenticated=True,
            )

        if response.status_code == 401:
            raise WorkBotUnauthorizedError(
                self._error_message(response),
                status_code=response.status_code,
            )

        if response.is_error:
            raise WorkBotApiError(
                self._error_message(response),
                status_code=response.status_code,
            )

        return self._decode_response(response)

    def _send_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        authenticated: bool = True,
    ) -> httpx.Response:
        try:
            return self._client.request(
                method,
                path,
                params=params,
                json=self._json_compatible(json),
                headers=self._build_headers(
                    authenticated=authenticated,
                ),
            )

        except httpx.RequestError as exc:
            raise WorkBotConnectionError(
                f"Unable to connect to WorkBot API at {self.base_url}."
            ) from exc

    def _with_scope(
        self,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        scoped_params = dict(params or {})

        if self.session.active_scope_id is not None:
            scoped_params["scope_id"] = self.session.active_scope_id

        return scoped_params
    # ========================================================
    # Authentication helpers
    # ========================================================

    def _refresh_access_token(self) -> LoginResult:
        response = self._send_request(
            "POST",
            "/api/auth/refresh",
            authenticated=False,
        )

        if response.status_code == 401:
            self.session.logout()

            raise WorkBotUnauthorizedError(
                self._error_message(response),
                status_code=response.status_code,
            )

        if response.is_error:
            raise WorkBotApiError(
                self._error_message(response),
                status_code=response.status_code,
            )

        result = self._decode_response(response)
        auth_result = self._parse_auth_response(result)

        self.session.login(
            auth_result.access_token
        )

        return auth_result

    def _parse_auth_response(
        self,
        result: Any,
    ) -> LoginResult:
        if not isinstance(result, dict):
            raise WorkBotApiError(
                "Invalid authentication response from WorkBot API."
            )

        access_token = result.get("access_token")
        user = result.get("user")

        if not isinstance(access_token, str) or not access_token:
            raise WorkBotApiError(
                "Authentication response did not contain an access token."
            )

        if not isinstance(user, dict):
            raise WorkBotApiError(
                "Authentication response did not contain user information."
            )

        return LoginResult(
            access_token=access_token,
            user=user,
        )

    # ========================================================
    # Header / response helpers
    # ========================================================

    def _build_headers(
        self,
        *,
        authenticated: bool = True,
    ) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
        }

        if (
            authenticated
            and self.session.access_token
        ):
            headers["Authorization"] = (
                f"Bearer {self.session.access_token}"
            )

        return headers

    def _decode_response(
        self,
        response: httpx.Response,
    ) -> Any:
        if response.status_code == 204:
            return None

        if not response.content:
            return None

        content_type = response.headers.get(
            "content-type",
            "",
        )

        if "application/json" in content_type:
            return response.json()

        return response.text

    def _error_message(
        self,
        response: httpx.Response,
    ) -> str:
        detail: Any = None

        try:
            payload = response.json()

            if isinstance(payload, dict):
                detail = payload.get("detail")

        except ValueError:
            pass

        if detail is None:
            detail = response.text.strip()

        if not detail:
            detail = response.reason_phrase

        return (
            f"{response.status_code} "
            f"{response.reason_phrase} - {detail}"
        )

    def _json_compatible(
        self,
        value: Any,
    ) -> Any:
        if isinstance(value, Decimal):
            return str(value)

        if isinstance(value, dict):
            return {
                key: self._json_compatible(item)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self._json_compatible(item)
                for item in value
            ]

        if isinstance(value, tuple):
            return [
                self._json_compatible(item)
                for item in value
            ]

        return value

    # ========================================================
    # Lifecycle
    # ========================================================

    def close(self) -> None:
        self._client.close()