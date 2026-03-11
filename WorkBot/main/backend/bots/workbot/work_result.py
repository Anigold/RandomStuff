from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict



'''
THIS IS THE LAST LAYER BETWEEN THE WORKBOT AND THE CLI/API/WHATEVER THE 
USER IS USING TO INTERACT WITH THE BOT.

ALL MESSAGING FROM WORKBOT TO THE USER WILL BE IN THIS OBJECT-TYPE.

'''
@dataclass
class WorkResult:
    success: bool
    message: str
    errors:  List[str] = field(default_factory=list)
    payload: Optional[Any] = None

    @staticmethod
    def ok(message: str, payload=None) -> "WorkResult":
        return WorkResult(success=True, message=message, payload=payload)

    @staticmethod
    def fail(message: str, errors: List[str] | None = None) -> "WorkResult":
        return WorkResult(success=False, message=message, errors=errors or [])
