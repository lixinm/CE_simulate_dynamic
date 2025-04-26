from logger import logger
from enum import Enum
from typing import Dict, List, Any, TYPE_CHECKING
from stakeholders.provider import Provider
if TYPE_CHECKING:
    from enablers.product import Product, ProductType
    from product_category import ProductCategory
class RemanufacturerType(Enum):
    STANDARD = "standard"

class Remanufacturer(Provider):
    """リマンプロバイダーの基底クラス"""
    
    def __init__(self, product_type: 'ProductType', attributes: Dict[str, Any]):
        super().__init__(product_type, attributes)
        self.name = "base"
        
    def calculate_price(self, product: 'Product', plan_of_use_period: int) -> float:
        """
        リマニュファクチャリング品の価格計算
        
        Args:
            product: 対象製品
            plan_of_use_period: 計画使用期間
            
        Returns:
            float: 計算された価格
        """
        raise NotImplementedError("Subclasses must implement calculate_price")


class StandardRemanufacturer(Remanufacturer):
    """標準的なリマンプロバイダー"""

    def __init__(self, attributes: Dict[str, Any], product_type: 'ProductType'):
        super().__init__(product_type, attributes)
        self.name = "standard"
        self._price = attributes["base_price"]
        self.remanufacturing_cost = attributes["remanufacturing_cost"]

    def calculate_price(self, product_category: 'ProductCategory', plan_of_use_period: int) -> float:
        """
        リマニュファクチャリング品の価格計算
        
        Args:
            product: 対象製品
            plan_of_use_period: 計画使用期間
            
        Returns:
            float: 計算された価格
        """
        # TODO: リマニュファクチャリング品の価格計算
        return self._price

    def add_product(self, product: 'Product') -> None:
        """製品をプロバイダーの管理下に追加"""
        if product not in self.products:
            self.products.append(product)
    
    def remove_product(self, product: 'Product') -> None:
        """製品をプロバイダーの管理から削除"""
        if product in self.products:
            self.products.remove(product)

def create_remanufacturer(remanufacturer_type: RemanufacturerType, attributes: Dict[str, Any], product_type: 'ProductType') -> Remanufacturer:
    """
    リマンプロバイダーファクトリー関数
    
    Args:
        remanufacturer_type: リマンプロバイダーの種類
        product_type: 製品の種類
    Returns:
        Remanufacturer: 生成されたリマンプロバイダーインスタンス
    """
    remanufacturer_map = {
        RemanufacturerType.STANDARD: StandardRemanufacturer,
    }
    return remanufacturer_map[remanufacturer_type](attributes, product_type)