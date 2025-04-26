import sys
import json
import random
import pandas as pd
from config.config import Config
from circular_ecosystem import CircularEcosystemType, create_circular_ecosystem
from pathlib import Path
from logger import logger
from visualization import Visualizer
import glob
import logging
import copy
from game import Game
import numpy as np

def main(config_dir: str = "config") -> None:
    """
    メイン実行関数
    
    Args:
        config_dir (str): 設定ファイルが格納されているディレクトリのパス
                         （例: "config/scenario1"）
    """
    config_path = Path(config_dir)
    
    # ディレクトリの存在確認
    if not config_path.exists():
        logger.error(f"Config directory not found: {config_path}")
        return
    
    if not config_path.is_dir():
        logger.error(f"Specified path is not a directory: {config_path}")
        return
    
    # 設定ファイルの一覧を取得
    config_files = list(config_path.glob("*.json"))
    logger.info(f"Found {len(config_files)} config files in {config_path}")
    
    if not config_files:
        logger.error(f"No JSON files found in {config_path}")
        return
    
    # 設定ファイルの一覧をログ出力
    for config_file in config_files:
        logger.debug(f"Found config file: {config_file}")
    
    # 結果保存用ディレクトリの作成
    result_dir = Path("results")
    result_dir.mkdir(parents=True, exist_ok=True)
    
    # 全結果を保持する辞書
    all_results = {}
    
    # 各設定ファイルに対してシミュレーションを実行
    for config_file in config_files:
        # ファイル名から拡張子を除去
        setting_name = Path(config_file).stem
        logging.info(f"Processing {setting_name}")
        
        try:
            # run_simulations関数を実行
            result = run_simulations(config_path, setting_name)
            all_results[setting_name] = result
            logging.info(f"Completed simulation for {setting_name}")
        except Exception as e:
            logging.error(f"Error processing {setting_name}: {str(e)}")
            continue
    
    # 全結果の可視化
    visualizer = Visualizer(result_dir)
    revenue_histories_all = [result['revenue_histories'] for result in all_results.values()]
    visualizer.plot_business_metrics_all(revenue_histories_all)
    
def run_simulations(config_path: Path, setting_name: str) -> pd.DataFrame:
    """
    指定されたディレクトリ内の全ての設定ファイルに対してシミュレーションを実行
    
    Args:
        setting_name: 設定ファイル名
    """

    # 再現性のための乱数シード設定
    random.seed(1)
    np.random.seed(1)

    # 設定ファイルの読み込み
    with open(config_path / f"{setting_name}.json") as f:
        setting_json = json.load(f)
    config = Config(**setting_json)
    
    # 結果保存用ディレクトリの作成
    result_dir = Path("results") / setting_name
    result_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    for run_id in range(config.num_of_run):
        # サーキュラーエコシステムの作成
        ecosystem_type = CircularEcosystemType[config.entity.upper()]
        ce = create_circular_ecosystem(ecosystem_type)

        # 設定の初期化
        ce.initialize(
            name=config.name,
            entity=config.entity,
            group=config.group,
            consumer_attributes=config.consumer_attributes,
            product_attributes=config.product_attributes,
            num_of_simulation=config.num_of_simulation,
            ecosystem_settings=config.ecosystem_settings,
            policy_settings=config.policy_settings,
            business_model_settings=config.business_model_settings
        )

        # ゲームインスタンスの作成
        game = Game()
        
        # シミュレーション実行
        results_per_run = []
        
        for year in range(config.num_of_simulation):

            # CEインスタンスをコピー
            ce_copy = copy.deepcopy(ce)
            # 均衡解の探索
            equilibrium = game.find_equilibrium(ce_copy, year)
            # 均衡価格の設定
            ce.set_equilibrium_prices(equilibrium)
            # シミュレーション実行
            result = ce.execute_yearly_cycle(year)
            results_per_run.append(result)
            
        result = pd.concat(results_per_run, ignore_index=True)
        if result is not None:  # Noneチェックを追加
            results.append(result)    
    
    revenue_histories = [result['revenue_history'] for result in results]
    product_cost_histories = [result['product_cost_history'] for result in results]
    repair_cost_histories = [result['repair_cost_history'] for result in results]
    matches_histories = [result['matches_history'] for result in results]
    material_flow_histories = [result['material_flow_history'] for result in results]
    financial_flow_histories = [result['financial_flow_history'] for result in results]
    logger.debug(f"revenue_histories: {revenue_histories}")

    # 各履歴データを辞書として収集
    simulation_results = {
        'revenue_histories': revenue_histories,
        'product_cost_histories': product_cost_histories,
        'repair_cost_histories': repair_cost_histories,
        'matches_histories': matches_histories,
        'material_flow_histories': material_flow_histories,
        'financial_flow_histories': financial_flow_histories
    }
    
    # 可視化
    visualizer = Visualizer(result_dir)

    # ビジネス指標のグラフを作成    
    visualizer.plot_business_metrics(
        revenue_histories,
        product_cost_histories,
        repair_cost_histories,
    )
    # マッチングのグラフを作成
    visualizer.plot_matches_percentage(matches_histories)
    # マテリアフローのグラフを作成
    visualizer.plot_material_flow(material_flow_histories)
    # 財務フローのグラフを作成
    visualizer.plot_financial_flow(financial_flow_histories)

    # 結果の保存
    if not results:
        raise ValueError("No simulation results were generated")
    
    df = pd.concat(results, ignore_index=True)
    output_file = f"{config.name}_{config.entity}_{config.group}.csv"
    output_path = result_dir / output_file
    df.to_csv(output_path, index=False)
    logger.info(f"Results saved to {output_path}")

    return simulation_results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if len(sys.argv) > 1:
        # コマンドライン引数がある場合はそのディレクトリを使用
        main(sys.argv[1])
    else:
        # 引数がない場合はデフォルトのconfigディレクトリを使用
        main()