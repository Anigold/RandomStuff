from typing import Literal

from pydantic import BaseModel


class StoreScopeResponse(BaseModel):
    id: str
    name: str
    type: Literal["store", "supervisor"]