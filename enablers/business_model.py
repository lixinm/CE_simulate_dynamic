from enum import Enum
from typing import Dict, List
from dataclasses import dataclass
import logging
from stakeholders.manufacturer import Manufacturer
from stakeholders.reuse_provider import ReuseProvider
from stakeholders.paas_provider import PaasProvider
from stakeholders.remanufacturer import Remanufacturer
from stakeholders.recycler import Recycler
from enablers.product import Product
from collections import defaultdict
import pandas as pd
logger = logging.getLogger(__name__)

class BusinessModelType(Enum):
    """ビジネスモデルの種類"""
    STANDARD = "standard"
    REVENUESHARING = "revenue_sharing"  # キーを"REVENUESHARING"に変更

class BusinessModel:
    """ビジネスモデル基底クラス"""
    
    def __init__(self, attributes: Dict = None):
        """
        ビジネスモデルの初期化
        
        Args:
            attributes: ビジネスモデルの属性を含む辞書（オプション）
        """
        self.attributes = attributes or {}
        self.PROVIDER_TYPES = ['manufacturer', 'paas_provider', 'reuse_provider', 'remanufacturer', 'recycler']
        self._reset_revenues()
        self._reset_product_costs()
        self._reset_repair_costs()
        self._init_history()
        self.financial_flow_data = []
    
    def _init_history(self) -> None:
        """履歴データの初期化"""
        # defaultdictを使用して、年次データの自動初期化
        self.revenue_history = defaultdict(lambda: {provider: 0.0 for provider in self.PROVIDER_TYPES})
        self.product_cost_history = defaultdict(lambda: {provider: 0.0 for provider in self.PROVIDER_TYPES})
        self.repair_cost_history = defaultdict(lambda: {provider: 0.0 for provider in self.PROVIDER_TYPES})
        self.profit_history = defaultdict(lambda: {provider: 0.0 for provider in self.PROVIDER_TYPES})

    def calculate_revenues(self, matches: Dict) -> None:
        """収益計算（サブクラスで実装）"""
        raise NotImplementedError

    def _reset_revenues(self) -> None:
        """収益の初期化"""
        self.revenues = {provider: 0.0 for provider in self.PROVIDER_TYPES}
    
    def _reset_product_costs(self) -> None:
        """製品のコストの初期化"""
        self.product_costs = {provider: 0.0 for provider in self.PROVIDER_TYPES}
        
    def _reset_repair_costs(self) -> None:
        """修理コストの初期化"""
        self.repair_costs = {provider: 0.0 for provider in self.PROVIDER_TYPES}
        
    def record_financial_flow(self, source: str, target: str, value: float) -> None:
        """財務フローの記録"""
        self.financial_flow_data.append({'source': source, 'target': target, 'value': value})

    def get_financial_flow_history(self) -> pd.DataFrame:
        """財務フローの履歴データを取得"""
        self.financial_flow = pd.DataFrame(self.financial_flow_data) 
        return self.financial_flow

