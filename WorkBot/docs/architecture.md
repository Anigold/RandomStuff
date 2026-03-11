# WorkBot Architecture

## Purpose

WorkBot is an operational automation system used by Ithaca Bakery to coordinate inventory, purchasing, and vendor communication workflows.

The system automates tasks that would otherwise require manual interaction with the Craftable inventory platform and manual preparation of vendor communications and operational files.

WorkBot provides programmatic control over these processes while keeping operational logic separated from infrastructure concerns such as Selenium automation, email services, and file formats.

---

# Architectural Style

WorkBot follows a **layered architecture inspired by hexagonal (ports and adapters) design**.

The architecture emphasizes separation between:

- domain models
- application workflows
- external systems
- infrastructure

Hexagonal architecture is applied **where beneficial**, rather than strictly enforced everywhere.

The goal is **operational extendability**, allowing new automation workflows to be added without deeply modifying the core system.

---

# Architectural Layers

## 1. Domain Layer

Location:
backend/domain

The domain layer defines the core operational entities and transformations.

Examples:

- Order
- Vendor
- Store
- Transfer
- Audit
- Item

Responsibilities:

- Represent business concepts
- Maintain domain invariants
- Provide domain transformations
- Remain independent of infrastructure

Domain models do not depend on:

- Selenium
- email systems
- file formats
- filesystem access

---

## 2. Application Layer

Location:
backend/app

The application layer coordinates workflows using domain models.

Key components:

### Services

Located in:
app/services

Services orchestrate operational use cases such as:

- order processing
- vendor email generation
- transfer management
- audit handling

Services coordinate domain models and infrastructure adapters.

---

### Ports

Located in:
app/ports


Ports define interfaces used by the application layer to interact with external systems.

Examples:

- download interfaces
- repository interfaces
- file handling interfaces

These allow infrastructure implementations to be swapped or mocked during testing.

---

### CLI

Located in:
app/cli

The CLI provides the primary user interface.

Responsibilities:

- parse commands
- validate input
- call WorkBot operations

The CLI intentionally contains **no business logic**.

---

## 3. Bots Layer

Location:
backend/bots

Bots encapsulate automation behavior.

### CraftableBot

Responsible for interacting with the Craftable platform using Selenium.

Capabilities include:

- downloading orders
- downloading audits
- submitting transfers
- extracting operational data

### WorkBot

WorkBot acts as the **central orchestrator of the system**.

Responsibilities:

- coordinate application services
- trigger automation bots
- provide a unified operational interface for the CLI

WorkBot represents the **single entry point between users and system services**.

---

## 4. Adapters Layer

Location:
backend/adapters

Adapters implement external integrations defined by application ports.

Examples include:

### Repositories

File-based persistence for:

- orders
- vendors
- stores
- transfers
- audits

### Email Adapters

Email services supporting:

- Gmail
- Outlook

### Download Adapters

Infrastructure for managing concurrent downloads and filesystem interactions.

---

## 5. Core Layer

Location:
backend/core

Core contains shared abstractions and reusable components.

Examples:

- serializers
- mappers
- formatters
- transformers
- normalization utilities

These utilities are used across multiple layers but do not depend on application services.

---

## 6. Infrastructure Layer

Location:
backend/infra

Infrastructure contains runtime configuration and low-level system concerns.

Examples:

- logging
- filesystem paths
- environment configuration
- store/vendor JSON configuration

---

# Persistence Model

WorkBot uses the local filesystem as its primary persistence mechanism.

| Entity | Storage |
|------|------|
| Stores | JSON configuration |
| Vendors | JSON configuration |
| Orders | Excel |
| Audits | Excel |
| Transfers | Excel |

Repositories translate between domain models and these storage formats.

---

# Dependency Direction

Dependencies should generally follow this direction:

CLI  
↓  
WorkBot  
↓  
Application Services  
↓  
Domain Models  
↓  
Ports  
↓  
Adapters  
↓  
Infrastructure  

Higher layers may depend on lower layers, but not vice versa.

---

# Typical Workflow Example

Example: generating vendor order emails.

1. User runs a CLI command.
2. CLI forwards the request to WorkBot.
3. WorkBot invokes the appropriate application service.
4. The service loads order data from repositories.
5. Domain models represent order information.
6. Email adapters generate email content.
7. Email services deliver the message.

---

# Testing Strategy

Tests are organized to mirror the system architecture.
tests/
adapters/
app/
bots/
infra/
integration/

This structure allows:

- unit testing of domain and services
- adapter testing
- full integration testing of operational workflows

---

# Extension Guidelines

When extending WorkBot:

### Add new operational workflows

Implement new application services.  
backend/app/services

---

### Add new automation

Implement new bots or bot helpers.  
backend/bots

---

### Add new external integrations

Create adapters implementing existing ports.  
backend/adapters

---

### Add new domain concepts

Create domain models and serializers.  
backend/domain

---

# Design Philosophy

WorkBot prioritizes:

- operational automation
- maintainable infrastructure integrations
- clear separation of concerns
- extensibility of workflows


---

# Future Evolution

Potential future improvements may include:

- additional automation bots
- expanded vendor integration formats
- enhanced reporting and auditing capabilities

The architecture is designed to support these expansions without major restructuring.
