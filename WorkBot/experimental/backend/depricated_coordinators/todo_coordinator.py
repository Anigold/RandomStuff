from __future__ import annotations
from typing import List, Optional

from backend.utils.logger import Logger
from backend.utils.days import weekday_name_of
from backend.storage.file.todo_file_handler import ToDoFileHandler
from backend.storage.file.vendor_file_handler import VendorFileHandler
from backend.models.to_do import ToDo

@Logger.attach_logger
class ToDoCoordinator:
    def __init__(self,
                 todo_files: ToDoFileHandler | None = None,
                 vendor_files: VendorFileHandler | None = None,
                 per_store: bool = False) -> None:
        self.todo_files   = todo_files or ToDoFileHandler()
        self.vendor_files = vendor_files or VendorFileHandler()
        self.per_store    = per_store

    def ensure_vendor_todos_for_date(self, date_iso: str) -> int:
        weekday_name = weekday_name_of(date_iso)
        vendors = self.vendor_files.vendors_with_order_day(weekday_name)
        self.logger.info(f"Generating vendor To-Dos for {date_iso} ({weekday_name}); {len(vendors)} vendor(s) match.")
        todos: List[ToDo] = []

        for v in vendors:
            vname = v["name"]
            cutoff = v.get("cutoff_time")
            due_at = f"{date_iso}T{cutoff}" if cutoff else None

            if self.per_store and v.get("stores"):
                for store in (v["stores"] or []):
                    todos.append(ToDo(kind="vendor_order",
                                      title=f"{vname} order ({store})",
                                      vendor=vname, store=store,
                                      due_time=cutoff, due_at=due_at))
            else:
                todos.append(ToDo(kind="vendor_order",
                                  title=f"{vname} order",
                                  vendor=vname,
                                  due_time=cutoff, due_at=due_at))

        return self.todo_files.merge_vendor_todos(date_iso, todos)

    def list_for_date(self, date_iso: str, autogenerate: bool = True) -> List[dict]:
        items = self.todo_files.list_todos(date_iso)
        if autogenerate:
            if self.ensure_vendor_todos_for_date(date_iso):
                items = self.todo_files.list_todos(date_iso)
        return items

    def add_custom(self, date_iso: str, title: str,
                   notes: Optional[str] = None, store: Optional[str] = None,
                   due_time: Optional[str] = None) -> None:
        self.todo_files.add_custom(date_iso, title, notes, store, due_time)

    def set_done(self, date_iso: str, index_1_based: int, done: bool = True) -> None:
        self.todo_files.mark_done(date_iso, index_1_based, done)
