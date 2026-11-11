from core.exceptions import ConflictError, NotFoundError

from .repository import ProductRepository
from .schemas import Product, ProductCreate

_repo = ProductRepository()


def list_products() -> list[Product]:
    return _repo.all()


def get_product(product_id: int) -> Product:
    product = _repo.get(product_id)
    if product is None:
        raise NotFoundError(f"Product {product_id} not found")
    return product


def create_product(data: ProductCreate) -> Product:
    return _repo.add(data)


def delete_product(product_id: int) -> None:
    if not _repo.delete(product_id):
        raise NotFoundError(f"Product {product_id} not found")


def reserve_stock(quantities: dict[int, int]) -> list[Product]:
    """Take stock for several products at once: all succeed or none change.

    `quantities` maps product id to how many units to take. Returns the
    products as they were before the stock was taken.
    """
    products = [get_product(product_id) for product_id in quantities]
    for product in products:
        if product.stock < quantities[product.id]:
            raise ConflictError(f"Not enough stock for product {product.id}")

    for product in products:
        new_stock = product.stock - quantities[product.id]
        _repo.save(product.model_copy(update={"stock": new_stock}))
    return products
