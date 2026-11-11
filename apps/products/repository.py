from .schemas import Product, ProductCreate


class ProductRepository:
    """In-memory storage. Swap for a database-backed version later."""

    def __init__(self) -> None:
        self._items: dict[int, Product] = {}
        self._next_id = 1

    def all(self) -> list[Product]:
        return list(self._items.values())

    def get(self, product_id: int) -> Product | None:
        return self._items.get(product_id)

    def add(self, data: ProductCreate) -> Product:
        product = Product(id=self._next_id, **data.model_dump())
        self._items[product.id] = product
        self._next_id += 1
        return product

    def save(self, product: Product) -> None:
        self._items[product.id] = product

    def delete(self, product_id: int) -> bool:
        return self._items.pop(product_id, None) is not None
