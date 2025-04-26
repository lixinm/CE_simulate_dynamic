import os
import json
from itertools import product

# 元のJSONデータ
base_json = {
    "name": "simulation",
    "entity": "revenue_share",
    "group": "test",
    "num_of_simulation": 10,
    "num_of_run": 10,
    "consumer_attributes": {
        "A": {
            "plan_of_use_shape": 1.644,
            "plan_of_use_scale": 6.618,
            "num_of_players": 10,
            "churn_rate": 0.0,
            "reuse_probability": 0.0,
            "num_of_products_mean": 1.0,
            "num_of_products_sd": 0.0,
            "pref_dict": {
                "ownership_part_worth_mean": 0.0,
                "ownership_part_worth_sd": 0.0,
                "subscription_part_worth_mean": .55,
                "subscription_part_worth_sd": 3.2,
                "reuse_part_worth_mean": 0.0,
                "reuse_part_worth_sd": 0.0,
                "remanufacture_part_worth_mean": 0.0,
                "remanufacture_part_worth_sd": 0.0,
                "price_part_worth_mean": 8.2,
                "price_part_worth_sd": 3.0,
                "spec_part_worth_mean": 0.0,
                "spec_part_worth_sd": 0.0,
                "size_part_worth_mean": 0.0,
                "size_part_worth_sd": 0.0
            }
        }
    },
    "product_attributes": {
        "p": {
            "size": 10.0,
            "price": 20.0,
            "base_of_new_products": 3.0,
            "base_price": 30.0,
            "price_discout_rate_by_generation": 0.1,
            "lifetime": 10.0,
            "base_production_cost": 16.0,
            "production_cost_discout_rate_by_generation": 0.1,
            "transport_cost": 4.0,
            "refurbish_cost": 1.0,
            "repair_cost": 1.0,
            "disporsal_cost": 1.0,
            "production_co2": 408.0,
            "transport_co2": 3.0,
            "use_co2": 178.0,
            "refurbish_co2": 2.0,
            "disporsal_co2": 49.0,
            "weibull_alpha": 1.81,
            "weibull_beta": 25.8,
            "repairable_year": 2.0,
            "price_dict": {
                "10": 0.5,
                "5": 0.8
            }
        }
    },
    "ecosystem_settings": {
        "paas_provider": {
            "type": "STANDARD",
            "attributes": {
                "base_price": 1.0,
                "production_volume": 2,
                "procurement_cost": 2.0,
                "repair_cost": 0.01,
                "base_production_volume": 0
            }
        },
        "manufacturer": {
            "type": "STANDARD",
            "attributes": {
                "base_price": 2.0,
                "production_volume": 8,
                "production_cost": 1.6,
                "repair_cost": 0.01,
                "base_production_volume": 0
            }
        }
    },
    "policy_settings": {
        "carbon_tax_rate": 0.1,
        "subsidy_rate": 0.2,
        "deposit_amount": 1000.0,
        "epr_fee": 500.0,
        "repair_cost_reduction": 0.3
    },
    "business_model_settings": {
        "business_model_type": "standard",
        "attributes": {
            "revenue_share": 0.0
        }
    }
}

# パラメータ設定
paas_base_prices = [0.8, 0.9, 1.0, 1.1, 1.2]
manufacturer_base_prices = [1.8, 1.9, 2.0, 2.1, 2.2]
paas_procurement_costs = [2.0]
revenue_shares = [0.0]

# 出力先ディレクトリ
output_dir = 'config/revenue_share'
os.makedirs(output_dir, exist_ok=True)

# 組み合わせを生成してファイルを書き出し
for paas_price, manu_price, procurement_cost, rev_share in product(paas_base_prices, manufacturer_base_prices, paas_procurement_costs, revenue_shares):
    config = json.loads(json.dumps(base_json))  # ディープコピー
    config['ecosystem_settings']['paas_provider']['attributes']['base_price'] = paas_price
    config['ecosystem_settings']['manufacturer']['attributes']['base_price'] = manu_price
    config['ecosystem_settings']['paas_provider']['attributes']['procurement_cost'] = procurement_cost  # 追加
    config['business_model_settings']['attributes']['revenue_share'] = rev_share

    filename = f"config_paas_{paas_price}_manu_{manu_price}_proc_{procurement_cost}_rev_{rev_share}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        json.dump(config, f, indent=4)

print(f"{len(paas_base_prices) * len(manufacturer_base_prices) * len(paas_procurement_costs) * len(revenue_shares)}個のJSONファイルが{output_dir}に出力されました。")
