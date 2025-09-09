from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import yaml
from dataclasses import asdict

from config.paths import TODOS_DIR
from backend.models.to_do import ToDo
from backend.utils.logger import Logger

@Logger.attach_logger
class ToDoFileHandler:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or TODOS_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _day_path(self, date_iso: str) -> Path:
        return self.base_dir / f"{date_iso}.yaml"

    def load_day(self, date_iso: str) -> Dict[str, Any]:
        p = self._day_path(date_iso)
        if not p.exists():
            return {"date": date_iso, "todos": []}
        with open(p, "r", encoding="utf-8") as f:
            return (yaml.safe_load(f) or {"date": date_iso, "todos": []})

    def save_day(self, date_iso: str, data: Dict[str, Any]) -> None:
        p = self._day_path(date_iso)
        with open(p, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

    def list_todos(self, date_iso: str) -> List[Dict[str, Any]]:
        return self.load_day(date_iso).get("todos", [])

    def merge_vendor_todos(self, date_iso: str, vendor_todos: List[ToDo]) -> int:
        day = self.load_day(date_iso)
        existing: List[Dict[str, Any]] = day.get("todos", [])

        def canon(x): return (x or "").strip()

        def key_of(obj: Dict[str, Any]) -> tuple:
            # IMPORTANT: coalesce None → "" and strip to match ToDo.key()
            return (canon(obj.get("kind")),
                    canon(obj.get("vendor")),
                    canon(obj.get("store")))

        index = {key_of(t): i for i, t in enumerate(existing)}
        inserted = 0

        for todo in vendor_todos:
            k = todo.key()
            if k in index:
                i = index[k]
                # Update fields; preserve done/notes
                existing[i]["title"]    = todo.title
                existing[i]["due_time"] = todo.due_time
                existing[i]["due_at"]   = todo.due_at
            else:
                existing.append(asdict(todo))
                inserted += 1

        # (optional sort left as-is)
        def sort_key(t: Dict[str, Any]):
            kind_rank = 0 if t.get("kind") == "vendor_order" else 1
            tm = t.get("due_time") or "99:99"
            return (kind_rank, tm, t.get("title", ""))

        existing.sort(key=sort_key)
        day["todos"] = existing
        self.save_day(date_iso, day)
        return inserted

    def add_custom(self, date_iso: str, title: str,
                   notes: str | None = None, store: str | None = None,
                   due_time: str | None = None) -> None:
        day = self.load_day(date_iso)
        todos: List[Dict[str, Any]] = day.get("todos", [])
        todo = ToDo(kind="custom", title=title, notes=notes, store=store,
                    due_time=due_time, due_at=(f"{date_iso}T{due_time}" if due_time else None))
        todos.append(asdict(todo))
        day["todos"] = todos
        self.save_day(date_iso, day)

    def mark_done(self, date_iso: str, index_1_based: int, done: bool = True) -> None:
        day = self.load_day(date_iso)
        todos = day.get("todos", [])
        if 1 <= index_1_based <= len(todos):
            todos[index_1_based - 1]["done"] = bool(done)
            self.save_day(date_iso, day)
        else:
            raise IndexError(f"Todo #{index_1_based} out of range (1..{len(todos)})")
# endregion
