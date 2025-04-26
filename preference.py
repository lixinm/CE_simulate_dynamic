from typing import Dict
from logger import logger
from stakeholders.paas_provider import PaasProvider
from stakeholders.reuse_provider import ReuseProvider
from stakeholders.remanufacturer import Remanufacturer
from stakeholders.manufacturer import Manufacturer
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from stakeholders.consumer import Consumer
    from enablers.product import Product
    from product_category import ProductCategory

class Preference:
    def __init__(self, part_worth_values: Dict, consumer: 'Consumer') -> None:
        self.owner: 'Consumer' = consumer
        self.part_worth_values: Dict = part_worth_values

    def calculate_utility(self, product_category: 'ProductCategory', total_price: float) -> float:
        """
        製品に対する効用値を計算
        
        Args:
            product_category: 対象製品カテゴリ
            total_price: 使用期間を考慮した総価格
            
        Returns:
            float: 効用値
        """
        # 各ステータスに対する選好の重み付け
        status_utility = (
            # 新品購入の選好
            self.part_worth_values['ownership'] * 
            (1 if isinstance(product_category.provider, Manufacturer) else 0) +
            
            # サブスクリプションの選好
            self.part_worth_values['subscription'] * 
            (1 if isinstance(product_category.provider, PaasProvider) else 0) +
            
            # リユース品の選好
            self.part_worth_values['reuse'] * 
            (1 if isinstance(product_category.provider, ReuseProvider) else 0) +
            
            # リマニュファクチャリング品の選好
            self.part_worth_values['remanufacture'] * 
            (1 if isinstance(product_category.provider, Remanufacturer) else 0)
        )

        price_utility = (
            # 新品購入の選好
            self.part_worth_values['price'] * total_price * 
            (1 if isinstance(product_category.provider, Manufacturer) else 0) +

            # サブスクリプションの選好
            self.part_worth_values['price'] * total_price * self.owner.plan_of_use_period * 
            (1 if isinstance(product_category.provider, PaasProvider) else 0) +

            # リユース品の選好
            self.part_worth_values['price'] * total_price * 
            (1 if isinstance(product_category.provider, ReuseProvider) else 0) +

            # リマニュファクチャリング品の選好
            self.part_worth_values['price'] * total_price * 
            (1 if isinstance(product_category.provider, Remanufacturer) else 0)
        )

        # 総合的な効用値の計算
        utility = (
            # ステータスに対する選好
            status_utility
            
            # 価格の選好（負の効用）
            - price_utility
            #TODO: リユースに切り替える偏差
            + 19
            
            # スペックの選好
            # + self.part_worth_values['spec'] * product.age
        )

        return utility

