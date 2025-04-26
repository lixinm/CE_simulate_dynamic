from enum import Enum
from typing import Dict, Type, Any, TYPE_CHECKING
import numpy as np
import pandas as pd
from logger import logger
from product_category import ProductCategory
if TYPE_CHECKING:
    from stakeholders.provider import Provider

class ProductType(Enum):
    """製品タイプの列挙型"""
    STANDARD = "standard"
    SUBSCRIPTION = "subscription"

class Product:
    """製品基底クラス"""
    def __init__(
        self,
        attributes: Dict[str, Any]
    ):
        """
        Args:
            attributes: 製品の属性を含む辞書
                name: 製品名
                price: 販売価格
                lifetime: 使用寿命
                weibull_alpha: ワイブル分布の形状パラメータ
                weibull_beta: ワイブル分布の尺度パラメータ
        """
        self.name = attributes["name"]
        self.lifetime = attributes["lifetime"]
        self.price = attributes["price"]
        self._matched = False
        self._malfunction = False
        self._disposed = False
        self._age = 0      # 製品の製造からの経過年数
        self.use_period = 0  # 現在の消費者による使用期間
        self.consumers = {}
        self.weibull_alpha = attributes["weibull_alpha"]  # ワイブル分布の形状パラメータ
        self.weibull_beta = attributes["weibull_beta"]  # ワイブル分布の尺度パラメータ
        self.provider_history = {}  # 年齢をキーとしたプロバイダー履歴
        self._provider = None
        self.next_provider = None
        self.material_flow = pd.DataFrame(columns=["source", "target", "value"])
        self.product_category = None

    def update_yearly_status(self) -> None:
        """
        年次の状態更新
        - 製品の年齢（製造からの経過年数）を更新
        - マッチしている場合は使用期間を更新
        - 年齢が寿命を超えた場合は廃棄
        """
        # 製品の年齢は常に増加
        self._age += 1
        
        # マッチしている場合のみ使用期間を更新
        if self._matched:
            self.use_period += 1
            logger.debug(f"Product {self.name}: age={self._age}, use_period={self.use_period}")
        else:
            logger.debug(f"Product {self.name}: age={self._age}, not in use")
            
        # 年齢が寿命を超えた場合、廃棄予定に設定
        if self._age >= self.lifetime:
            self.dispose()
            logger.debug(f"Product {self.name}: disposed due to exceeding lifetime")

    def reset_use_period(self) -> None:
        """
        新しい消費者に提供される際に使用期間をリセット
        """
        self.use_period = 0

    def add_provider(self, year: int, provider: 'Provider') -> None:
        """プロバイダーの追加"""
        self.provider_history[year] = provider.name
        self._provider = provider
        self.next_provider = None
        
    def add_consumer(self, year: int, consumer: str) -> None:
        """消費者の追加"""
        self.consumers[year] = consumer
        self._matched = True
        # マテリアフローの記録
        self.record_material_flow(self.provider.name, "consumer")

    def update_use_period(self) -> None:
        """使用年数を更新し、故障の有無を判定"""
        self.use_period += 1
        
        # 故障の有無を判定
        self.determine_malfunction()

        # 使用年数が計画使用年数を超えた場合、廃棄予定に設定
        if self.use_period >= self.lifetime:
            self.dispose()
    
    def is_available(self) -> bool:
        """
        製品が利用可能かどうかを判定
        
        Returns:
            bool: 以下の全ての条件を満たす場合にTrue
                - 残存寿命が0より大きい
                - マッチングされていない
                - 故障していない
                - 廃棄予定ではない
        """

        return (
            self.calculate_remaining_lifetime() > 0 and
            not self._matched and
            not self._malfunction and
            not self._disposed
        )
    
    def determine_malfunction(self) -> bool:
        """
        ワイブル分布に従って故障の発生を判定する
        
        Returns:
            bool: 故障が発生したかどうか
        """
        failure_prob = self._calculate_failure_rate()
        failure = np.random.choice(
            [False, True],
            # p=[1 - failure_prob, failure_prob]
            p=[0.5, 0.5]
        )
        
        self._malfunction = failure

        # 故障した場合、マテリアフローの記録
        if failure:
            if self.matched:    
                self.record_material_flow("consumer", "repair")
            else:
                self.record_material_flow(self.provider.name, "repair")

        return failure

    @property
    def malfunction(self) -> bool:
        """
        現在の故障状態を取得する
        
        Returns:
            bool: 故障しているかどうか
        """
        return self._malfunction
    
    @property
    def disposed(self) -> bool:
        """廃棄状態かどうかを取得"""
        return self._disposed
    
    @property
    def matched(self) -> bool:
        """マッチング状態かどうかを取得"""
        return self._matched
            
    def remove_consumer(self) -> None:
        """消費者の削除"""
        self._matched = False
    
    def calculate_remaining_lifetime(self) -> int:
        """使用可能な残り寿命を計算"""
        return self.lifetime - self.use_period

    def repair(self) -> None:
        """製品を修理状態にする"""
        self._malfunction = False

        # 修理した場合、マテリアフローの記録
        if self.matched:
            self.record_material_flow("repair", "consumer")
        else:
            self.record_material_flow("repair", self.provider.name)
    
    def dispose(self) -> None:
        """廃棄状態に設定"""
        self._disposed = True

        # マテリアフローの記録
        if self.matched:
            self.record_material_flow("consumer", "disposal")
        else:
            self.record_material_flow(self.provider.name, "disposal")

    def _calculate_failure_rate(self) -> float:
        """
        ワイブル分布に基づいて故障確率を計算する
        F(t) = 1 - exp(-(t/η)^m)
        
        Returns:
            float: 故障確率（0-1の範囲）
        """
        # ワイブルパラメータの設定
        m = self.weibull_alpha  # 形状パラメータ（故障の傾向を表す）
        eta = self.weibull_beta  # 尺度パラメータ（特性寿命、B63.2寿命）
        t = self.use_period     # 経過時間（製品年齢）
                
        # ワイブル分布の累積分布関数による故障確率の計算
        failure_prob = 1 - np.exp(-(t / eta) ** m)
        
        # 故障確率を0-1の範囲に制限
        return min(max(failure_prob, 0.0), 1.0)

    @property
    def provider(self) -> 'Provider':
        """
        現在のプロバイダーを取得
        
        Returns:
            Provider: 現在のプロバイダー
        """
        return self._provider
    
    @property
    def age(self) -> int:
        """製品の年齢を取得"""
        return self._age

    def set_next_provider(self, provider: str) -> None:
        """
        次のプロバイダー（返却先）を設定
        
        Args:
            provider: 返却先のプロバイダー名
        """
        # マテリアフローの記録
        self.record_material_flow("consumer", self.provider.name)
        self.next_provider = provider

    def release(self) -> None:
        """製品の解放処理"""
        self.reset_use_period()
        self._matched = False
    
    def record_material_flow(self, source: str, target: str) -> None:
        """マテリアフローの記録"""
        self.material_flow = pd.concat([self.material_flow, pd.DataFrame({'source': [source], 'target': [target], 'value': [1]})], ignore_index=True)
    
    def get_material_flow_history(self) -> pd.DataFrame:
        """マテリアフローの履歴データを取得"""
        return self.material_flow
    
    def set_product_category(self, product_category: ProductCategory) -> None:
        """製品カテゴリの設定"""
        self.product_category = product_category

class StandardProduct(Product):
    """標準的な製品"""
    def __init__(self, attributes: Dict[str, Any]):
        super().__init__(attributes=attributes)