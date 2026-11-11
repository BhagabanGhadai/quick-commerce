# Quick Commerce API

A FastAPI app built as a **modular monolith**: one deployable app, split into
business modules that keep their own code and talk to each other only through
small public interfaces.

## Layout

```
main.py                 # builds the app and mounts each module's router
core/                   # shared code every module may use (errors, later: db, config)
apps/
  products/
    __init__.py         # PUBLIC interface: the only thing other code may import
    api.py              # HTTP routes; no business logic
    service.py          # business logic
    repository.py       # storage (in-memory for now)
    schemas.py          # Pydantic models
  orders/               # same shape; uses products via `apps.products`
tests/                  # one folder per module
```

## Rules

These are checked by import-linter (`make imports`, and on every commit):

1. A module's files are private. Other code imports only from the module's
   `__init__.py`, e.g. `from apps import products` then
   `products.reserve_stock(...)`, never `apps.products.service`.
2. `core` never imports from `apps`.
3. No circular imports between modules (or between files inside a module).

Services raise errors from `core.exceptions` (`NotFoundError`,
`ConflictError`) instead of `HTTPException`; `main.py` turns them into HTTP
responses.

## Adding a module

1. Create `apps/<name>/` with `api.py`, `service.py`, `repository.py`,
   `schemas.py`, and an `__init__.py` that exports `router` plus anything other
   modules need.
2. Add it to the loop in `main.py`.
3. Add a "protected" contract for it in `pyproject.toml` (copy the products one).
4. Add tests under `tests/<name>/`.

## Commands

```
make setup     # install dev tools and git hooks
make start     # run the API with reload
make test      # run tests
make check     # lint, format check, dead code, module boundaries
```
