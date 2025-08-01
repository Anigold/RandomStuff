from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ContactInfo:
    name:  str
    title: str
    email: str
    phone: str


@dataclass
class ScheduleEntry:
    order_day:    str
    delivery_days: List[str]
    cutoff_time:  str


@dataclass
class OrderingInfo:
    method:          List[str] = field(default_factory=list)
    email:           str = ""
    portal_url:      str = ""
    phone_number:    str = ""
    schedule:        List[ScheduleEntry] = field(default_factory=list)
    

@dataclass
class VendorInfo:
    name:                 str
    order_format:         str = ""
    special_notes:        str = ""
    min_order_value:      float = 0
    min_order_cases:      int = 0
    internal_contacts:    List[ContactInfo] = field(default_factory=list)
    ordering:             OrderingInfo = field(default_factory=OrderingInfo)
    store_ids:            dict[str, str] = field(default_factory=dict)