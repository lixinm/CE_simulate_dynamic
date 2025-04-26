from typing import Dict, Any, Type, TYPE_CHECKING
import logging
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from enablers.product import Product, StandardProduct
    from enablers.product import ProductType

def create_product(product_type: 'ProductType', attributes: Dict[str, Any]) -> 'Product':
    """
    製品クラスのファクトリー関数
    
    Args:
        product_type: 製品タイプ（ProductType列挙型）
        attributes: 製品の属性
        
    Returns:
        Product: 生成された製品インスタンス
    """
    # 実行時にインポート
    from enablers.product import Product, ProductType, StandardProduct
    
    # 製品タイプと対応するクラスのマッピング
    product_map = {
        ProductType.STANDARD: StandardProduct,
    }
    
    if product_type not in product_map:
        raise ValueError(f"Unsupported product type: {product_type}. Available types: {list(product_map.keys())}")
    
    try:
        # 製品インスタンスの生成
        product_class = product_map[product_type]
        product = product_class(attributes)
        logger.debug(f"Creating product {attributes['name']}")
        return product
        
    except Exception as e:
        logger.error(f"Failed to create product of type {product_type}")
        logger.error(f"Attributes: {attributes}")
        logger.error(f"Error: {str(e)}")
        raise