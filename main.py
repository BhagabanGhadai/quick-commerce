from fastapi import FastAPI

from apps.products.router import router as products_router

app = FastAPI(title="Quick Commerce API")

app.include_router(products_router)


@app.get("/health")
def health():
    return {"status": "ok"}
