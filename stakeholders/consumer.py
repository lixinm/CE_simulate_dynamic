from enum import Enum
from typing import Dict, Type, List, Any
import numpy as np
from preference import Preference
import logging
from stakeholders.provider import Provider
from stakeholders.paas_provider import PaasProvider
from stakeholders.reuse_provider import ReuseProvider
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from enablers.product import Product, ProductType
    from stakeholders.recycler import Recycler
    from product_category import ProductCategory
    from stakeholders.manufacturer import Manufacturer

logger = logging.getLogger(__name__)

class ConsumerType(Enum):
    STANDARD = "standard"

class Consumer:
    """消費者基底クラス"""
    def __init__(self, name: str, attributes: Dict[str, Any]):
        self.name = name
        self.pref_dict = attributes["pref_dict"]
        self.churn_rate = attributes["churn_rate"]
        self.reuse_probability = attributes["reuse_probability"]
        self.num_of_products = int(np.random.normal(
            attributes["num_of_products_mean"],
            attributes["num_of_products_sd"]
        ))
        self.matched_product = None
        self.matched_price = None
        self.use_period = 0
        self._plan_of_use_period = 0
        self.preference = None

    def set_use_period(self, attribute: Dict[str, Any]) -> None:
        """使用期間の設定（ガンマ分布に従う）"""
        # ガンマ分布のパラメータ
        shape = attribute["plan_of_use_shape"]  # 形状パラメータ（α）
        scale = attribute["plan_of_use_scale"]  # 尺度パラメータ（β）
        
        # ガンマ分布から月単位の使用期間をサンプリング
        months = np.random.gamma(shape, scale)
        
        # 月を年に換算（四捨五入）し、最小値を1年に設定
        self._plan_of_use_period = max(1, round(months / 12))
        
        logger.debug(f"Consumer {self.name} planned use period: {months:.1f} months = {self._plan_of_use_period} years")

    def set_preferences(self) -> None:
        """選好の設定"""
        part_worth_values = self._calculate_part_worth_values()
        self.preference = Preference(part_worth_values, self)

    def _calculate_part_worth_values(self) -> Dict[str, float]:
        """部分効用値の計算"""
        return {
            'ownership': np.random.normal(
                self.pref_dict["ownership_part_worth_mean"],
                self.pref_dict["ownership_part_worth_sd"]
            ),
            'subscription': np.random.normal(
                self.pref_dict["subscription_part_worth_mean"],
                self.pref_dict["subscription_part_worth_sd"]
            ),
            'reuse': np.random.normal(
                self.pref_dict["reuse_part_worth_mean"],
                self.pref_dict["reuse_part_worth_sd"]
            ),
            'remanufacture': np.random.normal(
                self.pref_dict["remanufacture_part_worth_mean"],
                self.pref_dict["remanufacture_part_worth_sd"]
            ),
            'price': np.random.normal(
                self.pref_dict["price_part_worth_mean"],
                self.pref_dict["price_part_worth_sd"]
            ),
            'spec': np.random.normal(
                self.pref_dict["spec_part_worth_mean"],
                self.pref_dict["spec_part_worth_sd"]
            )
        }

    def add_matched_product_category(self, product_category: 'ProductCategory', price: float) -> None:
        """
        マッチングした製品カテゴリと価格を記録
        
        Args:
            product: マッチングした製品
            price: 製品の価格
        """
        self.matched_product_category = product_category
        self.matched_price = price
    
    def set_possession(self, product: 'Product') -> None:
        """製品の所有情報をセット"""
        self.matched_product = product
        
    def update_use_period(self) -> None:
        """使用年数を更新"""
        if self.matched_product is None:
            return
            
        self.use_period += 1
        logger.debug(f"Consumer {self.name} uses product {self.matched_product.name} for {self.use_period}/{self._plan_of_use_period} years")
        
        # 計画使用期間に達した場合、または確率的にチャーンする場合
        if (self.use_period >= self._plan_of_use_period or 
            np.random.random() < self.churn_rate):
            self.decide_EoL()
            logger.debug(f"Consumer {self.name} released product {self.matched_product.name}")
            self.release_product()

    def decide_EoL(self) -> None:
        """製品の使用終了後の返却先を決定する"""
        from stakeholders.manufacturer import Manufacturer
        from stakeholders.paas_provider import PaasProvider
        from stakeholders.reuse_provider import ReuseProvider
        from stakeholders.recycler import Recycler

        if self.matched_product is None:
            return
            
        provider = self.matched_product.provider
            
        if isinstance(provider, Manufacturer):
            if np.random.random() < self.reuse_probability:
                self.matched_product.set_next_provider("reuse_provider")
            else:
                self.matched_product.set_next_provider("recycler")
                self.matched_product.dispose()
                
        elif isinstance(provider, PaasProvider):
            # PaaSプロバイダーの製品は再度PaaSとして提供
            self.matched_product.set_next_provider("paas_provider")
            
        elif isinstance(provider, ReuseProvider):
            # リユース品は使用後にリサイクラーへ
            self.matched_product.set_next_provider("recycler")

    def release_product(self) -> None:
        """製品の解放"""
        if self.matched_product:
            self.matched_product.release()
            self.matched_product = None

    def calculate_utility(self, product_category: 'ProductCategory', total_price: float) -> float:
        """
        製品に対する効用値を計算
        
        Args:
            product: 対象製品
            total_price: 使用期間を考慮した総価格
            
        Returns:
            float: 効用値
        """
        return self.preference.calculate_utility(product_category, total_price)
    
    @property
    def plan_of_use_period(self) -> int:
        """計画使用期間"""
        return self._plan_of_use_period

class StandardConsumer(Consumer):
    """標準的な消費者"""
    def __init__(self, name: str, attributes: Dict[str, Any]):
        super().__init__(name, attributes)
        self.set_use_period(attributes)
        self.set_preferences()


def create_consumer(consumer_type: ConsumerType, name: str, attributes: Dict[str, Any]) -> Consumer:
    """消費者クラスのファクトリー関数"""
    consumer_map = {
        ConsumerType.STANDARD: StandardConsumer,
    }
    return consumer_map[consumer_type](name, attributes)