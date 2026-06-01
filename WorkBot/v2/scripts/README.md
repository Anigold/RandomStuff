# Scripts

Utility and command scripts for the WorkBot project.

## dev/

Developer environment commands.

- `start_dev.py` — Starts the local development environment.
- `reset_dev_db.py` — Resets the local development database.
- `install_package.py` — Installs a Python package and updates project dependency tracking.

## diagnostics/

Inspection and debugging scripts.

- `inspect_db.py` — Prints database state.
- `check_items.py` — Checks item data health.
- `check_reference_data.py` — Checks required reference data.
- `generate_file_tree.py` — Generates a text representation of the project file tree.

## data/

Data import, migration, seeding, and validation scripts.

### data/imports/

- `import_craftable_order_file.py`
- `import_items_from_legacy_json.py`
- `import_item_vendor_info_upload.py`
- `import_vendors_from_legacy_json.py`

### data/migrations/

- `migrate_json_to_db.py`

### data/seeds/

- `seed_dev_data.py`
- `seed_reference_data.py`

### data/validation/

- `validate_imported_items.py`

## use_cases/

Application-level business commands.

### use_cases/items/

- `show_item.py`
- `delete_item.py`

### use_cases/orders/

- `show_order.py`
- `show_orders.py`
- `delete_order.py`

### use_cases/stores/

- `add_store.py`
- `list_stores.py`

### use_cases/vendors/

- `add_vendor.py`
- `list_vendors.py`