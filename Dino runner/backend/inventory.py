from dataclasses import dataclass


@dataclass
class InventoryItem:
    name: str
    quantity: int = 1
    max_stack: int = 99

    def add(self, amount: int = 1) -> int:
        if amount < 0:
            raise ValueError("amount must not be negative")

        added = min(amount, self.max_stack - self.quantity)
        self.quantity += added
        return added

    def remove(self, amount: int = 1) -> int:
        if amount < 0:
            raise ValueError("amount must not be negative")

        removed = min(amount, self.quantity)
        self.quantity -= removed
        return removed


class Inventory:
    def __init__(self, max_slots: int = 12):
        self.max_slots = max_slots
        self._items: dict[str, InventoryItem] = {}

    def add(self, name: str, amount: int = 1, max_stack: int = 99) -> bool:
        if not name:
            raise ValueError("item name must not be empty")
        if amount <= 0:
            raise ValueError("amount must be greater than zero")

        item = self._items.get(name)
        if item is None:
            if len(self._items) >= self.max_slots:
                return False
            item = InventoryItem(name=name, quantity=0, max_stack=max_stack)
            self._items[name] = item

        added = item.add(amount)
        if added == 0 and item.quantity == 0:
            del self._items[name]
        return added == amount

    def remove(self, name: str, amount: int = 1) -> bool:
        if amount <= 0:
            raise ValueError("amount must be greater than zero")

        item = self._items.get(name)
        if item is None or item.quantity < amount:
            return False

        item.remove(amount)
        if item.quantity == 0:
            del self._items[name]
        return True

    def has(self, name: str, amount: int = 1) -> bool:
        return self.count(name) >= amount

    def count(self, name: str) -> int:
        item = self._items.get(name)
        return item.quantity if item is not None else 0

    def get_items(self) -> list[InventoryItem]:
        return list(self._items.values())

    def clear(self) -> None:
        self._items.clear()