class StandardBusinessModel(BusinessModel):
    """従来型ビジネスモデル"""
    
    def __init__(self, attributes: Dict = None):
        """
        標準的なビジネスモデルの初期化
        
        Args:
            attributes: ビジネスモデルの属性を含む辞書（オプション）
        """
        super().__init__(attributes)
        self.paas_customers = {}  # PaaSの顧客管理を追加

    def calculate_revenues(self, matches: Dict, year: int) -> None:
        """
        各ステークホルダーの売上を計算
        """
        # 売上の初期化
        self._reset_revenues()

        # 各プロバイダーの収益を計算
        for consumer, product in matches.items():
            price = consumer.matched_price
            provider = product.provider

            if isinstance(provider, Manufacturer):
                self.revenues['manufacturer'] += price
                self.record_financial_flow('consumer', 'manufacturer', price)
            elif isinstance(provider, ReuseProvider):
                self.revenues['reuse_provider'] += price
                self.record_financial_flow('consumer', 'reuse_provider', price)
            elif isinstance(provider, PaasProvider):
                # PaaS顧客として登録
                self.paas_customers[consumer] = {
                    'remaining_period': consumer.plan_of_use_period,
                    'price': consumer.matched_price
                }          
            elif isinstance(provider, Remanufacturer):
                self.revenues['remanufacturer'] += price
                self.record_financial_flow('consumer', 'remanufacturer', price)
            elif isinstance(provider, Recycler):
                self.revenues['recycler'] += price
                self.record_financial_flow('consumer', 'recycler', price)
            else:
                raise ValueError(f"不明なプロバイダータイプです: {type(provider)}")
            
        # 既存PaaS顧客からの月額収益を計算
        paas_customers_to_remove = []
        
        for consumer, info in self.paas_customers.items():
            if info['remaining_period'] > 0:
                self.revenues['paas_provider'] += info['price']
                self.record_financial_flow('consumer', 'paas_provider', info['price'])
                info['remaining_period'] -= 1
            
            if info['remaining_period'] <= 0:
                paas_customers_to_remove.append(consumer)
        
        # 契約期間が終了した顧客を削除
        for consumer in paas_customers_to_remove:
            del self.paas_customers[consumer]
        
        # 履歴データの更新
        for provider in self.PROVIDER_TYPES:
            self.revenue_history[year][provider] = self.revenues[provider]
        
        # ログ出力
        logger.debug(f"Revenue history: {self.revenue_history[year]}")

    def calculate_product_costs(self, products: List[Product], year: int) -> None:
        """製品のコスト計算"""

        # 製品のコストの初期化
        self._reset_product_costs()

        for product in products:
            provider = product.provider
            if isinstance(product.provider, Manufacturer):
                self.product_costs['manufacturer'] += provider.production_cost
            elif isinstance(product.provider, ReuseProvider):
                self.product_costs['reuse_provider'] += provider.reuse_cost
            elif isinstance(product.provider, PaasProvider):
                self.product_costs['paas_provider'] += provider.procurement_cost
            else:
                raise ValueError(f"不明なプロバイダータイプです: {type(product.provider)}")
        
        # 履歴データの更新
        for provider in self.PROVIDER_TYPES:
            self.product_cost_history[year][provider] = self.product_costs[provider]
            
    def calculate_repair_costs(self, products: List[Product], year: int) -> None:
        """修理コストの計算"""

        # 修理コストの初期化
        self._reset_repair_costs()

        for product in products:
            provider = product.provider
            if isinstance(provider, ReuseProvider):
                self.repair_costs['reuse_provider'] += provider.repair_cost
            elif isinstance(provider, Manufacturer):
                self.repair_costs['manufacturer'] += provider.repair_cost
            elif isinstance(provider, PaasProvider):
                self.repair_costs['paas_provider'] += provider.repair_cost
            else:
                raise ValueError(f"修理コストを計算できないプロバイダータイプです: {type(provider)}")
        
        # 履歴データの更新
        for provider in self.PROVIDER_TYPES:
            self.repair_cost_history[year][provider] = self.repair_costs[provider]

    def calculate_profit(self, year: int) -> None:
        """利益の計算"""
        for provider in self.PROVIDER_TYPES:
            self.profit_history[year][provider] = self.revenue_history[year][provider] - self.product_cost_history[year][provider] - self.repair_cost_history[year][provider]
    
