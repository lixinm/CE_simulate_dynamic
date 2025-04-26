from enum import Enum
from typing import Dict, List
from dataclasses import dataclass

class PolicyType(Enum):
    """制度の種類"""
    CARBON_TAX = "carbon_tax"          # 炭素税
    SUBSIDY = "subsidy"                # 補助金
    DEPOSIT = "deposit"                # デポジット制度
    EPR = "epr"                        # 拡大生産者責任
    RIGHT_TO_REPAIR = "right_to_repair"  # 修理する権利

@dataclass
class PolicyParameter:
    """制度のパラメータ"""
    carbon_tax_rate: float = 0.0       # 炭素税率
    subsidy_rate: float = 0.0          # 補助金率
    deposit_amount: float = 0.0        # デポジット金額
    epr_fee: float = 0.0              # EPR費用
    repair_cost_reduction: float = 0.0  # 修理コスト削減率

class Policy:
    """制度設計クラス"""
    
    def __init__(self, parameters: PolicyParameter):
        self.parameters = parameters
