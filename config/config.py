from typing import Dict, Union, Any
from dataclasses import dataclass

@dataclass
class Config:
    name: str
    entity: str
    group: str
    num_of_simulation: int
    num_of_run: int
    consumer_attributes: Dict[str, Dict]
    product_attributes: Dict[str, Union[str, float, Dict]]
    ecosystem_settings: Dict[str, Dict[str, Union[str, Dict[str, Union[str, float]]]]]
    policy_settings: Dict[str, float]
    business_model_settings: Dict[str, Dict]