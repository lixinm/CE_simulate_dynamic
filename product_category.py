from stakeholders.provider import Provider
from stakeholders.consumer import Consumer
from typing import Union, List, TYPE_CHECKING
if TYPE_CHECKING:
    from enablers.product import Product

class ProductCategory:
    def __init__(
        self, provider: Provider
    ):
        self._provider = provider
        self.product_list = []  # このカテゴリに属する製品のリスト
        self.candidates = []  # このカテゴリの使用する顧客の候補
    
    def add_products(self, products: Union['Product', List['Product']]) -> None:
        """
        このカテゴリに製品を追加する。
        単一の製品または製品のリストを受け取る。
        
        Args:
            products: 追加する製品または製品のリスト
        """
        from enablers.product import Product

        if isinstance(products, Product):
            # 単一の製品の場合
            self.product_list.append(products)
            products.set_product_category(self)  # 製品にもセットしておく
        else:
            # 製品リストの場合
            self.product_list.extend(products)
            for product in products:
                product.set_product_category(self)  # 各製品にもセットしておく
    
    def add_candidate(self, candidate: Consumer) -> None:
        """
        このカテゴリに引数の消費者を追加する。
        """
        self.candidates.append(candidate)
    
    def remove_all(self) -> None:
        """
        このカテゴリに属する製品と候補をすべて削除する。
        """
        self.product_list = []
        self.candidates = []
    @property
    def provider(self) -> Provider:
        """
        このカテゴリに属する製品のプロバイダーを返す。
        """
        return self._provider
