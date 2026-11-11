from collections import Counter

from apps import products
from core.exceptions import NotFoundError

from .repository import OrderRepository
from .schemas import Order, OrderCreate, OrderItem

_repo = OrderRepository()


def list_orders() -> list[Order]:
    return _repo.all()


def get_order(order_id: int) -> Order:
    order = _repo.get(order_id)
    if order is None:
        raise NotFoundError(f"Order {order_id} not found")
    return order


def place_order(data: OrderCreate) -> Order:
    # The same product may appear on several lines; reserve the combined amount.
    quantities: Counter[int] = Counter()
    for line in data.items:
        quantities[line.product_id] += line.quantity

    reserved = products.reserve_stock(dict(quantities))

    items = [
        OrderItem(
            product_id=product.id,
            name=product.name,
            unit_price=product.price,
            quantity=quantities[product.id],
        )
        for product in reserved
    ]
    total = round(sum(item.unit_price * item.quantity for item in items), 2)
    return _repo.add(items, total)
