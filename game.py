from circular_ecosystem import CircularEcosystem
from stakeholders.provider import Provider
from scipy.optimize import minimize_scalar
import logging
import copy

logger = logging.getLogger(__name__)    

class Game:
    def __init__(self):
        self.price_min = 10
        self.price_max = 200
        self.damping = 0.5
        self.tol = 5
        self.max_iter = 1000

    def find_equilibrium(self, ecosystem: CircularEcosystem, year: int) -> dict[str, float]:
        """
        エコシステムの均衡価格を探索
        
        Args:
            ecosystem: サーキュラーエコシステムのインスタンス
            
        Returns:
            dict[str, float]: プロバイダーごとの均衡価格を含む辞書
        """
        # 存在するプロバイダーのみでマッピングを作成
        provider_instances = {}
        
        # ecosystem_settingsに基づいてプロバイダーを追加
        if "manufacturer" in ecosystem.ecosystem_settings:
            provider_instances['manufacturer'] = ecosystem.manufacturer
            
        if "paas_provider" in ecosystem.ecosystem_settings:
            provider_instances['paas_provider'] = ecosystem.paas_provider
            
        if "reuse_provider" in ecosystem.ecosystem_settings:
            provider_instances['reuse_provider'] = ecosystem.reuse_provider
            
        if "remanufacturer" in ecosystem.ecosystem_settings:
            provider_instances['remanufacturer'] = ecosystem.remanufacturer
            
        if "recycler" in ecosystem.ecosystem_settings:
            provider_instances['recycler'] = ecosystem.recycler
        
        # 存在するプロバイダーの数をカウント
        active_providers_count = len(provider_instances)
        logger.debug(f"Active providers count: {active_providers_count}")
        
        old_prices = {}
        new_prices = {}

        for i in range(self.max_iter):
        
            # 存在するプロバイダーに対して処理を実行
            for provider_name, instance in provider_instances.items():
                if instance:
                    # 現在の価格を保存
                    old_prices[provider_name] = instance.price
                    
                    # 最適価格と利益を計算
                    best_price, best_profit = self.best_response(ecosystem, year, provider_name)

                    # 価格を更新
                    instance.set_price(best_price)
                    
                    # 新しい価格を計算
                    if best_profit is None or best_profit <= 0:
                        new_prices[provider_name] = float('inf')
                    else:
                        new_prices[provider_name] = self.damping * best_price + (1 - self.damping) * old_prices[provider_name]

            # 収束判定
            dist = 0
            for provider_name, instance in provider_instances.items():
                if instance:
                    if new_prices[provider_name] != float('inf') and old_prices[provider_name] != float('inf'):
                        dist += (new_prices[provider_name] - old_prices[provider_name])**2
            dist = dist**(1/active_providers_count)
            print(f"year: {year}, dist: {dist}")

            if dist < self.tol:
                return new_prices

            logger.warning("警告: 収束しませんでした。最終値を返します。")
        return new_prices
                    
    def best_response(self, ecosystem: CircularEcosystem, year: int, provider: str) -> float:
        """
        各プロバイダーの最適価格を計算
        """
        res = minimize_scalar(
        lambda price: -self.calculate_profit(ecosystem, year, provider, price) + price * 0.01,
        bounds=(self.price_min, self.price_max),
        method='Bounded'
        )
        best_price = res.x
        best_profit = -res.fun
        logger.debug(f"for {provider}, best_price: {best_price}, best_profit: {best_profit}")

        return best_price, best_profit

    
    def calculate_profit(self, ecosystem: CircularEcosystem, year: int, provider: str, price: float) -> float:
        """
        各プロバイダーの利潤を計算
        """
        ecosystem_copy = copy.deepcopy(ecosystem)
        # インスタンスの参照を正しく更新
        if provider == 'manufacturer':
            ecosystem_copy.manufacturer.set_price(price)
        elif provider == 'paas_provider':
            ecosystem_copy.paas_provider.set_price(price)
        elif provider == 'reuse_provider':
            ecosystem_copy.reuse_provider.set_price(price)
        elif provider == 'remanufacturer':
            ecosystem_copy.remanufacturer.set_price(price)
        elif provider == 'recycler':
            ecosystem_copy.recycler.set_price(price)
                    
        result_df = ecosystem_copy.execute_yearly_cycle(year)
        result = result_df.iloc[-1]

        print(f"{provider} price: {int(price)}, revenue: {int(result['revenue_history'][provider])}, profit: {int(result['revenue_history'][provider]-result['product_cost_history'][provider]-result['repair_cost_history'][provider])}")

        return result['revenue_history'][provider]-result['product_cost_history'][provider]-result['repair_cost_history'][provider]

        
        