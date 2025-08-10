from __future__ import annotations
import sqlite3
from pathlib import Path
from config.paths import DATABASE_PATH

SCHEMA = """
PRAGMA foreign_keys = ON;

-- ── Core tables ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Stores (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  store_name TEXT    NOT NULL UNIQUE,
  address    BLOB    NOT NULL
);

CREATE TABLE IF NOT EXISTS Employees (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  name         TEXT    NOT NULL,
  position     TEXT    NOT NULL,
  phone_number TEXT    NOT NULL,
  email        TEXT
);

CREATE TABLE IF NOT EXISTS Positions (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS StoreEmployees (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  employee_id INTEGER NOT NULL REFERENCES Employees(id) ON DELETE RESTRICT,
  store_id    INTEGER NOT NULL REFERENCES Stores(id)    ON DELETE RESTRICT,
  position_id INTEGER NOT NULL REFERENCES Positions(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS Vendors (
  id                    INTEGER PRIMARY KEY AUTOINCREMENT,
  name                  TEXT    NOT NULL UNIQUE,
  minimum_order_cost    INTEGER NOT NULL,
  minimum_order_cases   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS Items (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  item_name TEXT    NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Units (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  units_name TEXT    NOT NULL
);

-- ── Orders & lines ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS Orders (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  store_id  INTEGER NOT NULL REFERENCES Stores(id)  ON DELETE RESTRICT,
  vendor_id INTEGER NOT NULL REFERENCES Vendors(id) ON DELETE RESTRICT,
  date      TEXT    NOT NULL,              -- YYYY-MM-DD
  placed    INTEGER NOT NULL DEFAULT 0,
  UNIQUE (store_id, vendor_id, date)
);

CREATE TABLE IF NOT EXISTS OrderItems (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id  INTEGER NOT NULL REFERENCES Items(id)  ON DELETE RESTRICT,
  order_id INTEGER NOT NULL REFERENCES Orders(id) ON DELETE CASCADE,
  quantity INTEGER NOT NULL,
  cost_per INTEGER NOT NULL  -- cents
);

-- ── Vendor catalog ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS VendorItems (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id    INTEGER NOT NULL REFERENCES Items(id)   ON DELETE RESTRICT,
  vendor_id  INTEGER NOT NULL REFERENCES Vendors(id) ON DELETE RESTRICT,
  vendor_sku TEXT    NOT NULL,
  price      INTEGER NOT NULL,      -- cents
  units_id   INTEGER,               -- nullable
  case_size  INTEGER NOT NULL,
  FOREIGN KEY (units_id) REFERENCES Units(id) ON DELETE RESTRICT
);

-- ── Store inventory ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS StoreItems (
  id       INTEGER PRIMARY KEY AUTOINCREMENT,
  on_hand  INTEGER NOT NULL,
  item_id  INTEGER NOT NULL REFERENCES Items(id)  ON DELETE RESTRICT,
  store_id INTEGER     REFERENCES Stores(id)      ON DELETE SET NULL,
  par      INTEGER NOT NULL
);

-- ── Helpful indexes ─────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_orders_date           ON Orders(date);
CREATE INDEX IF NOT EXISTS idx_orderitems_order      ON OrderItems(order_id);
CREATE INDEX IF NOT EXISTS idx_orderitems_item       ON OrderItems(item_id);
CREATE INDEX IF NOT EXISTS idx_vendoritems_vendor    ON VendorItems(vendor_id);
CREATE INDEX IF NOT EXISTS idx_vendoritems_item      ON VendorItems(item_id);
CREATE INDEX IF NOT EXISTS idx_storeitems_store_item ON StoreItems(store_id, item_id);
"""

def ensure_schema(db_path: str | Path = DATABASE_PATH) -> None:
    '''Ensure required tables/indexes exist. Safe to run every startup.'''
    p = Path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(p) as conn:
        conn.executescript(SCHEMA)
        conn.commit()
