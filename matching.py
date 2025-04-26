from typing import List, Dict, Optional
from stakeholders.consumer import Consumer
from enablers.product import Product
from logger import logger
from collections import defaultdict
from stakeholders.manufacturer import Manufacturer
from stakeholders.paas_provider import PaasProvider
from stakeholders.reuse_provider import ReuseProvider
from stakeholders.remanufacturer import Remanufacturer
from product_category import ProductCategory
class Matching:
    """消費者と製品のマッチング処理を行うクラス"""
    
    def __init__(self):
        self.matches_history: Dict[int, Dict[Consumer, Product]] = {}
        self.PROVIDER_TYPES = ['manufacturer', 'paas_provider', 'reuse_provider', 'remanufacturer']
        self._init_history()
    
    def _init_history(self) -> None:
        """履歴データの初期化"""
        # defaultdictを使用して、年次データの自動初期化
        self.matches_history = defaultdict(lambda: {provider: 0 for provider in self.PROVIDER_TYPES})

    def match(self, year: int, consumers: List[Consumer], product_categories: List[ProductCategory]) -> Dict[Consumer, ProductCategory]:
        """
        消費者と製品のマッチングを実行
        
        Returns:
            Dict[Consumer, ProductCategory]: 消費者と製品カテゴリのマッチング結果
        """
        matches = {}

        # 各消費者について、最も効用の高い製品とマッチング
        for consumer in consumers:
            result = self._find_best_product_category(consumer, product_categories)
            if result:
                best_product_category, total_price = result
                matches[consumer] = best_product_category
                best_product_category.add_candidate(consumer)
                consumer.add_matched_product_category(best_product_category, total_price)
                logger.debug(f"Matched consumer {consumer.name} to product {best_product_category.provider.name}")
        
        # マッチング結果を記録
        self.record_matches(year, matches)

        return matches
        
    def _calculate_total_price(self, product_category: 'ProductCategory', plan_of_use_period: int) -> float:
        """
        使用期間に応じた総価格を計算
        
        Args:
            product: 対象製品
            plan_of_use_period: 計画使用期間
            
        Returns:
            float: 総価格
        """
        provider = product_category.provider
        return provider.calculate_price(product_category, plan_of_use_period)

    def _find_best_product_category(self, consumer: Consumer, product_categories: List[ProductCategory]) -> Optional[ProductCategory]:
        """
        消費者にとって最適な利用可能な製品カテゴリを見つける
        
        Args:
            consumer: 対象の消費者
            product_categories: 利用可能な製品カテゴリのリスト
            
        Returns:
            Optional[ProductCategory]: 利用可能な最適な製品カテゴリ。見つからないか効用が負の場合はNone
        """
        # 各製品の使用期間に応じた価格を計算
        product_category_with_price = []
        for product_category in product_categories:
            total_price = self._calculate_total_price(
                product_category,
                consumer.plan_of_use_period
            )
            product_category_with_price.append({
                'product_category': product_category,
                'total_price': total_price
            })
        # 効用値を計算して製品をソート
        product_categories_with_utility = [
            {
                'product_category': p['product_category'],
                'total_price': p['total_price'],
                'utility': consumer.calculate_utility(p['product_category'], p['total_price'])
            }
            for p in product_category_with_price
        ]
        sorted_product_categories = sorted(
            product_categories_with_utility,
            key=lambda p: p['utility'],
            reverse=True
        )

        logger.debug(
            f"Sorted product categories with utility for {consumer.name}: " + 
            f"{[(item['product_category'].provider.name, round(item['total_price']), round(item['utility'])) for item in sorted_product_categories]}"
        )
        if sorted_product_categories and sorted_product_categories[0]['utility'] > 0: # TODO: 効用が負の場合はマッチングしない
            best_match = sorted_product_categories[0]
            return best_match['product_category'], best_match['total_price']
        else:
            logger.debug(f"No product found with positive utility for consumer {consumer}")
            return None

    def record_matches(self, time_step: int, matches: Dict[Consumer, Product]):
        """マッチングを記録"""
        self.matches_history[time_step] = defaultdict(int)
        
        # プロバイダーごとのマッチング数をカウント
        for consumer, product in matches.items():
            provider = product.provider        
            if isinstance(provider, Manufacturer):
                self.matches_history[time_step]['manufacturer'] += 1
            elif isinstance(provider, PaasProvider):
                self.matches_history[time_step]['paas_provider'] += 1
            elif isinstance(provider, ReuseProvider):
                self.matches_history[time_step]['reuse_provider'] += 1
            elif isinstance(provider, Remanufacturer):
                self.matches_history[time_step]['remanufacturer'] += 1

    def get_matches_history(self) -> Dict[int, Dict[str, int]]:
        """プロバイダーごとのマッチング数の履歴を取得"""
        return dict(self.matches_history) 