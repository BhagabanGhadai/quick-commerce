"""Products module: catalog and stock.

This file is the module's public interface. Other modules and main.py may only
import what is listed here; everything else in this package is private
(enforced by import-linter, see pyproject.toml).
"""

from .api import router
from .service import reserve_stock

__all__ = ["reserve_stock", "router"]
