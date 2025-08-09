from pathlib import Path
import json
from typing import Union, Any
import os
from openpyxl import Workbook
from config.paths import DOWNLOADS_PATH
import tempfile
import shutil

class FileHandler:

    def __init__(self, base_dir: Union[str, Path]):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.downloads_path = Path(DOWNLOADS_PATH)

        self.extension_map = {
            'xlsx':  'xlsx',
            'xls':   'xls',
            'excel': 'xlsx',
            'csv':   'csv',
            'json':  'json',
            'text':  'txt',
            'pdf':   'pdf',
            'PDF':   'pdf'
        }
        
        self._save_strategies = {
            'excel': self._save_excel,
            'csv':   self._save_csv,
            'json':  self._save_json
        }

    def _write_data(self, format: str, data: Any, file_path: Path) -> None:
        try:
            save_func = self._save_strategies[format]
        except KeyError:
            raise ValueError(f"Unsupported format: {format}")
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        save_func(data, file_path)

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

    def remove_file(self, file_path: Union[str, Path]) -> None:
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
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            workbook.save(tmp_path)  # safe write
            tmp.close()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if file_path.exists():
                file_path.unlink()
            shutil.move(tmp_path, file_path)
        
    def _save_csv(self, csv_string: str, file_path: Path) -> None:
        with open(file_path, 'w') as f:
            f.write(csv_string)

    def _save_json(self, json_data: dict, file_path: Path) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)

    def move_file(self, src: Path, dest: Path ,overwrite: bool = False) -> None:
        if not src.exists():
            raise FileNotFoundError(f"Source file does not exist: {src}")
        
        dest.parent.mkdir(parents=True, exist_ok=True)

        if dest.exists():
            if overwrite:
                dest.unlink()
            else:
                raise FileExistsError(f"{dest} already exists.")
            
        src.rename(dest)
