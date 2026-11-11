from .schemas import Order, OrderItem


class OrderRepository:
    """In-memory storage. Swap for a database-backed version later."""

    def __init__(self) -> None:
        self._items: dict[int, Order] = {}
        self._next_id = 1

    def all(self) -> list[Order]:
        return list(self._items.values())

    def get(self, order_id: int) -> Order | None:
        return self._items.get(order_id)

    def add(self, items: list[OrderItem], total: float) -> Order:
        order = Order(id=self._next_id, items=items, total=total)
        self._items[order.id] = order
        self._next_id += 1
        return order