class RevenueSharingBusinessModel(BusinessModel):
    """収益分配型ビジネスモデル"""
    
    def __init__(self, attributes: Dict):
        """
        収益共有ビジネスモデルの初期化
        
        Args:
            attributes: ビジネスモデルの属性を含む辞書
                revenue_share: 収益共有率
        """
        super().__init__(attributes)
        self.paas_customers = {}  # PaaSの顧客管理を追加
        self.revenue_share = float(attributes["revenue_share"])
    
    def calculate_revenues(self, matches: Dict, year: int) -> None:
        """
        各ステークホルダーの売上を計算
        """
        # 売上の初期化
        self._reset_revenues()

        # 各プロバイダーの収益を計算
        for consumer, product_category in matches.items():
            price = consumer.matched_price
            provider = product_category.provider

            if isinstance(provider, Manufacturer):
                self.revenues['manufacturer'] += price
                self.record_financial_flow('consumer', 'manufacturer', price)
            elif isinstance(provider, PaasProvider):
                # PaaS顧客として登録
                self.paas_customers[consumer] = {
                    'remaining_period': consumer.plan_of_use_period,
                    'price': consumer.matched_price
                }          
            else:
                raise ValueError(f"不明なプロバイダータイプです: {type(provider)}")
            
        # 既存PaaS顧客からの月額収益を計算
        paas_customers_to_remove = []
        
        for consumer, info in self.paas_customers.items():
            if info['remaining_period'] > 0:
                self.revenues['paas_provider'] += info['price'] * (1 - self.revenue_share)
                self.revenues['manufacturer'] += info['price'] * self.revenue_share
                self.record_financial_flow('consumer', 'paas_provider', info['price'] * (1 - self.revenue_share))
                self.record_financial_flow('paas_provider', 'manufacturer', info['price'] * self.revenue_share)
                info['remaining_period'] -= 1
            
            if info['remaining_period'] <= 0:
                paas_customers_to_remove.append(consumer)
        
        # 契約期間が終了した顧客を削除
        for consumer in paas_customers_to_remove:
            del self.paas_customers[consumer]
        
        # 履歴データの更新
        for provider in self.PROVIDER_TYPES:
            self.revenue_history[year][provider] = self.revenues[provider]
        
        # ログ出力
        logger.debug(f"Revenue history: {self.revenue_history[year]}")

    def calculate_product_costs(self, products: List[Product], year: int) -> None:
        """製品のコスト計算"""

        # 製品のコストの初期化
        self._reset_product_costs()

        for product in products:
            provider = product.provider
            if isinstance(product.provider, Manufacturer):
                self.product_costs['manufacturer'] += provider.production_cost
            elif isinstance(product.provider, PaasProvider):
                self.product_costs['manufacturer'] += provider.procurement_cost # PaaSプロバイダーのコストを製造業者に分配
            else:
                raise ValueError(f"不明なプロバイダータイプです: {type(product.provider)}")
        
        # 履歴データの更新
        for provider in self.PROVIDER_TYPES:
            self.product_cost_history[year][provider] = self.product_costs[provider]
            
    def calculate_repair_costs(self, products: List[Product], year: int) -> None:
        """修理コストの計算"""

        # 修理コストの初期化
        self._reset_repair_costs()

        for product in products:
            provider = product.provider
            if isinstance(provider, Manufacturer):
                self.repair_costs['manufacturer'] += provider.repair_cost
            elif isinstance(provider, PaasProvider):
                self.repair_costs['manufacturer'] += provider.repair_cost # PaaSプロバイダーの修理コストを製造業者に分配
            else:
                raise ValueError(f"修理コストを計算できないプロバイダータイプです: {type(provider)}")
        
        # 履歴データの更新
        for provider in self.PROVIDER_TYPES:
            self.repair_cost_history[year][provider] = self.repair_costs[provider]

    def calculate_profit(self, year: int) -> None:
        """利益の計算"""
        for provider in self.PROVIDER_TYPES:
            self.profit_history[year][provider] = self.revenue_history[year][provider] - self.product_cost_history[year][provider] - self.repair_cost_history[year][provider]

def create_business_model(
    business_model_type: BusinessModelType,
    attributes: Dict
) -> BusinessModel:
    """ビジネスモデルファクトリー関数"""
    business_model_map = {
        BusinessModelType.STANDARD: StandardBusinessModel,
        BusinessModelType.REVENUESHARING: RevenueSharingBusinessModel
    }
    return business_model_map[business_model_type](attributes)