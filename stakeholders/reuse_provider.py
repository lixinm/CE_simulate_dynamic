from typing import Dict, List, Any
from enum import Enum
from stakeholders.provider import Provider
import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from enablers.product import Product, ProductType
    from product_category import ProductCategory
logger = logging.getLogger(__name__)

class ReuseProviderType(Enum):
    STANDARD = "standard"

class ReuseProvider(Provider):
    """リユースプロバイダー基底クラス"""
    
    def __init__(self, attributes: Dict[str, Any], product_type: 'ProductType'):
        super().__init__(product_type, attributes)

    def provide_products(self, product_attributes: Dict[str, Dict[str, Any]], year: int) -> List['Product']:
        """製品の提供"""        
        available_products = [
            product for product in self.products 
            if product.is_available()
        ]
        logger.debug(f"---Reuse provider providing products for year {year}---")
        for product in available_products:
            logger.debug(f"Available product: {product.name}")
        return available_products

    def calculate_price(self, product_category: 'ProductCategory', plan_of_use_period: int) -> float:
        """リユース品の価格計算（サブクラスで実装）"""
        raise NotImplementedError


class StandardReuseProvider(ReuseProvider):
    """標準的なリユースプロバイダー"""
    
    def __init__(self, attributes: Dict[str, Any], product_type: 'ProductType'):
        super().__init__(product_type, attributes)
        self.name = "reu"
        self._reuse_cost = attributes["reuse_cost"]
        self.repair_cost = attributes["repair_cost"]
        self._price = attributes["base_price"]

    def calculate_price(self, product_category: 'ProductCategory', plan_of_use_period: int) -> float:
        """リユース品の価格計算"""
        # TODO: リユース品の価格計算
        return self._price
    
    @property
    def reuse_cost(self) -> float:
        """リユースコスト"""
        return self._reuse_cost

def create_reuse_provider(reuse_provider_type: ReuseProviderType, attributes: Dict[str, Any], product_type: 'ProductType') -> ReuseProvider:
    """リユースプロバイダーファクトリー関数"""
    reuse_provider_map = {
        ReuseProviderType.STANDARD: StandardReuseProvider,
    }
    return reuse_provider_map[reuse_provider_type](attributes, product_type)