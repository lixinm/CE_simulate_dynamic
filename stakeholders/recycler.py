from logger import logger
from enum import Enum
from typing import Dict, List, Any
from enablers.product import Product, ProductType
from stakeholders.provider import Provider
from product_category import ProductCategory
class RecyclerType(Enum):
    STANDARD = "standard"

class Recycler(Provider):
    """リサイクルプロバイダーの基底クラス"""
    
    def __init__(self, product_type: ProductType, attributes: Dict[str, Any]):
        super().__init__(product_type, attributes)
    
    def calculate_price(self, product: Product, plan_of_use_period: int) -> float:
        """リサイクル品の価格計算（サブクラスで実装）"""
        raise NotImplementedError


class StandardRecycler(Recycler):
    """標準的なリサイクルプロバイダー"""

    def __init__(self, attributes: Dict[str, Any], product_type: ProductType):
        super().__init__(product_type, attributes)
        self.name = "rec"
        self._price = attributes["base_price"]
    
    def calculate_price(self, product_category: 'ProductCategory', plan_of_use_period: int) -> float:
        """リサイクル品の価格計算"""
        # TODO: リサイクル品の価格計算
        return self._price

def create_recycler(recycler_type: RecyclerType, attributes: Dict[str, Any], product_type: ProductType) -> Recycler:
    """
    リサイクルプロバイダーファクトリー関数
    
    Args:
        recycler_type: リサイクルプロバイダーの種類
        product_type: 製品の種類
    Returns:
        Recycler: 生成されたリサイクルプロバイダーインスタンス
    """
    recycler_map = {
        RecyclerType.STANDARD: StandardRecycler,
    }
    return recycler_map[recycler_type](attributes, product_type)