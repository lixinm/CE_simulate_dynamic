from enum import Enum
from typing import Dict, List, Any, TYPE_CHECKING
from stakeholders.provider import Provider
from logger import logger
from product_factory import create_product
if TYPE_CHECKING:
    from enablers.product import Product, ProductType
    from product_category import ProductCategory

class ManufacturerType(Enum):
    STANDARD = "standard"

class Manufacturer(Provider):
    """メーカー基底クラス"""
    def __init__(self, product_type: 'ProductType', attributes: Dict[str, Any]):
        super().__init__(product_type, attributes)

class StandardManufacturer(Manufacturer):
    """標準的なメーカー"""

    def __init__(self, attributes: Dict[str, Any], product_type: 'ProductType'):
        super().__init__(product_type, attributes)
        self.name = "man"
        self.production_volume = attributes["production_volume"]
        self.repair_cost = attributes["repair_cost"]
        self.production_cost = attributes["production_cost"]
        self._price = attributes["base_price"]

    def create_products(self, product_attributes: Dict[str, Dict[str, Any]], year: int, production_volume: int) -> List['Product']:
        """製品の生成"""
        logger.debug(f"---Manufacturer creating products for year {year}---")

        new_products = []
        
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
    
    @property
    def manufacturing_cost(self) -> float:
        """製造コスト"""
        return self.production_cost

def create_manufacturer(manufacturer_type: ManufacturerType, attributes: Dict[str, Any], product_type: 'ProductType') -> Manufacturer:
    """メーカーファクトリー関数"""
    manufacturer_map = {
        ManufacturerType.STANDARD: StandardManufacturer,
    }
    return manufacturer_map[manufacturer_type](attributes, product_type)