from circular_ecosystem import CircularEcosystem, CircularEcosystemType, create_circular_ecosystem
from stakeholders.provider import Provider
from scipy.optimize import minimize_scalar
import logging
import copy
import os
from itertools import product
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from copy import deepcopy


logger = logging.getLogger(__name__)    


# ----------------------  helper for multiprocessing  ----------------------
def _equilibrium_worker(args):
    """
    参数是一个 tuple：
        (config_dict, provider_names, price_combo, year,
         price_min, price_max, grid_step)
    返回:
        dict(provider -> price)  如果 price_combo 是局部均衡
        None                     否则
    """
    (cfg, names, combo, year,
     price_min, price_max, grid_step) = args

    # ---- 下面是把原来的 _is_local_equilibrium 复制/裁剪过来 ----
    ce = build_ecosystem(cfg, year)
    for n, p in zip(names, combo):
        getattr(ce, n).set_price(p)
    base_res = ce.execute_yearly_cycle(year).iloc[-1]

    # ----------- 初筛：盈利>0 & 价格>平均成本 ------------
    for n, p in zip(names, combo):
        rev   = base_res['revenue_history'][n]
        pcost = base_res['product_cost_history'][n]
        rcost = base_res['repair_cost_history'][n]
        profit    = rev - pcost - rcost
        avg_cost  = pcost / max(base_res.get('sales_volume', {}).get(n, 1), 1)
        if profit <= 0 or p <= avg_cost:
            return None
    base_profit = {n: base_res['revenue_history'][n] -
                      base_res['product_cost_history'][n] -
                      base_res['repair_cost_history'][n]
                   for n in names}

    # ----------- 局部扰动检查 ------------
    for idx, n in enumerate(names):
        for delta in (grid_step, -grid_step):
            np = combo[idx] + delta
            if not (price_min <= np <= price_max):
                continue
            new_combo      = list(combo); new_combo[idx] = np
            ce_nei         = build_ecosystem(cfg, year)
            for nn, pp in zip(names, new_combo):
                getattr(ce_nei, nn).set_price(pp)
            nei_res        = ce_nei.execute_yearly_cycle(year).iloc[-1]
            nei_profit     = (nei_res['revenue_history'][n] -
                              nei_res['product_cost_history'][n] -
                              nei_res['repair_cost_history'][n])
            nei_avg_cost   = (nei_res['product_cost_history'][n] /
                              max(nei_res.get('sales_volume', {}).get(n, 1), 1))
            if nei_profit > base_profit[n] and nei_profit > 0 and np > nei_avg_cost:
                return None  # 可改进，不是局部峰
    # ------------------ 是局部均衡 ------------------
    return dict(zip(names, combo))



class Game:
    def __init__(self):
        self.price_min = 2
        self.price_max = 200
        self.damping = 0.5
        self.tol = 5
        self.max_iter = 100

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

        
def build_ecosystem(config_dict, year):
    """在当前进程重新构建一个全新的 CircularEcosystem。"""
    ce = create_circular_ecosystem(CircularEcosystemType[config_dict["entity"].upper()])
    ce.initialize(
        name=config_dict["name"],
        entity=config_dict["entity"],
        group=config_dict["group"],
        consumer_attributes=config_dict["consumer_attributes"],
        product_attributes=config_dict["product_attributes"],
        num_of_simulation=config_dict["num_of_simulation"],
        ecosystem_settings=config_dict["ecosystem_settings"],
        policy_settings=config_dict["policy_settings"],
        business_model_settings=config_dict["business_model_settings"],
    )
    return ce


class GameWithFullGridLocalPeak:
    """单线程（调试版）Grid‑search 局部峰值均衡搜索器。"""

    def __init__(self, price_min: int = 2, price_max: int =100, grid_step: int = 2,
                 max_combinations: int = 50000):
        self.price_min = price_min
        self.price_max = price_max
        self.grid_step = grid_step
        self.max_combinations = max_combinations

    # ---------------------------------------------------------------------
    # public API
    # ---------------------------------------------------------------------
    def find_equilibrium(self, ecosystem, year: int):
        provider_names = self._get_provider_names(ecosystem)
        if not provider_names:
            logger.warning("No providers found in the ecosystem.")
            return []

        combinations = self._generate_grid(len(provider_names))
        logger.info(f"[Single‑thread] Evaluating {len(combinations)} price combinations…")

        config_dict = self._serialize_ecosystem(ecosystem)
        # equilibria: list[dict[str, float]] = []

        # for comb in tqdm(combinations):
        #     if self._is_local_equilibrium(config_dict, provider_names, comb, year):
        #         equilibria.append(dict(zip(provider_names, comb)))

        equilibria: list[dict[str, float]] = []

        # ----------- 组装任务参数 -------------
        tasks = (
            (config_dict, provider_names, comb, year,
            self.price_min, self.price_max, self.grid_step)
            for comb in combinations
        )

        # ----------- 多进程 Map -------------
        #n_workers = os.cpu_count() or 1
        n_workers = 15
        with ProcessPoolExecutor(max_workers=n_workers) as ex:
            # 返回值按提交顺序；用 tqdm 包一层进度条
            for res in tqdm(ex.map(_equilibrium_worker, tasks),
                            total=len(combinations),
                            desc=f"Year {year} grid"):
                if res:          # 只有局部均衡时 _equilibrium_worker 才会返回 dict
                    equilibria.append(res)
