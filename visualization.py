import matplotlib.pyplot as plt
from typing import Dict, List
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from logger import logger
import matplotlib as mpl
import japanize_matplotlib  # 日本語フォントのサポートを追加
from pathlib import Path
# フォント関連の警告を抑制
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
from collections import defaultdict
import seaborn as sns

class Visualizer:
    def __init__(self, result_dir: Path):
        self.result_dir = result_dir

    def calculate_statistics(self, histories: list[pd.Series]):
        """
        複数の履歴データから統計データを計算してseaborn用のDataFrameを作成
        
        Args:
            histories: 履歴データのリスト
        
        Returns:
            統計データを含むDataFrame
        """
        # 時間軸とプロバイダーの取得
        time_steps = sorted(histories[0].index)
        providers = histories[0].values[0].keys()
        
        data = []
        for t in time_steps:
            for provider in providers:
                # 全実験からこの時点のこのプロバイダーの値を収集
                values = [history[t][provider] for history in histories]
                
                data.append({
                    'Time Step': t,
                    'Provider': provider,
                    'Value': np.mean(values),
                    'Std': np.std(values),
                    'Lower': np.mean(values) - np.std(values),
                    'Upper': np.mean(values) + np.std(values)
                })
        
        stats_df = pd.DataFrame(data)
        logger.debug(f"stats_df: {stats_df}")
        return stats_df

    def plot_business_metrics(self, revenue_histories: list[pd.Series], 
                            product_cost_histories: list[pd.Series], 
                            repair_cost_histories: list[pd.Series],
                            profit_histories: list[pd.Series]):
        """ビジネス指標の折れ線グラフを作成（seabornを使用）"""
        import seaborn as sns
        
        # 日本語フォントの設定
        plt.rcParams['font.family'] = 'IPAexGothic'
        
        # フォントサイズの設定
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'legend.title_fontsize': 12
        })
        
        # スタイル設定とカラーパレット
        sns.set_style("whitegrid", {
            'font.family': 'IPAexGothic',
            'axes.facecolor': '.95'
        })
        sns.set_palette("bright")
        
        # brightパレットの色を取得
        colors = sns.color_palette("bright")
        
        # プロバイダーごとの色を定義（brightパレットを使用）
        palette = {
            'manufacturer': colors[2],       # 緑
            'paas_provider': colors[0],      # 青
            'reuse_provider': colors[1],     # オレンジ
            'remanufacturer': colors[4],     # 紫
            'recycler': colors[5],           # 茶
        }
        
        # 統計データの計算
        revenue_stats = self.calculate_statistics(revenue_histories)
        product_cost_stats = self.calculate_statistics(product_cost_histories)
        repair_cost_stats = self.calculate_statistics(repair_cost_histories)
        profit_stats = self.calculate_statistics(profit_histories)
        logger.debug(f"revenue_stats: {revenue_stats}")
        
        # 最初の要素から提供者のリストを取得
        providers = revenue_histories[0].values[0].keys()
        num_providers = len(providers)
        
        # プロバイダー名の日本語マッピング
        provider_labels = {
            'manufacturer': '製造業者',
            'paas_provider': 'PaaSプロバイダー',
            'reuse_provider': '再利用業者',
            'remanufacturer': '再製造業者',
            'recycler': 'リサイクル業者'
        }
        
        # メトリクスの日本語マッピング
        metric_labels = {
            'Revenue': '収益',
            'Product Cost': '製品コスト',
            'Repair Cost': '修理コスト',
            'Profit': '利益'
        }
        
        # プロバイダーごとにサブプロット作成
        fig, axes = plt.subplots(4, num_providers, figsize=(5*num_providers, 20))
        
        # 各指標、各プロバイダーについてプロット
        metrics = [
            (revenue_stats, "Revenue"),
            (product_cost_stats, "Product Cost"),
            (repair_cost_stats, "Repair Cost"),
            (profit_stats, "Profit")
        ]
        
        for i, (metric_stats, title) in enumerate(metrics):
            for j, provider in enumerate(providers):
                ax = axes[i, j]
                
                # データの準備
                # プロバイダーでフィルタリング
                provider_data = metric_stats[metric_stats['Provider'] == provider]
                
                data = []
                time_steps = sorted(provider_data['Time Step'].unique())
                for t in time_steps:
                    row = provider_data[provider_data['Time Step'] == t].iloc[0]
                    data.append({
                        'Time Step': t,
                        'Value': row['Value'],
                        'Std': row['Std']
                    })
                
                df = pd.DataFrame(data)
                logger.debug(f"Provider {provider} data:")
                logger.debug(f"Raw metric_stats filtered:\n{provider_data}")
                logger.debug(f"Processed df:\n{df}")
                
                # seabornでプロット
                sns.lineplot(
                    data=df,
                    x='Time Step',
                    y='Value',
                    ax=ax,
                    marker='o',
                    markersize=6,
                    color=palette.get(provider, '#7f7f7f'),
                    label=provider_labels.get(provider, provider)
                )
                
                # 標準偏差の範囲を追加
                ax.fill_between(
                    df['Time Step'],
                    df['Value'] - df['Std'],
                    df['Value'] + df['Std'],
                    alpha=0.2,
                    color=palette.get(provider, '#7f7f7f')
                )
                
                # グラフの装飾（日本語フォント指定）
                if i == 0:
                    ax.set_title(provider_labels.get(provider, provider), fontfamily='IPAexGothic')
                if j == 0:
                    ax.set_ylabel(metric_labels.get(title, title), fontfamily='IPAexGothic')
                ax.set_xlabel('時間ステップ', fontfamily='IPAexGothic')
                
                # グリッドの設定
                ax.grid(True, alpha=0.3)
                
                # 凡例を非表示（最上段のプロバイダー名で代用）
                ax.legend([])
        
        # 全体のタイトル（日本語フォント指定）
        fig.suptitle('ビジネス指標の推移', fontsize=16, y=1.02, fontfamily='IPAexGothic')
        
        # レイアウトの調整
        plt.tight_layout()
        
        # グラフを保存
        plt.savefig(
            self.result_dir / 'business_metrics.png',
            bbox_inches='tight',
            dpi=300
        )
        plt.close()

    def calculate_matches_statistics(self, matches_histories: list[pd.Series]):
        """複数の履歴データから平均値を計算し、パーセンテージに変換"""
        time_steps = sorted(matches_histories[0].index)
        stats = pd.Series([{} for _ in time_steps], index=time_steps)
        
        # 全プロバイダーのリストを取得
        all_providers = set()
        for history in matches_histories:
            for t in time_steps:
                data = history[t]
                providers = data[max(data.keys())].keys()
                all_providers.update(providers)
        
        for t in time_steps:
            provider_sums = {provider: 0.0 for provider in all_providers}  # 全プロバイダーで初期化
            
            for history in matches_histories:
                data = history[t]
                latest_data = data[max(data.keys())]
                for provider in all_providers:
                    provider_sums[provider] += latest_data.get(provider, 0)  # 存在しない場合は0
            
            num_histories = len(matches_histories)
            provider_means = {provider: sum_val / num_histories 
                            for provider, sum_val in provider_sums.items()}
            
            total = sum(provider_means.values())
            if total > 0:
                stats[t] = {provider: (count / total) * 100 
                        for provider, count in provider_means.items()}
            else:
                stats[t] = provider_means
        
        return stats

    def plot_matches_percentage(self, matches_histories: list[pd.Series]):
        """マッチング数のパーセンテージを積み上げ折れ線グラフを表示（seaborn使用）"""
        import seaborn as sns
        
        # 日本語フォントの設定
        plt.rcParams['font.family'] = 'IPAexGothic'
        
        # フォントサイズの設定
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'legend.title_fontsize': 12
        })
        
        # スタイル設定とカラーパレット
        sns.set_style("whitegrid", {
            'font.family': 'IPAexGothic',
            'axes.facecolor': '.95'
        })
        sns.set_palette("bright")
        
        # brightパレットの色を取得
        colors = sns.color_palette("bright")
        
        # 統計データの計算
        stats = self.calculate_matches_statistics(matches_histories)
        
        # データフレームの作成
        data = []
        time_steps = sorted(stats.index)
        providers = list(stats[0].keys())
        
        for t in time_steps:
            for provider in providers:
                data.append({
                    'Time Step': t,
                    'Provider': provider,
                    'Percentage': stats[t][provider]
                })
        
        df = pd.DataFrame(data)
        
        # プロバイダー名を日本語に変換
        provider_mapping = {
            'manufacturer': '製造業者',
            'paas_provider': 'PaaSプロバイダー',
            'reuse_provider': '再利用業者',
            'remanufacturer': '再製造業者',
            'recycler': 'リサイクル業者'
        }
        df['Provider'] = df['Provider'].map(provider_mapping)
        
        # カラーパレットの設定（brightパレットを使用）
        palette = {
            '製造業者': colors[2],        # 緑
            'PaaSプロバイダー': colors[0], # 青
            '再利用業者': colors[1],       # オレンジ
            '再製造業者': colors[4],       # 紫
            'リサイクル業者': colors[5]     # 茶
        }
        
        # グラフの作成
        plt.figure(figsize=(12, 6))
        
        # 積み上げ面グラフの作成
        ax = plt.gca()
        
        # ピボットテーブルの作成
        pivot_df = df.pivot(
            index='Time Step',
            columns='Provider',
            values='Percentage'
        )
        
        # 積み上げ面グラフの描画
        pivot_df.plot(
            kind='area',
            stacked=True,
            alpha=0.3,
            color=palette,
            ax=ax
        )
        
        # 線の追加
        for provider in pivot_df.columns:
            cumsum = pivot_df[provider].copy()
            for other_provider in pivot_df.columns:
                if other_provider != provider:
                    if list(pivot_df.columns).index(other_provider) < list(pivot_df.columns).index(provider):
                        cumsum += pivot_df[other_provider]
            
            plt.plot(
                pivot_df.index,
                cumsum,
                color=palette[provider],
                linewidth=2
            )
        
        # グラフの装飾
        plt.title("プロバイダーのマッチング割合", fontsize=14, pad=15, fontfamily='IPAexGothic')
        plt.xlabel("時間ステップ", fontsize=12, fontfamily='IPAexGothic')
        plt.ylabel("割合 (%)", fontsize=12, fontfamily='IPAexGothic')
        
        # 凡例の設定
        plt.legend(
            title='プロバイダー',
            bbox_to_anchor=(1.05, 1),
            loc='upper left',
            borderaxespad=0.,
            prop={'family': 'IPAexGothic'}
        )
        
        # グリッドの設定
        plt.grid(True, alpha=0.3)
        
        # レイアウトの調整
        plt.tight_layout()
        
        # グラフを保存
        plt.savefig(
            self.result_dir / 'matches_percentage.png',
            bbox_inches='tight',
            dpi=300
        )
        plt.close()

    def plot_material_flow(self, material_flow_histories: list[list[pd.Series]]):
        """
        マテリアルフローの平均値を計算してサンキーダイアグラムを作成
        
        Args:
            material_flow_histories: マテリアルフロー情報を持つSeriesのリストのリスト
        """
        # 全てのフローデータを一つのリストに集約
        all_flows = []
        for history in material_flow_histories:
            for history_annual in history:
                # Seriesをディクショナリのリストとして追加
                if not history_annual.empty:
                    all_flows.extend(history_annual.to_dict('records'))
        
        # リストからDataFrameを作成
        combined_df = pd.DataFrame(all_flows)
        
        # 値が0より大きい行のみを保持
        combined_df = combined_df[combined_df['value'] > 0]
        
        if combined_df.empty:
            logger.debug("Warning: No valid flow data found")
            return
            
        # sourceとtargetでグループ化して合計値を計算
        sum_flow = combined_df.groupby(
            ['source', 'target'],
            as_index=False
        )['value'].sum()

        # 実験回数で割って平均値を計算
        num_experiments = len(material_flow_histories)
        average_flow = sum_flow.copy()
        average_flow['value'] = sum_flow['value'] / num_experiments
        
        # ノードの順序と列の位置を定義
        node_columns = {
            'man': 0,      # 1列目
            'pas': 1,      # 2列目
            'reu': 1,
            'consumer': 2, # 3列目
            'repair': 3,   # 4列目
            'rec': 3,
            'disposal': 4  # 5列目
        }
        
        # 各列内での垂直位置
        node_positions = {
            'man': 0.5,    # 1列目中央
            'pas': 0.3,    # 2列目上部
            'reu': 0.7,    # 2列目下部
            'consumer': 0.5, # 3列目中央
            'repair': 0.3,  # 4列目上部
            'rec': 0.7,     # 4列目下部
            'disposal': 0.5  # 5列目中央
        }
        
        node_colors = {
            'man': '#2ca02c',     # 緑
            'pas': '#1f77b4',     # 青
            'reu': '#ff7f0e',     # オレンジ
            'consumer': '#d62728', # 赤
            'repair': '#9467bd',   # 紫
            'rec': '#8c564b',     # 茶
            'disposal': '#e377c2'  # ピンク
        }
        
        # 半透明の色を生成する関数
        def add_alpha(hex_color, alpha=0.5):
            rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})'
        
        # ノードを順序に従ってソート
        nodes = sorted(list(set(
            average_flow['source'].unique().tolist() + 
            average_flow['target'].unique().tolist()
        )), key=lambda x: (node_columns[x], node_positions[x]))
        
        node_indices = {node: i for i, node in enumerate(nodes)}
        
        source_indices = average_flow['source'].map(node_indices).tolist()
        target_indices = average_flow['target'].map(node_indices).tolist()
        values = average_flow['value'].tolist()
        
        # エッジの色を設定（sourceノードの色を半透明に）
        link_colors = [add_alpha(node_colors[average_flow['source'].iloc[i]]) for i in range(len(values))]
        
        # サンキーダイアグラムの作成
        fig = go.Figure(data=[go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = nodes,
                color = [node_colors[node] for node in nodes],
                x = [node_columns[node] * 0.2 for node in nodes],  # x座標を5列に分ける
                y = [node_positions[node] for node in nodes]       # y座標を指定
            ),
            link = dict(
                source = source_indices,
                target = target_indices,
                value = values,
                color = link_colors
            )
        )])
        
        fig.update_layout(
            title_text=f"マテリアルフロー平均 (n={num_experiments})",
            font_size=10,
            height=600
        )
            
        fig.write_html(self.result_dir / "average_material_flow_sankey.html")

    def plot_financial_flow(self, financial_flow_histories: list[list[pd.Series]]):
        """
        財務フローの平均値を計算してサンキーダイアグラムを作成
        
        Args:
            financial_flow_histories: 財務フロー情報を持つSeriesのリストのリスト
        """
        # 全てのフローデータを一つのリストに集約
        all_flows = []
        for history in financial_flow_histories:
            for history_annual in history:
                # Seriesをディクショナリのリストとして追加
                if not history_annual.empty:
                    all_flows.extend(history_annual.to_dict('records'))
        
        # リストからDataFrameを作成
        combined_df = pd.DataFrame(all_flows)
        
        # 値が0より大きい行のみを保持
        combined_df = combined_df[combined_df['value'] > 0]
        
        if combined_df.empty:
            logger.debug("Warning: No valid flow data found")
            return
            
        # sourceとtargetでグループ化して合計値を計算
        sum_flow = combined_df.groupby(
            ['source', 'target'],
            as_index=False
        )['value'].sum()

        # 実験回数で割って平均値を計算
        num_experiments = len(financial_flow_histories)
        average_flow = sum_flow.copy()
        average_flow['value'] = sum_flow['value'] / num_experiments
        
        # ノードの順序と列の位置を定義
        node_columns = {
            'consumer': 0,          # 1列目
            'paas_provider': 1,     # 2列目
            'manufacturer': 2,      # 3列目
            'reuse_provider': 3,    # 4列目
            'recycler': 4,          # 5列目
            'disposal': 5           # 6列目
        }
        
        # 各列内での垂直位置
        node_positions = {
            'consumer': 0.5,        # 1列目中央
            'paas_provider': 0.5,   # 2列目中央
            'manufacturer': 0.5,    # 3列目中央
            'reuse_provider': 0.5,  # 4列目中央
            'recycler': 0.3,        # 5列目上部
            'disposal': 0.7         # 5列目下部
        }
        
        node_colors = {
            'consumer': '#2ca02c',     # 緑
            'paas_provider': '#1f77b4',     # 青
            'manufacturer': '#ff7f0e',     # オレンジ
            'reuse_provider': '#d62728', # 赤
            'recycler': '#9467bd',   # 紫
            'disposal': '#8c564b'  # 茶
        }
        
        # 半透明の色を生成する関数
        def add_alpha(hex_color, alpha=0.5):
            rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})'
        
        # ノードを順序に従ってソート
        nodes = sorted(list(set(
            average_flow['source'].unique().tolist() + 
            average_flow['target'].unique().tolist()
        )), key=lambda x: (node_columns[x], node_positions[x]))
        
        node_indices = {node: i for i, node in enumerate(nodes)}
        
        source_indices = average_flow['source'].map(node_indices).tolist()
        target_indices = average_flow['target'].map(node_indices).tolist()
        values = average_flow['value'].tolist()
        
        # エッジの色を設定（sourceノードの色を半透明に）
        link_colors = [add_alpha(node_colors[average_flow['source'].iloc[i]]) for i in range(len(values))]
        
        # サンキーダイアグラムの作成
        fig = go.Figure(data=[go.Sankey(
            node = dict(
                pad = 15,
                thickness = 20,
                line = dict(color = "black", width = 0.5),
                label = nodes,
                color = [node_colors[node] for node in nodes],
                x = [node_columns[node] * 0.2 for node in nodes],  # x座標を5列に分ける
                y = [node_positions[node] for node in nodes]       # y座標を指定
            ),
            link = dict(
                source = source_indices,
                target = target_indices,
                value = values,
                color = link_colors
            )
        )])
        
        fig.update_layout(
            title_text=f"財務フロー平均 (n={num_experiments})",
            font_size=10,
            height=600
        )
            
        fig.write_html(self.result_dir / "average_financial_flow_sankey.html")
    
    def plot_business_metrics_all(self, histories_all: list[list[pd.Series]], config_files: list[Path]):
        """
        全設定のビジネスメトリクスを可視化
        
        Args:
            revenue_histories_all: 全設定の収益履歴データのリスト
                [
                    [pd.Series(...), pd.Series(...), ...],  # setting1の実験結果
                    [pd.Series(...), pd.Series(...), ...],  # setting2の実験結果
                    ...
                ]
        """
        # 設定ごとのプロバイダー別平均収益を計算
        setting_averages = []
        
        for setting_histories in histories_all:
            # プロバイダーごとの時系列データを収集
            provider_timeseries = defaultdict(lambda: defaultdict(list))
            
            # 各実験、各タイムステップのデータを収集
            for experiment in setting_histories:
                for timestep, revenues in experiment.items():
                    for provider, value in revenues.items():
                        provider_timeseries[provider][timestep].append(value)
            
            # 各プロバイダーの全期間平均を計算
            provider_averages = {
                provider: np.mean([
                    np.mean(values) for values in timeseries.values()
                ])
                for provider, timeseries in provider_timeseries.items()
            }
            
            setting_averages.append(provider_averages)
        
        # 利益の比較
        self.plot_profit_comparison(setting_averages, config_files)
        
        # グラフの作成
        plt.figure(figsize=(12, 6))
        
        # プロバイダーごとに折れ線グラフを作成
        providers = list(setting_averages[0].keys())
        settings = [Path(config_file).stem for config_file in config_files]
        
        for provider in providers:
            values = [avg[provider] for avg in setting_averages]
            plt.plot(settings, values, marker='o', label=provider)
        
        plt.title('Average Revenue by Provider Across Settings')
        plt.xlabel('Setting')
        plt.ylabel('Average Revenue')
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        
        # 保存
        plt.savefig(self.result_dir / "business_metrics_comparison.png", bbox_inches='tight')
        plt.close()

    def plot_profit_comparison(self, setting_averages: List[Dict[str, pd.Series]], config_files: list[Path]) -> None:
        """PaaSプロバイダーとメーカーの平均利益を散布図でプロット"""
        plt.figure(figsize=(10, 8))
        
        # 基準となる設定の値を取得
        base_config_name = "config_paas_1.0_manu_2.0_proc_2.0_rev_0.0"
        base_averages = None
        for averages, config_file in zip(setting_averages, config_files):
            if config_file.stem == base_config_name:
                base_averages = averages
                break
        
        if base_averages is None:
            raise ValueError(f"基準となる設定 {base_config_name} が見つかりません")
            
        base_paas = base_averages['paas_provider']
        base_manufacturer = base_averages['manufacturer']
        
        # revとprocurement costの値でグループ化
        groups = {}
        
        # まず、すべてのrev値とproc値を収集して、ユニークな値の数を把握
        rev_values = set()
        proc_values = set()
        for _, config_file in zip(setting_averages, config_files):
            parts = config_file.stem.split('_')
            rev_values.add(float(parts[-1]))
            proc_values.add(float(parts[-3]))
        
        # オレンジ、青、緑のカラーパレット
        colors = [
            sns.color_palette("bright")[1],  # オレンジ
            sns.color_palette("bright")[0],  # 青
            sns.color_palette("bright")[2],  # 緑
            sns.color_palette("bright")[3],  # 紫
            sns.color_palette("bright")[4],  # ピンク
        ]
        
        # 値をソートしてインデックスを割り当て
        rev_to_idx = {val: i for i, val in enumerate(sorted(rev_values))}
        proc_to_idx = {val: i for i, val in enumerate(sorted(proc_values))}
        
        # グループ化
        for averages, config_file in zip(setting_averages, config_files):
            parts = config_file.stem.split('_')
            rev_value = float(parts[-1])
            proc_value = float(parts[-3])
            
            key = (rev_value, proc_value)
            if key not in groups:
                groups[key] = []
            groups[key].append((averages, config_file))
        
        # プロット
        legend_added = set()
        for ((rev_value, proc_value), group) in sorted(groups.items()):
            # 組み合わせごとに色を割り当て
            color_idx = rev_to_idx[rev_value] * len(proc_values) + proc_to_idx[proc_value]
            color = colors[color_idx % len(colors)]  #  色の数を超えないように修正
            
            for averages, config_file in group:
                paas_profit = averages['paas_provider']
                manufacturer_profit = averages['manufacturer']
                
                key = (rev_value, proc_value)
                label = f'rev_{rev_value}, proc_{proc_value}' if key not in legend_added else None
                legend_added.add(key)
                
                plt.scatter(
                    paas_profit,
                    manufacturer_profit,
                    alpha=0.8,
                    color=color,
                    label=label,
                    s=100
                )
        
        # 参考線を追加
        plt.axhline(y=base_manufacturer, color='r', linestyle='--', alpha=0.3, label='Benchmark')
        plt.axvline(x=base_paas, color='r', linestyle='--', alpha=0.3,)
        
        plt.xlabel('PaaS Provider Profit')
        plt.ylabel('Manufacturer Profit')
        plt.title('Average Profit Comparison: PaaS Provider vs Manufacturer')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.axis('equal')
        
        plt.tight_layout()
        plt.savefig(self.result_dir / "average_profit_comparison.png")
        plt.close()

        
