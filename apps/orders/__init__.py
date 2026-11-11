"""Orders module: placing and viewing orders.

Public interface only; see apps/products/__init__.py for the rules.
"""

from .api import router

__all__ = ["router"]
