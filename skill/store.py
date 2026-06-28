from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class Product:
    id: str
    name: str
    category: str
    price: float
    attributes: List[str]
    size: str
    brand: str


@dataclass
class CartItem:
    product: Product
    quantity: int
    verified: bool = False


@dataclass
class Cart:
    items: List[CartItem] = field(default_factory=list)

    @property
    def total(self) -> float:
        return sum(i.product.price * i.quantity for i in self.items)


@dataclass
class SearchFilters:
    keywords: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    max_price: Optional[float] = None
    min_price: Optional[float] = None
    attributes: List[str] = field(default_factory=list)


class Store(ABC):
    @abstractmethod
    def search(self, filters: SearchFilters) -> List[Product]: ...

    @abstractmethod
    def add_to_cart(self, product_id: str, quantity: int = 1, hebrew_name: str = None) -> CartItem: ...

    @abstractmethod
    def get_cart(self) -> Cart: ...

    @abstractmethod
    def verify_cart(self) -> Dict[str, bool]: ...
