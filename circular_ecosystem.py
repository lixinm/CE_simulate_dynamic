from enum import Enum
from stakeholders.manufacturer import create_manufacturer, ManufacturerType
from stakeholders.remanufacturer import create_remanufacturer, RemanufacturerType
from stakeholders.recycler import create_recycler, RecyclerType
from stakeholders.paas_provider import create_paas_provider, PaasProviderType
from stakeholders.reuse_provider import create_reuse_provider, ReuseProviderType
from stakeholders.provider import Provider
from typing import Dict
import pandas as pd
from stakeholders.consumer import Consumer, ConsumerType, create_consumer
from enablers.policy import Policy, PolicyType, PolicyParameter
from enablers.product import Product, ProductType
from logger import logger
from enablers.business_model import create_business_model, BusinessModelType
from matching import Matching
from product_category import ProductCategory
class CircularEcosystemType(Enum):
    ALL = "all"
    REVENUE_SHARE = "revenue_share"

class CircularEcosystem:
    """
    メーカとサードパーティがリユースを行うシミュレーション
    """

    def __init__(self):
        """
        CircularEcosystemの初期化
        """
        self.products = []
        self.consumers = []

    def initialize(
        self,
        name: str,
        entity: str,
        group: str,
        consumer_attributes: Dict,
        product_attributes: Dict,
        num_of_simulation: int,
        ecosystem_settings: Dict[str, str],
        policy_settings: Dict,
        business_model_settings: Dict,
        product_type: str = "STANDARD"
    ) -> None:
        """
        エコシステムの初期化を行う
        
        Args:
            name: プロジェクト名
            entity: エンティティ名
            group: グループ名
            consumer_attributes: 消費者の属性設定
            product_attributes: 製品の属性設定
            num_of_simulation: シミュレーション回数
            ecosystem_settings: エコシステムコンポーネントの設定
            policy_settings: 制度の設定（オプション）
            product_type: PaaSプロバイダーの製品タイプ
            paas_provider_type: PaaSプロバイダーのタイプ
            business_model_type: ビジネスモデルのタイプ
        """
        # 基本設定の初期化
        self.name = name
        self.entity = entity
        self.group = group
        self.consumer_attributes = consumer_attributes
        self.product_attributes = product_attributes
        self.num_of_simulation = num_of_simulation

        # エコシステム設定の初期化
        self.paas_provider_type = ecosystem_settings["paas_provider"]["type"]
        self.reuse_provider_type = ecosystem_settings["reuse_provider"]["type"]
        self.manufacturer_type = ecosystem_settings["manufacturer"]["type"]
        self.remanufacturer_type = ecosystem_settings["remanufacturer"]["type"]
        self.recycler_type = ecosystem_settings["recycler"]["type"]
        
        # プロバイダー属性の設定
        self.paas_provider_attributes = ecosystem_settings["paas_provider"]["attributes"]
        self.reuse_provider_attributes = ecosystem_settings["reuse_provider"]["attributes"]
        self.manufacturer_attributes = ecosystem_settings["manufacturer"]["attributes"]
        self.remanufacturer_attributes = ecosystem_settings["remanufacturer"]["attributes"]
        self.recycler_attributes = ecosystem_settings["recycler"]["attributes"]

        # シコシステムコンポーネントの初期化
        self.paas_provider = create_paas_provider(
            paas_provider_type=PaasProviderType[self.paas_provider_type],
            attributes=self.paas_provider_attributes,
            product_type=ProductType[product_type],
        )
        self.reuse_provider = create_reuse_provider(
            reuse_provider_type=ReuseProviderType[self.reuse_provider_type],
            attributes=self.reuse_provider_attributes,
            product_type=ProductType[product_type],
        )
        self.manufacturer = create_manufacturer(
            manufacturer_type=ManufacturerType[self.manufacturer_type],
            attributes=self.manufacturer_attributes,
            product_type=ProductType[product_type],
        )
        self.remanufacturer = create_remanufacturer(
            remanufacturer_type=RemanufacturerType[self.remanufacturer_type],
            attributes=self.remanufacturer_attributes,
            product_type=ProductType[product_type],
        )
        self.recycler = create_recycler(
            recycler_type=RecyclerType[self.recycler_type],
            attributes=self.recycler_attributes,
            product_type=ProductType[product_type],
        )

        # 制度の初期化（policy_settingsがある場合のみ）
        if policy_settings:
            self.policy = Policy(
                parameters=PolicyParameter(
                    carbon_tax_rate=policy_settings["carbon_tax_rate"],
                    subsidy_rate=policy_settings["subsidy_rate"],
                    deposit_amount=policy_settings["deposit_amount"],
                    epr_fee=policy_settings["epr_fee"],
                    repair_cost_reduction=policy_settings["repair_cost_reduction"]
                )
            )
        else:
            self.policy = None  # policy_settingsが指定されていない場合はNoneを設定
        
        # ビジネスモデルの初期化
        if business_model_settings:
            # アンダースコアを削除して大文字に変換
            model_type = business_model_settings["business_model_type"].replace("_", "").upper()
            self.business_model = create_business_model(
                business_model_type=BusinessModelType[model_type],
                attributes=business_model_settings["attributes"]
            )
        else:
            self.business_model = None

        # マッチングの初期化
        self.matching = Matching()

    def set_equilibrium_prices(self, prices: dict[str, float]):
        """
        各プロバイダーの均衡価格を設定
        
        Args:
            prices: プロバイダーごとの価格を含む辞書
                   例: {
                       'manufacturer': 100.0,
                       'paas_provider': 50.0,
                       'reuse_provider': 30.0,
                       'remanufacturer': 40.0,
                       'recycler': 20.0
                   }
        """
        # 各プロバイダーに価格を設定
        if 'manufacturer' in prices and self.manufacturer:
            self.manufacturer.set_price(prices['manufacturer'])
            
        if 'paas_provider' in prices and self.paas_provider:
            self.paas_provider.set_price(prices['paas_provider'])
            
        if 'reuse_provider' in prices and self.reuse_provider:
            self.reuse_provider.set_price(prices['reuse_provider'])
            
        if 'remanufacturer' in prices and self.remanufacturer:
            self.remanufacturer.set_price(prices['remanufacturer'])
            
        if 'recycler' in prices and self.recycler:
            self.recycler.set_price(prices['recycler'])

    def execute_yearly_cycle(self, year: int) -> pd.DataFrame:
        """年次サイクルの実行"""
        logger.debug(f"##### Starting yearly cycle for year {year} #####")
        new_consumers = []
        
        # 消費者の生成
        for name, attribute in self.consumer_attributes.items():
            logger.debug(f"--- Creating {attribute['num_of_players']} consumers of type {name} ---")
            logger.debug("part_worth_values: [ownership,subscription,reuse,remanufacture,price,spec]")
            for i in range(attribute["num_of_players"]):
                consumer_name = f"{name}_{year}_{i}"
                consumer = create_consumer(
                    consumer_type=ConsumerType[attribute.get("type", "STANDARD")],
                    name=consumer_name,
                    attributes=attribute
                )
                logger.debug(f"Created consumer {consumer.name}, "
                           f"part_worth_values: {[round(v, 3) for v in consumer.preference.part_worth_values.values()]}, "
                           f"plan_of_use_period: {consumer.plan_of_use_period}")
                new_consumers.append(consumer)
        self.consumers.extend(new_consumers)

        # 製品の生成
        new_products = []
        new_products.extend(self.manufacturer.create_products(self.product_attributes, year))
        new_products.extend(self.paas_provider.provide_products(self.product_attributes, year))
        new_products.extend(self.reuse_provider.provide_products(self.product_attributes, year))
        self.products.extend(new_products)

        # ビジネスモデルのコスト計算
        self.business_model.calculate_product_costs(new_products, year)

        # # 消費者に制度を適用
        # for consumer in consumers:
        #     self.policy.apply_to_consumer(consumer)

        # # 製品に制度を適用
        # for product in products:
        #     self.policy.apply_to_product(product)

        # マッチング実行
        logger.debug("---Starting matching process---")
        matches = self.matching.match(year, new_consumers, self.products)
        
        # ビジネスモデルの売上計算
        if self.business_model:
            self.business_model.calculate_revenues(matches, year)
                
        # 消費者の使用年数更新
        logger.debug("---Updating consumer status---")
        for consumer in self.consumers:
            consumer.update_use_period()
        
        # 製品の状態更新、移管、返却処理
        logger.debug("---Updating product status---")
        for product in self.products:
            # 年次の状態更新（年齢と使用期間）
            product.update_yearly_status()
            
            # マッチしている製品の故障判定と修理
            if product.matched:
                product.determine_malfunction()
                if product.malfunction:
                    logger.debug(f"Product {product.name} malfunctioned")
                    if product.provider is not None:
                        # 修理コストを計算
                        self.business_model.calculate_repair_costs(product, year)
                        product.provider.repair_product(product)
                        logger.debug(f"Product {product.name} repaired by {product.provider.name}")
            else:
                # 未マッチ製品の移管処理
                if product.next_provider == "paas_provider":
                    product.add_provider(year+1, self.paas_provider)
                    logger.debug(f"Product {product.name} is transferred to {self.paas_provider.name}")
                elif product.next_provider == "reuse_provider":
                    product.add_provider(year+1, self.reuse_provider)
                    logger.debug(f"Product {product.name} is transferred to {self.reuse_provider.name}")
                elif product.next_provider == "recycler":
                    product.add_provider(year+1, self.recycler)
                    logger.debug(f"Product {product.name} is transferred to {self.recycler.name}")
        logger.debug("---Calculating business model revenues---")
        logger.debug(f"Revenue: {self.business_model.revenue_history[year]}")
        logger.debug(f"Product cost: {self.business_model.product_cost_history[year]}")
        logger.debug(f"Repair cost: {self.business_model.repair_cost_history[year]}")
        
        # ビジネスモデルから履歴データを取得
        revenue_history = dict(self.business_model.revenue_history[year])
        product_cost_history = dict(self.business_model.product_cost_history[year])
        repair_cost_history = dict(self.business_model.repair_cost_history[year])
        
        # マッチングの履歴データを取得
        matches_history = dict(self.matching.get_matches_history())

        # マテリアフローの履歴データを取得
        material_flow_all = pd.DataFrame(columns=["source", "target", "value"])
        for product in self.products:
            material_flow_all = pd.concat([material_flow_all, product.get_material_flow_history()], ignore_index=True)
        material_flow_all = material_flow_all.groupby(["source", "target"]).sum().reset_index()
        
        # 財務フローの履歴データを取得
        financial_flow_all = self.business_model.get_financial_flow_history().groupby(["source", "target"]).sum().reset_index()

        # 結果の生成
        result = {
            'revenue_history': revenue_history,
            'product_cost_history': product_cost_history,
            'repair_cost_history': repair_cost_history,
            'matches_history': matches_history,
            'material_flow_history': material_flow_all,
            'financial_flow_history': financial_flow_all
        }
        
        return pd.DataFrame([result])

