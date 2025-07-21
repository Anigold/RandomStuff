from pathlib import Path
import json
from typing import Union, Any
import os
from openpyxl import Workbook

class FileHandler:
    def __init__(self, base_dir: Union[str, Path]):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.extension_map = {
            'excel': 'xlsx',
            'csv': 'csv',
            'json': 'json',
            'text': 'txt'
        }
        self.save_strategies = {
            'excel': self._save_excel,
            'csv': self._save_csv
        }

    def read_json(self, file_path: Union[str, Path]) -> Any:
        path = self._resolve_path(file_path)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def write_json(self, file_path: Union[str, Path], data: Any, indent: int = 4) -> None:
        path = self._resolve_path(file_path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent)

    def file_exists(self, file_path: Union[str, Path]) -> bool:
        return self._resolve_path(file_path).exists()

    def delete_file(self, file_path: Union[str, Path]) -> None:
        path = self._resolve_path(file_path)
        if path.exists():
            path.unlink()

    def list_files(self, suffix: str = None) -> list[Path]:
        if suffix:
            return list(self.base_dir.glob(f'*{suffix}'))
        return list(self.base_dir.iterdir())

    def _resolve_path(self, path: Union[str, Path]) -> Path:
        p = Path(path)
        return p if p.is_absolute() else self.base_dir / p

    def _save_excel(self, workbook: Workbook, file_path: Path) -> None:
        return workbook.save(file_path)
    
    def _save_csv(self, csv_string: str, file_path: Path) -> None:
        with open(file_path, 'w') as f:
            f.write(csv_string)