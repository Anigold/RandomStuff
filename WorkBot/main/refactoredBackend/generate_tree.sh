#!/bin/bash

# Root directory
mkdir -p workbot_refactor
cd workbot_refactor || exit 1

### === BACKEND === ###
mkdir -p backend/models
mkdir -p backend/parsers
mkdir -p backend/coordinators
mkdir -p backend/storage/file
mkdir -p backend/storage/database
mkdir -p backend/utils

touch backend/models/__init__.py
touch backend/models/item.py
touch backend/models/order.py
touch backend/models/order_item.py
touch backend/models/transfer.py
touch backend/models/vendor.py

touch backend/parsers/__init__.py
touch backend/parsers/order_parser.py
touch backend/parsers/transfer_parser.py
touch backend/parsers/item_parser.py

touch backend/coordinators/__init__.py
touch backend/coordinators/order_coordinator.py
touch backend/coordinators/vendor_coordinator.py
touch backend/coordinators/store_coordinator.py
touch backend/coordinators/transfer_coordinator.py

touch backend/storage/__init__.py
touch backend/storage/file/__init__.py
touch backend/storage/file/order_file_storage.py
touch backend/storage/file/transfer_file_storage.py
touch backend/storage/database/__init__.py
touch backend/storage/database/order_db_storage.py
touch backend/storage/database/transfer_db_storage.py

touch backend/utils/__init__.py
touch backend/utils/logger.py
touch backend/utils/helpers.py
touch backend/utils/pack_size_parser.py

### === API === ###
mkdir -p api
touch api/__init__.py
touch api/app.py
touch api/routes.py

### === CLI === ###
mkdir -p cli
touch cli/__init__.py
touch cli/main.py

### === CONFIGURATION === ###
touch config.py
touch .env
touch requirements.txt
touch README.md

### === FRONTEND (React) === ###
mkdir -p frontend/public
mkdir -p frontend/src/components
mkdir -p frontend/src/pages
mkdir -p frontend/src/hooks
mkdir -p frontend/src/styles
mkdir -p frontend/src/utils

touch frontend/public/index.html

touch frontend/src/main.jsx
touch frontend/src/App.jsx
touch frontend/src/index.css

touch frontend/src/components/Navbar.jsx
touch frontend/src/components/OrderCard.jsx
touch frontend/src/components/OrderModal.jsx
touch frontend/src/components/EditOrderItemModal.jsx
touch frontend/src/components/Toolbar.jsx

touch frontend/src/pages/OrdersPage.jsx
touch frontend/src/pages/Dashboard.jsx

touch frontend/src/hooks/useOrders.js
touch frontend/src/hooks/useVendors.js

touch frontend/src/utils/api.js
touch frontend/src/styles/theme.css

### === FINAL ECHO === ###
echo "✅ Full project structure created under $(pwd)/workbot_refactor"