class CircularEcosystem_RevenueShare:
    """
    メーカとPaaSプロバイダーがレベニューシェアを行うシミュレーション
    """

    def __init__(self):
        """
        CircularEcosystem_RevenueShareの初期化
        """
        self.products = []
        self.consumers = []
        self.product_categories = []

    def initialize(
        self,
        name: str,
        entity: str,
        group: str,
        consumer_attributes: Dict,
        product_attributes: Dict,
        num_of_simulation: int,
        ecosystem_settings: Dict[str, str],
        policy_settings: Dict,
        business_model_settings: Dict,
        product_type: str = "STANDARD"
    ) -> None:
        """
        エコシステムの初期化を行う
        
        Args:
            name: プロジェクト名
            entity: エンティティ名
            group: グループ名
            consumer_attributes: 消費者の属性設定
            product_attributes: 製品の属性設定
            num_of_simulation: シミュレーション回数
            ecosystem_settings: エコシステムコンポーネントの設定
            policy_settings: 制度の設定（オプション）
            product_type: PaaSプロバイダーの製品タイプ
            paas_provider_type: PaaSプロバイダーのタイプ
            business_model_type: ビジネスモデルのタイプ
        """
        # 基本設定の初期化
        self.name = name
        self.entity = entity
        self.group = group
        self.consumer_attributes = consumer_attributes
        self.product_attributes = product_attributes
        self.num_of_simulation = num_of_simulation
        self.ecosystem_settings = ecosystem_settings

        # エコシステム設定の初期化
        self.paas_provider_type = ecosystem_settings["paas_provider"]["type"]
        self.manufacturer_type = ecosystem_settings["manufacturer"]["type"]

        # プロバイダー属性の設定
        self.paas_provider_attributes = ecosystem_settings["paas_provider"]["attributes"]
        self.manufacturer_attributes = ecosystem_settings["manufacturer"]["attributes"]

        # シコシステムコンポーネントの初期化
        self.paas_provider = create_paas_provider(
            paas_provider_type=PaasProviderType[self.paas_provider_type],
            attributes=self.paas_provider_attributes,
            product_type=ProductType[product_type],
        )
        self.manufacturer = create_manufacturer(
            manufacturer_type=ManufacturerType[self.manufacturer_type],
            attributes=self.manufacturer_attributes,
            product_type=ProductType[product_type],
        )

        # 製品カテゴリの初期化
        for provider_name, settings in ecosystem_settings.items():
            if provider_name not in ["paas_provider", "manufacturer"]:
                continue
                
            provider_instance = None
            if provider_name == "paas_provider" and self.paas_provider:
                provider_instance = self.paas_provider
            elif provider_name == "manufacturer" and self.manufacturer:
                provider_instance = self.manufacturer
                
            if provider_instance:
                product_category = ProductCategory(provider_instance)
                self.product_categories.append(product_category)
                logger.debug(f"Created product category for {provider_name}")

        # 制度の初期化（policy_settingsがある場合のみ）
        if policy_settings:
            self.policy = Policy(
                parameters=PolicyParameter(
                    carbon_tax_rate=policy_settings["carbon_tax_rate"],
                    subsidy_rate=policy_settings["subsidy_rate"],
                    deposit_amount=policy_settings["deposit_amount"],
                    epr_fee=policy_settings["epr_fee"],
                    repair_cost_reduction=policy_settings["repair_cost_reduction"]
                )
            )
        else:
            self.policy = None  # policy_settingsが指定されていない場合はNoneを設定

        # ビジネスモデルの初期化
        if business_model_settings:
            # アンダースコアを削除して大文字に変換
            model_type = business_model_settings["business_model_type"].replace("_", "").upper()
            self.business_model = create_business_model(
                business_model_type=BusinessModelType[model_type],
                attributes=business_model_settings["attributes"]
            )
        else:
            self.business_model = None

        # マッチングの初期化
        self.matching = Matching()

    def set_equilibrium_prices(self, prices: dict[str, float]):
        """
        各プロバイダーの均衡価格を設定
        
        Args:
            prices: プロバイダーごとの価格を含む辞書
                   例: {
                       'manufacturer': 100.0,
                       'paas_provider': 50.0,
                       'reuse_provider': 30.0,
                       'remanufacturer': 40.0,
                       'recycler': 20.0
                   }
        """
        # 各プロバイダーに価格を設定
        if 'manufacturer' in prices and self.manufacturer:
            self.manufacturer.set_price(prices['manufacturer'])
            
        if 'paas_provider' in prices and self.paas_provider:
            self.paas_provider.set_price(prices['paas_provider'])
            
        if 'reuse_provider' in prices and self.reuse_provider:
            self.reuse_provider.set_price(prices['reuse_provider'])
            
        if 'remanufacturer' in prices and self.remanufacturer:
            self.remanufacturer.set_price(prices['remanufacturer'])
            
        if 'recycler' in prices and self.recycler:
            self.recycler.set_price(prices['recycler'])

    def execute_yearly_cycle(self, year: int) -> pd.DataFrame:
        """年次サイクルの実行"""
        logger.debug(f"##### Starting yearly cycle for year {year} #####")
        new_consumers = []
        
        # 消費者の生成
        for name, attribute in self.consumer_attributes.items():
            logger.debug(f"--- Creating {attribute['num_of_players']} consumers of type {name} ---")
            logger.debug("part_worth_values: [ownership,subscription,reuse,remanufacture,price,spec]")
            for i in range(attribute["num_of_players"]):
                consumer_name = f"{name}_{year}_{i}"
                consumer = create_consumer(
                    consumer_type=ConsumerType[attribute.get("type", "STANDARD")],
                    name=consumer_name,
                    attributes=attribute
                )
                logger.debug(f"Created consumer {consumer.name}, "
                           f"part_worth_values: {[round(v, 3) for v in consumer.preference.part_worth_values.values()]}, "
                           f"plan_of_use_period: {consumer.plan_of_use_period}")
                new_consumers.append(consumer)
        self.consumers.extend(new_consumers)

        # 製品の生成
        new_products = []
        new_products.extend(self.manufacturer.create_products(self.product_attributes, year, self.manufacturer_attributes["base_production_volume"]))
        new_products.extend(self.paas_provider.create_products(self.product_attributes, year, self.paas_provider_attributes["base_production_volume"]))
        self.products.extend(new_products)

        # 利用可能な製品を取得
        logger.debug("---Getting available products---")
        available_products = []
        for product in self.products:
            if product.is_available():
                available_products.append(product)
                logger.debug(f"{product.name}")

        # 製品カテゴリに製品を追加
        for product_category in self.product_categories:
            for product in available_products:
                if product_category.provider == product.provider:
                    product_category.add_products(product)

        # # 消費者に制度を適用
        # for consumer in consumers:
        #     self.policy.apply_to_consumer(consumer)

        # # 製品に制度を適用
        # for product in products:
        #     self.policy.apply_to_product(product)

        # マッチング実行
        logger.debug("---Starting matching process---")
        matches = self.matching.match(year, new_consumers, self.product_categories)

        # マッチング結果から製品の割当
        for product_category in self.product_categories:
            # 製品カテゴリに製品が足りない場合は新規生産/調達
            if len(product_category.candidates) > len(product_category.product_list):
                _new_products = product_category.provider.create_products(self.product_attributes, year, (len(product_category.candidates) - len(product_category.product_list)))
                product_category.add_products(_new_products)
                new_products.extend(_new_products)
                self.products.extend(_new_products)
            for consumer, product in zip(product_category.candidates, product_category.product_list):
                consumer.set_possession(product)
                product.add_consumer(year, consumer.name)

        # ビジネスモデルのコスト計算
        self.business_model.calculate_product_costs(new_products, year)

        # ビジネスモデルの売上計算
        if self.business_model:
            self.business_model.calculate_revenues(matches, year)
                        
        # 消費者の使用年数更新
        logger.debug("---Updating consumer status---")
        for consumer in self.consumers:
            consumer.update_use_period()
        # 製品の状態更新、移管、返却処理
        logger.debug("---Updating product status---")
        repaired_products = [] # 修理済みの製品リスト
        for product in self.products:
            # 年次の状態更新（年齢と使用期間）
            product.update_yearly_status()
            
            # マッチしている製品の故障判定と修理
            if product.matched:
                product.determine_malfunction()
                if product.malfunction:
                    logger.debug(f"Product {product.name} malfunctioned")
                    if product.provider is not None:
                        # 修理コストを計算
                        product.provider.repair_product(product)
                        if not product.malfunction:
                            repaired_products.append(product)
                        logger.debug(f"Product {product.name} repaired by {product.provider.name}")
            else:
                # 未マッチ製品の移管処理
                if product.next_provider == "paas_provider":
                    product.add_provider(year+1, self.paas_provider)
                    logger.debug(f"Product {product.name} is transferred to {self.paas_provider.name}")
        
        # 修理コストの計算
        self.business_model.calculate_repair_costs(repaired_products, year)

        # 利益の計算
        self.business_model.calculate_profit(year)

        # 製品カテゴリの更新
        for product_category in self.product_categories:
            product_category.remove_all()

        logger.debug("---Calculating business model revenues---")
        logger.debug(f"Revenue: {self.business_model.revenue_history[year]}")
        logger.debug(f"Product cost: {self.business_model.product_cost_history[year]}")
        logger.debug(f"Repair cost: {self.business_model.repair_cost_history[year]}")
        logger.debug(f"Profit: {self.business_model.profit_history[year]}")
        # ビジネスモデルから履歴データを取得
        revenue_history = dict(self.business_model.revenue_history[year])
        product_cost_history = dict(self.business_model.product_cost_history[year])
        repair_cost_history = dict(self.business_model.repair_cost_history[year])
        profit_history = dict(self.business_model.profit_history[year])
        # マッチングの履歴データを取得
        matches_history = dict(self.matching.get_matches_history())

        # マテリアフローの履歴データを取得
        material_flow_all = pd.DataFrame(columns=["source", "target", "value"])
        for product in self.products:
            material_flow_all = pd.concat([material_flow_all, product.get_material_flow_history()], ignore_index=True)
        material_flow_all = material_flow_all.groupby(["source", "target"]).sum().reset_index()
        
        # 財務フローの履歴データを取得
        financial_flow_all = self.business_model.get_financial_flow_history().groupby(["source", "target"]).sum().reset_index()

        # 結果の生成
        result = {
            'revenue_history': revenue_history,
            'product_cost_history': product_cost_history,
            'repair_cost_history': repair_cost_history,
            'profit_history': profit_history,
            'matches_history': matches_history,
            'material_flow_history': material_flow_all,
            'financial_flow_history': financial_flow_all
        }
        
        return pd.DataFrame([result])

def create_circular_ecosystem(circular_ecosystem_type: CircularEcosystemType) -> CircularEcosystem:
    """
    サーキュラーエコシステムファクトリー関数
    
    Args:
        circular_ecosystem_type: エコシステムの種類
    Returns:
        CircularEcosystem: 指定された種類のエコシステムインスタンス
    """
    circular_ecosystem_map = {
        CircularEcosystemType.ALL: CircularEcosystem,
        CircularEcosystemType.REVENUE_SHARE: CircularEcosystem_RevenueShare,
    }
    return circular_ecosystem_map[circular_ecosystem_type]()

