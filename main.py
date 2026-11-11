from fastapi import FastAPI

from apps import orders, products
from core.config import get_settings
from core.exceptions import register_exception_handlers

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug)

register_exception_handlers(app)

# Each module exposes one router through its public interface.
for module in (products, orders):
    app.include_router(module.router)


@app.get("/health")
def health():
    return {"status": "ok"}
