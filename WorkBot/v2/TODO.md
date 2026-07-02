# Current Feature Checklist

Based on recent v2 project work, this checklist captures the active and upcoming features, cleanup tasks, and documentation items.

## API / Backend Features

### `/api/me` endpoint work

- [ ] Add `/api/me` route
- [ ] Return current authenticated user/session context
- [ ] Define response DTO for current-user data
- [ ] Add service/use-case function if needed
- [ ] Add integration tests for successful `/api/me` response
- [ ] Add tests for unauthenticated request behavior
- [ ] Add tests for invalid/expired session behavior if applicable
- [ ] Confirm route follows existing API response patterns

### API integration test cleanup

- [x] Refactor API integration tests to use shared fixtures
- [x] Confirm `client` fixture is auto-discovered through `conftest.py`
- [x] Confirm `ApiTestContext` usage works across API test modules
- [x] Run full test suite successfully
- [ ] Continue using shared fixtures for new route tests
- [ ] Add new fixture helpers as route coverage grows

### New route expansion

- [x] Add recent new API routes
- [x] Confirm tests pass after route additions
- [ ] Continue route-by-route feature expansion
- [ ] Keep routes thin: request DTO → service/use case → response DTO
- [ ] Avoid putting business logic directly into route handlers

---

## Domain / DTO / Service Layer Work

### DTO boundary consistency

- [ ] Ensure incoming request data is represented as DTOs
- [ ] Ensure outgoing API responses use response DTOs
- [ ] Keep DTOs separate from domain models
- [ ] Add DTO conversion helpers where useful
- [ ] Avoid leaking raw API dictionaries into domain logic

### Domain model refinement

- [ ] Continue clarifying which concepts belong in the domain layer
- [ ] Keep business rules close to domain models or service/use-case layer
- [ ] Avoid persistence-specific logic inside domain models
- [ ] Review existing domain models for consistency

### Service/use-case layer

- [ ] Add use-case functions for new features before exposing them through API routes
- [ ] Keep orchestration logic out of routes
- [ ] Use repositories through interfaces where possible
- [ ] Add unit tests for service behavior

---

## Repository / Persistence Work

### Repository interface consistency

- [ ] Keep repository methods focused on persistence actions
- [ ] Add new repository interface methods only when needed by use cases
- [ ] Avoid API-specific naming in repositories
- [ ] Ensure implementations match interface expectations

### Data mapping

- [ ] Confirm storage data maps cleanly into domain models
- [ ] Confirm domain models map cleanly back to stored records
- [ ] Add tests for persistence edge cases
- [ ] Review vendor/item mapping logic as item features expand

---

## Item / Vendor Information Work

### Vendor item information updates

- [ ] Use item name as the reliable identifier from Purchase Log data
- [ ] Ignore false item ID references from the Purchase Log
- [ ] Use `workbot.items.get_item_by_name` to resolve saved item info
- [ ] Let most recent purchase override older pricing
- [ ] Create separate vendor info entries when SKU differs
- [ ] Preserve existing vendor info when purchase data does not replace it
- [ ] Add tests for same item/new SKU behavior
- [ ] Add tests for same item/newer price behavior

### Purchase unit / pricing model

- [ ] Preserve current admin-facing fractional purchase units where needed
- [ ] Normalize pricing internally to a reliable per-pound/per-unit measure
- [ ] Keep display/admin layout separate from calculation logic
- [ ] Confirm Malt Barrel-style item layouts work in both old and new formats

---

## Frontend / React Work

### React setup

- [ ] Add React files under the frontend directory
- [ ] Confirm project is being developed in a Debian VM
- [ ] Install Node/npm in the Debian VM environment
- [ ] Set up React build tooling
- [ ] Decide whether React is embedded into the current app or served separately
- [ ] Add frontend development commands/scripts
- [ ] Confirm backend/frontend dev startup flow

### Frontend architecture

- [ ] Define React app folder structure
- [ ] Separate components, pages/views, API clients, and shared utilities
- [ ] Create API client layer for backend calls
- [ ] Avoid duplicating backend domain logic in frontend
- [ ] Decide how DTO response shapes map into frontend state

---

## Developer Tooling

### Requirements update tooling

- [ ] Add `tools/` directory if still desired
- [ ] Create script to update `requirements.txt`
- [ ] Decide whether requirements updates are manual, scripted, or pre-commit based
- [ ] Make tooling compatible with Debian VM development
- [ ] Document usage for future contributors

### Development server scripts

- [ ] Continue improving `scripts.dev.start_dev`
- [ ] Confirm virtual environment handling works on Debian
- [ ] Remove Windows/PowerShell-specific assumptions
- [ ] Add clear startup errors for missing dependencies like `npm`
- [ ] Confirm Ctrl+C/shutdown behavior works cleanly

---

## Testing

### Current test status

- [x] Full `python -m pytest tests` suite was green
- [x] API integration tests were refactored successfully
- [x] New shared fixtures were added successfully
- [ ] Add `/api/me` tests
- [ ] Add tests for each new route as it is introduced
- [ ] Add service-layer tests before or alongside API tests
- [ ] Keep fixtures reusable but not overly magical

---

## Documentation / Onboarding

### Feature workflow docs

- [x] Create full feature workflow diagram
- [x] Create compact feature workflow diagram
- [x] Export diagrams as downloadable PNGs
- [ ] Add diagrams to onboarding documentation
- [ ] Add checklist for adding/extending implementations
- [ ] Add DTO/domain/service/repository explanation to docs
- [ ] Add “how to add a new API route” guide

---

## Architecture Review Items

### Boundary review

- [ ] Keep API layer thin
- [ ] Keep DTOs at system boundaries
- [ ] Keep domain models independent from API/storage details
- [ ] Keep repositories focused on persistence
- [ ] Keep tests aligned with architectural layers

---

## Suggested Immediate Next Checklist

For the next development pass, focus on this order:

- [ ] Add `/api/me` route
- [ ] Add `/api/me` response DTO
- [ ] Add `/api/me` service/use-case function if needed
- [ ] Add authenticated `/api/me` integration test
- [ ] Add unauthenticated `/api/me` integration test
- [ ] Run `python -m pytest tests`
- [ ] Refactor if needed
- [ ] Commit when green

This matches where the project most recently left off: the API tests are green, fixtures are in place, and `/api/me` tests are the next feature-focused step.