# ② 改成普通 for-loop（保持 tqdm 进度条）
        # for res in tqdm(map(_equilibrium_worker, tasks),
        #                 total=len(combinations),
        #                 desc=f"Year {year} grid"):
        #     if res:                       # 只有局部均衡时 _equilibrium_worker 才会返回 dict
        #         equilibria.append(res)

        # if not equilibria:
        #     logger.warning(f"Year {year}: No local equilibrium found.")
        # else:
        #     logger.info(f"Year {year}: Found {len(equilibria)} local equilibria. Equilibria = {equilibria}")
        # return equilibria

    # ------------------------------------------------------------------
    # core checking logic (single‑thread)
    # ------------------------------------------------------------------
    def _is_local_equilibrium(self, config_dict, provider_names, price_combo, year):
        ce = build_ecosystem(config_dict, year)
        for n, p in zip(provider_names, price_combo):
            getattr(ce, n).set_price(p)
        base_res = ce.execute_yearly_cycle(year).iloc[-1]

        # --- 初筛: 利润>0 & 价格>成本 ---
        for n, p in zip(provider_names, price_combo):
            rev = base_res['revenue_history'][n]
            pcost = base_res['product_cost_history'][n]
            rcost = base_res['repair_cost_history'][n]
            profit = rev - pcost - rcost
            avg_cost = pcost / max(base_res.get('sales_volume', {}).get(n, 1), 1)
            if profit <= 0 or p <= avg_cost:
                return False
        base_profit = {n: base_res['revenue_history'][n] - base_res['product_cost_history'][n] - base_res['repair_cost_history'][n] for n in provider_names}

        # --- 局部扰动检查 ---
        for idx, n in enumerate(provider_names):
            for delta in (self.grid_step, -self.grid_step):
                np = price_combo[idx] + delta
                if not (self.price_min <= np <= self.price_max):
                    continue
                new_combo = list(price_combo)
                new_combo[idx] = np
                ce_nei = build_ecosystem(config_dict, year)
                for nn, pp in zip(provider_names, new_combo):
                    getattr(ce_nei, nn).set_price(pp)
                nei_res = ce_nei.execute_yearly_cycle(year).iloc[-1]
                nei_profit = nei_res['revenue_history'][n] - nei_res['product_cost_history'][n] - nei_res['repair_cost_history'][n]
                nei_avg_cost = nei_res['product_cost_history'][n] / max(nei_res.get('sales_volume', {}).get(n, 1), 1)
                if nei_profit > base_profit[n] and nei_profit > 0 and np > nei_avg_cost:
                    return False  # 可改进，不是局部峰
        return True

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _get_provider_names(self, ecosystem):
        return [n for n in [
            'manufacturer', 'paas_provider', 'reuse_provider', 'remanufacturer', 'recycler'
        ] if getattr(ecosystem, n, None) is not None]

    def _generate_grid(self, n):
        grid = list(range(self.price_min, self.price_max + 1, self.grid_step))
        combos = list(product(grid, repeat=n))
        if len(combos) > self.max_combinations:
            import random
            random.shuffle(combos)
            combos = combos[:self.max_combinations]
        return combos

    def _serialize_ecosystem(self, ecosystem):
        """Extract pickle‑safe config; ensure business_model_settings is present."""
        # --- reconstruct business_model_settings ---
        if ecosystem.business_model is not None:
            cls_name = ecosystem.business_model.__class__.__name__.upper()
            if "REVENUESHARING" in cls_name:
                bm_type = "REVENUESHARING"
            else:
                bm_type = "STANDARD"
            bm_settings = {
                "business_model_type": bm_type,
                "attributes": deepcopy(getattr(ecosystem.business_model, "attributes", {})),
            }
        else:
            bm_settings = {
                "business_model_type": "STANDARD",
                "attributes": {},
            }

        return {
            "name": ecosystem.name,
            "entity": ecosystem.entity,
            "group": ecosystem.group,
            "consumer_attributes": deepcopy(ecosystem.consumer_attributes),
            "product_attributes": deepcopy(ecosystem.product_attributes),
            "num_of_simulation": ecosystem.num_of_simulation,
            "ecosystem_settings": deepcopy(ecosystem.ecosystem_settings),
            "policy_settings": deepcopy(getattr(ecosystem, "policy_settings", {})),
            "business_model_settings": bm_settings,
        }
