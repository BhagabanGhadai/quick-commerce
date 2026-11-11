from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps import orders, products
from core.compression import CompressionMiddleware
from core.config import get_settings
from core.exceptions import register_exception_handlers
from core.hpp import HPPMiddleware
from core.logging_config import RequestLoggingMiddleware, setup_logging
from core.security_headers import SecurityHeadersMiddleware
from core.timeout import TimeoutMiddleware

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title=settings.app_name, debug=settings.debug)

# Middleware added last runs first (outermost). Read bottom-up for request order.
app.add_middleware(HPPMiddleware)  # pass allow_lists=[...] for real list params
app.add_middleware(TimeoutMiddleware, seconds=settings.request_timeout_seconds)
# Never compress routes that return tokens (see core/compression.py).
app.add_middleware(CompressionMiddleware, excluded_paths=["/auth"])
app.add_middleware(RequestLoggingMiddleware)  # also logs timeouts as 504
# CORS wraps the app so error responses still get CORS headers.
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
