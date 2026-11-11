from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from apps import orders, products
from core.config import get_settings
from core.exceptions import register_exception_handlers
from core.logging_config import RequestLoggingMiddleware, setup_logging
from core.security_headers import SecurityHeadersMiddleware

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title=settings.app_name, debug=settings.debug)

# Middleware added last runs first: the logger times the whole request, and
# CORS wraps the app so error responses still get CORS headers.
app.add_middleware(GZipMiddleware, minimum_size=1000)  # skip tiny responses
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Outermost, so every response gets the headers, even CORS preflight and errors.
app.add_middleware(SecurityHeadersMiddleware)

register_exception_handlers(app)

# Each module exposes one router through its public interface.
for module in (products, orders):
    app.include_router(module.router)


@app.get("/health")
def health():
    return {"status": "ok"}
