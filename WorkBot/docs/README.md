# WorkBot

WorkBot automates inventory and purchasing workflows for Ithaca Bakery locations.  
It interacts with the Craftable inventory platform to download audits and orders, generate vendor upload files, process store orders, manage transfers between locations, and produce operational emails.

The system provides a command-line interface for running operational tasks while keeping business logic separated from infrastructure such as Selenium automation, file formats, and email services.

WorkBot is designed primarily as an internal operational automation tool and development platform for extending inventory workflows.

---

# Core Capabilities

WorkBot supports the following operational workflows:

### Order Processing
- Download store orders from Craftable
- Sort and combine orders
- View and audit order data
- Delete or archive order sets

### Vendor Communication
- Generate vendor order emails
- Generate store order emails
- Produce vendor upload files (Excel)

### Inventory & Auditing
- Download inventory audits
- Generate audit data for operational review

### Transfers
- Convert orders to transfers
- Input transfers into Craftable

### Data Management
- Maintain vendor configuration
- Maintain store configuration
- Normalize identifiers and store names

---

# System Overview

WorkBot follows a layered architecture inspired by **hexagonal (ports and adapters) principles**, though applied pragmatically rather than strictly.

The system separates:

- **Domain logic**
- **Application orchestration**
- **External integrations**
- **Infrastructure**

This separation allows operational workflows to evolve without tightly coupling business logic to Selenium automation, file formats, or email systems.

---

# High-Level Architecture
CLI
&darr;
WorkBot (Application Entry Point)
&darr;
Application Services
&darr;
Domain Models
&darr;
Ports / Interfaces
&darr;
Adapters
(Craftable Bot, Email, File System, Repositories)


---

# Repository Layout


backend/
adapters/ External integrations (email, downloads, repositories)
app/ Application layer (services, CLI, ports)
bots/ Automation agents (Craftable interaction, WorkBot orchestrator)
core/ Shared abstractions, utilities, normalization
domain/ Business models and domain logic
infra/ Infrastructure configuration and runtime utilities
errors/ Error handling framework
tests/ Unit and integration tests

---

# Key Concepts

### WorkBot

WorkBot acts as the central operational orchestrator.  
All user interactions with the system pass through WorkBot.

Responsibilities:

- Coordinate application services
- Trigger automation tasks
- Serve as the operational interface for the CLI

The CLI acts purely as a **user interface layer** that forwards commands to WorkBot.

---

### CraftableBot

CraftableBot automates interactions with the Craftable inventory platform using Selenium.

Its responsibilities include:

- Downloading store orders
- Downloading inventory audits
- Submitting transfers
- Extracting structured operational data

Craftable itself lacks native automation or export APIs, so browser automation provides the programmatic access required by WorkBot.

---

### Application Services

Application services implement operational workflows such as:

- Order processing
- Vendor communication
- File generation
- Email generation
- Transfer coordination

Services coordinate domain models and infrastructure adapters.

---

### Domain Models

The domain layer represents the core operational entities:

- Audit
- Item
- Order
- OrderItem
- Store
- Transfer
- TransferItem
- Vendor
- StoreItemInfo
- VendorItemInfo

Domain models are intentionally kept independent of infrastructure concerns.

---

# Data Storage

WorkBot uses the local filesystem as its primary persistence layer.

| Data | Format |
|-----|------|
| Stores | JSON configuration |
| Vendors | JSON configuration |
| Orders | Excel |
| Audits | Excel |
| Transfers | Excel |

Repositories handle translation between domain models and these file formats.

---

# External Systems

WorkBot integrates with several external systems:

| System | Purpose |
|------|------|
| Craftable | Inventory platform used by Ithaca Bakery |
| Gmail / Outlook | Vendor communication |
| Local filesystem | Operational data storage |
| Excel files | Vendor upload and reporting formats |

---

# Development

WorkBot is intended for **internal operational automation and extensibility**.

Primary development goals:

- Operational flexibility
- Extendable automation workflows
- Clear separation of concerns
- Maintainable infrastructure integrations

---

# Architecture Documentation

Detailed architecture documentation can be found in:
docs/architecture.md

This document explains system layers, dependency rules, and extension guidelines.

---

# License

Internal use project for operational automation.