from typing import List, Dict, Any, TYPE_CHECKING
if TYPE_CHECKING:
    from enablers.product import Product, ProductType
    from product_category import ProductCategory
class Provider:
    """プロバイダー基底クラス"""
    
    def __init__(self, product_type: 'ProductType', attributes: Dict[str, Any]):
        self.product_type = product_type
        self.name = "base"
        self.products: List['Product'] = []

    def add_product(self, product: 'Product') -> None:
        """製品をプロバイダーの管理下に追加"""
        if product not in self.products:
            self.products.append(product)
    
    def remove_product(self, product: 'Product') -> None:
        """製品をプロバイダーの管理から削除"""
        if product in self.products:
            self.products.remove(product)
        
    def repair_product(self, product: 'Product') -> None:
        """製品の修理"""
        if product.calculate_remaining_lifetime() > 0:
            product.repair()
        else:
            product.dispose()
            if product.matched:
                product.remove_consumer()
    
    def _register_as_provider(self, product: 'Product', year: int) -> None:
        """製品の提供者として登録"""
        product.add_provider(year, self)
    
    def set_price(self, price: float) -> None:
        """価格の設定"""
        self._price = price

    def calculate_price(self, product_category: 'ProductCategory', year: int) -> float:
        """価格の計算"""
        pass

    @property
    def price(self) -> float:
        """価格の取得"""
        return self._price
