from typing import Dict, List, Any, TYPE_CHECKING
from stakeholders.provider import Provider
from enum import Enum
from logger import logger
from product_factory import create_product
if TYPE_CHECKING:
    from enablers.product import Product, ProductType
    from product_category import ProductCategory
class PaasProviderType(Enum):
    STANDARD = "standard"

class PaasProvider(Provider):
    """PaaSプロバイダー基底クラス"""
    
    def __init__(self, product_type: 'ProductType', attributes: Dict[str, Any]):
        super().__init__(product_type, attributes)
        self.name = "paas_base"

    def provide_products(self, product_attributes: Dict[str, Dict[str, Any]], year: int) -> List['Product']:
        """製品の提供（サブクラスで実装）"""
        new_products = self.create_new_products(product_attributes, year)
        available_products = [
            product for product in self.products 
            if product.is_available()
        ]
        new_products.extend(available_products)
        return new_products

    def create_new_products(self, product_attributes: Dict[str, Dict[str, Any]], year: int) -> List['Product']:
        """製品の生成（サブクラスで実装）"""
        raise NotImplementedError

    def _create_base_product(self, name: str, year: int, attribute: Dict[str, Any]) -> 'Product':
        """基本的な製品インスタンスの作成（サブクラスで実装）"""
        raise NotImplementedError

    def calculate_price(self, product: 'Product', plan_of_use_period: int) -> float:
        """サブスクリプション価格の計算（サブクラスで実装）"""
        raise NotImplementedError

class StandardPaasProvider(PaasProvider):
    """標準的なパッケージ"""

    def __init__(self, attributes: Dict[str, Any], product_type: 'ProductType'):
        super().__init__(product_type, attributes)
        self.name = "pas"
        self.procurement_cost = attributes["procurement_cost"]
        self.repair_cost = attributes["repair_cost"]
        self.products: List[Product] = []
        self._price = attributes["base_price"]
        self.production_volume = attributes["production_volume"]

    def provide_products(self, product_attributes: Dict[str, Dict[str, Any]], year: int) -> List['Product']:
        """製品の提供"""
        logger.debug(f"---PaaS provider providing products for year {year}---")
        
        # 新製品の作成
        new_products = self.create_products(product_attributes, year)
        for product in new_products:
            logger.debug(f"New product: {product.name}")
        
        # 利用可能な製品のみをフィルタリング
        available_products = [
            product for product in self.products 
            if product.is_available()
        ]
        for product in available_products:
            logger.debug(f"Used product: {product.name}")
        
        # 新製品と利用可能な製品を結合
        new_products.extend(available_products)
        return new_products

    def create_products(self, product_attributes: Dict[str, Dict[str, Any]], year: int, production_volume: int) -> List['Product']:
        """製品の生成"""
        logger.debug(f"---PaaS provider creating products for year {year}---")
        new_products = []  # 製品リストの初期化
        
        for name, attribute in product_attributes.items():
            # 指定された数の製品を生産
            for i in range(production_volume):
                product = self._create_base_product(
                    name=f"{name}_{year}_{i}_{self.name}",
                    year=year,
                    attribute=attribute
                )
                self._register_as_provider(product, year)
                new_products.append(product)
        
        return new_products

    def _create_base_product(self, name: str, year: int, attribute: Dict[str, Any]) -> 'Product':
        """基本的な製品インスタンスの作成"""
        product_attributes = {
            "name": name,
            "price": attribute["price"],
            "lifetime": attribute["lifetime"],
            "weibull_alpha": attribute["weibull_alpha"],
            "weibull_beta": attribute["weibull_beta"]
        }
        return create_product(self.product_type, product_attributes)
    
    def calculate_price(self, product_category: 'ProductCategory', plan_of_use_period: int) -> float:
        """新品の価格計算"""
        # TODO: 新品の価格計算
        return self._price
    
def create_paas_provider(paas_provider_type: PaasProviderType, attributes: Dict[str, Any], product_type: 'ProductType') -> PaasProvider:
    """PaaSプロバイダーファクトリー関数"""
    paas_provider_map = {
        PaasProviderType.STANDARD: StandardPaasProvider,
    }
    return paas_provider_map[paas_provider_type](attributes, product_type)