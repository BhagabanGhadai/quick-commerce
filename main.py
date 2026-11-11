from fastapi import FastAPI

from apps import orders, products
from core.exceptions import register_exception_handlers

app = FastAPI(title="Quick Commerce API")

register_exception_handlers(app)

# Each module exposes one router through its public interface.
for module in (products, orders):
    app.include_router(module.router)


@app.get("/health")
def health():
    return {"status": "ok"}
