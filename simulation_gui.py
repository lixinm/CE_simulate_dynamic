import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json, os, glob
import numpy as np

class SimulationGUI(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = tk.Tk()
        super().__init__(master)
        self.master = master
        self.master.title("Circular Economy Simulation")
        self.master.geometry("800x600")
        
        self.current_config = None
        
        # メインフレームの作成
        self.create_widgets()
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_widgets(self):
        """GUIウィジェットの作成"""
        # ノートブック（タブ）の作成
        self.notebook = ttk.Notebook(self)
        
        # シミュレーション実行タブ
        sim_frame = ttk.Frame(self.notebook)
        self.notebook.add(sim_frame, text="シミュレーション実行")
        self.create_simulation_tab(sim_frame)
        
        # 設定エディタタブ
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="設定エディタ")
        self.create_config_tab(config_frame)
        
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
    def create_simulation_tab(self, parent):
        """シミュレーション実行タブの作成"""
        # 設定ファイル選択部分
        file_frame = ttk.LabelFrame(parent, text="設定ファイル", padding=5)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(
            file_frame, 
            textvariable=self.file_path_var, 
            width=50,
            state='readonly'
        )
        self.file_path_entry.pack(side=tk.LEFT, padx=5)
        
        select_button = ttk.Button(
            file_frame,
            text="参照...",
            command=self.select_config
        )
        select_button.pack(side=tk.LEFT, padx=5)
        
        # 設定内容表示部分
        content_frame = ttk.LabelFrame(parent, text="設定内容", padding=5)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.content_text = tk.Text(content_frame, height=15, width=60)
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.content_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        
        # 実行ボタン
        run_button = ttk.Button(
            parent,
            text="シミュレーション実行",
            command=self.run_simulation,
            style='Run.TButton'
        )
        run_button.pack(pady=10)
        
        # ボタンのスタイル設定
        style = ttk.Style()
        style.configure('Run.TButton', font=('Helvetica', 10, 'bold'))
        
    def create_config_tab(self, parent):
        """設定エディタタブの作成"""
        # 設定エディタ用のノートブック（タブ）の作成
        config_notebook = ttk.Notebook(parent)
        config_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本設定タブ
        basic_frame = ttk.Frame(config_notebook)
        config_notebook.add(basic_frame, text="Basic Settings")
        self.create_basic_settings(basic_frame)
        
        # 消費者設定タブ
        consumer_frame = ttk.Frame(config_notebook)
        config_notebook.add(consumer_frame, text="Consumer Settings")
        self.create_consumer_settings(consumer_frame)
        
        # 製品設定タブ
        product_frame = ttk.Frame(config_notebook)
        config_notebook.add(product_frame, text="Product Settings")
        self.create_product_settings(product_frame)
        
        # エコシステム設定タブ
        ecosystem_frame = ttk.Frame(config_notebook)
        config_notebook.add(ecosystem_frame, text="Ecosystem Settings")
        self.create_ecosystem_settings(ecosystem_frame)
        
        # ポリシー設定タブ
        policy_frame = ttk.Frame(config_notebook)
        config_notebook.add(policy_frame, text="Policy Settings")
        self.create_policy_settings(policy_frame)
        
        # ビジネスモデル設定タブ
        business_model_frame = ttk.Frame(config_notebook)
        config_notebook.add(business_model_frame, text="Business Model Settings")
        self.create_business_model_settings(business_model_frame)
        
        # 保存ボタン
        save_button = ttk.Button(parent, text="設定を保存", command=self.save_config)
        save_button.pack(pady=10)
    
    def create_basic_settings(self, parent):
        """基本設定の入力フィールドを作成"""
        # 基本設定のフレーム
        settings_frame = ttk.LabelFrame(parent, text="Basic Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 設定項目
        self.name_var = tk.StringVar(value="simulation")
        self.entity_var = tk.StringVar(value="revenue_share")
        self.group_var = tk.StringVar(value="test")
        self.num_simulation_var = tk.StringVar(value="10")
        self.num_run_var = tk.StringVar(value="10")
        
        # 名前
        ttk.Label(settings_frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=2)
        
        # エンティティ
        ttk.Label(settings_frame, text="Entity:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.entity_var).grid(row=1, column=1, padx=5, pady=2)
        
        # グループ
        ttk.Label(settings_frame, text="Group:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.group_var).grid(row=2, column=1, padx=5, pady=2)
        
        # シミュレーション回数
        ttk.Label(settings_frame, text="Number of Simulations:").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.num_simulation_var).grid(row=3, column=1, padx=5, pady=2)
        
        # 実行回数
        ttk.Label(settings_frame, text="Number of Runs:").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.num_run_var).grid(row=4, column=1, padx=5, pady=2)

    def create_consumer_settings(self, parent):
        """消費者設定の入力フィールドを作成"""
        # スクロール可能なフレーム
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 消費者設定のフレーム
        settings_frame = ttk.LabelFrame(scrollable_frame, text="Consumer A Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # 基本設定
        self.consumer_vars = {
            "plan_of_use_shape": tk.StringVar(value="1.644"),
            "plan_of_use_scale": tk.StringVar(value="6.618"),
            "num_of_players": tk.StringVar(value="10"),
            "churn_rate": tk.StringVar(value="0.0"),
            "reuse_probability": tk.StringVar(value="0.0"),
            "num_of_products_mean": tk.StringVar(value="1.0"),
            "num_of_products_sd": tk.StringVar(value="0.0")
        }

        # 選好設定
        self.pref_vars = {
            "ownership_part_worth_mean": tk.StringVar(value="0.0"),
            "ownership_part_worth_sd": tk.StringVar(value="0.0"),
            "subscription_part_worth_mean": tk.StringVar(value="5.5"),
            "subscription_part_worth_sd": tk.StringVar(value="3.2"),
            "reuse_part_worth_mean": tk.StringVar(value="0.0"),
            "reuse_part_worth_sd": tk.StringVar(value="0.0"),
            "remanufacture_part_worth_mean": tk.StringVar(value="0.0"),
            "remanufacture_part_worth_sd": tk.StringVar(value="0.0"),
            "price_part_worth_mean": tk.StringVar(value="0.0"),
            "price_part_worth_sd": tk.StringVar(value="0.0"),
            "spec_part_worth_mean": tk.StringVar(value="0.0"),
            "spec_part_worth_sd": tk.StringVar(value="0.0"),
            "size_part_worth_mean": tk.StringVar(value="0.0"),
            "size_part_worth_sd": tk.StringVar(value="0.0")
        }

        # 基本設定の入力フィールド
        row = 0
        ttk.Label(settings_frame, text="Basic Settings", font=('Helvetica', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        for key, var in self.consumer_vars.items():
            ttk.Label(settings_frame, text=f"{key}:").grid(row=row, column=0, sticky=tk.W)
            ttk.Entry(settings_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=2)
            row += 1

        # 選好設定の入力フィールド
        ttk.Label(settings_frame, text="Preference Settings", font=('Helvetica', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        
        for key, var in self.pref_vars.items():
            ttk.Label(settings_frame, text=f"{key}:").grid(row=row, column=0, sticky=tk.W)
            ttk.Entry(settings_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=2)
            row += 1

        # スクロールバーとキャンバスを配置
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_product_settings(self, parent):
        """製品設定の入力フィールドを作成"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 製品設定のフレーム
        settings_frame = ttk.LabelFrame(scrollable_frame, text="Product Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # 製品属性の変数を初期化
        self.product_vars = {
            "size": tk.StringVar(value="10.0"),
            "price": tk.StringVar(value="20.0"),
            "base_of_new_products": tk.StringVar(value="3.0"),
            "base_price": tk.StringVar(value="30.0"),
            "price_discout_rate_by_generation": tk.StringVar(value="0.1"),
            "lifetime": tk.StringVar(value="10.0"),
            "base_production_cost": tk.StringVar(value="16.0"),
            "production_cost_discout_rate_by_generation": tk.StringVar(value="0.1"),
            "transport_cost": tk.StringVar(value="4.0"),
            "refurbish_cost": tk.StringVar(value="1.0"),
            "repair_cost": tk.StringVar(value="1.0"),
            "disporsal_cost": tk.StringVar(value="1.0"),
            "production_co2": tk.StringVar(value="408.0"),
            "transport_co2": tk.StringVar(value="3.0"),
            "use_co2": tk.StringVar(value="178.0"),
            "refurbish_co2": tk.StringVar(value="2.0"),
            "disporsal_co2": tk.StringVar(value="49.0"),
            "weibull_alpha": tk.StringVar(value="1.81"),
            "weibull_beta": tk.StringVar(value="25.8"),
            "repairable_year": tk.StringVar(value="2.0")
        }

        # 価格辞書の入力フィールド
        self.price_dict_vars = {
            "10": tk.StringVar(value="0.5"),
            "5": tk.StringVar(value="0.8")
        }

        row = 0
        # 製品属性の入力フィールド
        for key, var in self.product_vars.items():
            ttk.Label(settings_frame, text=f"{key}:").grid(row=row, column=0, sticky=tk.W)
            ttk.Entry(settings_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=2)
            row += 1

        # 価格辞書の入力フィールド
        ttk.Label(settings_frame, text="Price Dictionary", font=('Helvetica', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        row += 1
        for key, var in self.price_dict_vars.items():
            ttk.Label(settings_frame, text=f"Price {key}:").grid(row=row, column=0, sticky=tk.W)
            ttk.Entry(settings_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=2)
            row += 1

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_ecosystem_settings(self, parent):
        """エコシステム設定の入力フィールドを作成"""
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # プロバイダー設定を初期化
        self.ecosystem_vars = {
            "paas_provider": {
                "type": tk.StringVar(value="STANDARD"),
                "attributes": {
                    "base_price": tk.StringVar(value="100.0"),
                    "production_volume": tk.StringVar(value="2"),
                    "procurement_cost": tk.StringVar(value="200.0"),
                    "repair_cost": tk.StringVar(value="1.0"),
                    "base_production_volume": tk.StringVar(value="0")
                }
            },
            # "reuse_provider": {
            #     "type": tk.StringVar(value="STANDARD"),
            #     "attributes": {
            #         "initial_used_product_price": tk.StringVar(value="100"),
            #         "reuse_cost": tk.StringVar(value="100"),
            #         "repair_cost": tk.StringVar(value="200"),
            #         "revenue_share": tk.StringVar(value="0.6"),
            #         "quality_threshold": tk.StringVar(value="0.7")
            #     }
            # },
            "manufacturer": {
                "type": tk.StringVar(value="STANDARD"),
                "attributes": {
                    "base_price": tk.StringVar(value="200.0"),
                    "production_volume": tk.StringVar(value="8"),
                    "production_cost": tk.StringVar(value="160.0"),
                    "repair_cost": tk.StringVar(value="1.0"),
                    "base_production_volume": tk.StringVar(value="0")
                }
            # },
            # "remanufacturer": {
            #     "type": tk.StringVar(value="STANDARD"),
            #     "attributes": {
            #         "remanufacturing_cost": tk.StringVar(value="400"),
            #         "quality_threshold": tk.StringVar(value="0.8"),
            #         "success_rate": tk.StringVar(value="0.9"),
            #         "product_price": tk.StringVar(value="100")
            #     }
            # },
            # "recycler": {
            #     "type": tk.StringVar(value="STANDARD"),
            #     "attributes": {
            #         "recycling_cost": tk.StringVar(value="100"),
            #         "material_recovery_rate": tk.StringVar(value="0.8"),
            #         "processing_capacity": tk.StringVar(value="1000")
            #     }
            }
        }

        # 各プロバイダーの設定フレームを作成
        for provider_name, provider_data in self.ecosystem_vars.items():
            provider_frame = ttk.LabelFrame(scrollable_frame, text=f"{provider_name.title()} Settings", padding=10)
            provider_frame.pack(fill=tk.X, padx=5, pady=5)

            # タイプの設定
            ttk.Label(provider_frame, text="Type:").grid(row=0, column=0, sticky=tk.W)
            ttk.Entry(provider_frame, textvariable=provider_data["type"]).grid(row=0, column=1, padx=5, pady=2)

            # 属性の設定
            row = 1
            for attr_name, var in provider_data["attributes"].items():
                ttk.Label(provider_frame, text=f"{attr_name}:").grid(row=row, column=0, sticky=tk.W)
                ttk.Entry(provider_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=2)
                row += 1

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_business_model_settings(self, parent):
        """ビジネスモデル設定の入力フィールドを作成"""
        settings_frame = ttk.LabelFrame(parent, text="Business Model Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # ビジネスモデルの設定を辞書で管理
        self.business_model_vars = {
            "business_model_type": tk.StringVar(value="revenue_sharing"),
            "attributes": {
                "revenue_share_min": tk.StringVar(value="0.1"),
                "revenue_share_max": tk.StringVar(value="0.5"),
                "revenue_share_step": tk.StringVar(value="0.1")
            }
        }

        # ビジネスモデルタイプ
        ttk.Label(settings_frame, text="Business Model Type:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            settings_frame,
            textvariable=self.business_model_vars["business_model_type"],
            state="readonly"
        ).grid(row=0, column=1, padx=5, pady=5)

        # Revenue Share範囲設定
        ttk.Label(settings_frame, text="Revenue Share Min:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            settings_frame,
            textvariable=self.business_model_vars["attributes"]["revenue_share_min"]
        ).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(settings_frame, text="Revenue Share Max:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            settings_frame,
            textvariable=self.business_model_vars["attributes"]["revenue_share_max"]
        ).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(settings_frame, text="Revenue Share Step:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(
            settings_frame,
            textvariable=self.business_model_vars["attributes"]["revenue_share_step"]
        ).grid(row=3, column=1, padx=5, pady=5)

    def create_policy_settings(self, parent):
        """ポリシー設定の入力フィールドを作成"""
        settings_frame = ttk.LabelFrame(parent, text="Policy Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # ポリシー設定の変数を初期化
        self.policy_vars = {
            "carbon_tax_rate": tk.StringVar(value="0.1"),
            "subsidy_rate": tk.StringVar(value="0.2"),
            "deposit_amount": tk.StringVar(value="1000.0"),
            "epr_fee": tk.StringVar(value="500.0"),
            "repair_cost_reduction": tk.StringVar(value="0.3")
        }

        # ポリシー設定の入力フィールド
        row = 0
        for key, var in self.policy_vars.items():
            ttk.Label(settings_frame, text=f"{key}:").grid(row=row, column=0, sticky=tk.W)
            ttk.Entry(settings_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=2)
            row += 1

    def save_config(self):
        """設定をJSONファイルとして保存"""
        # Revenue Share の範囲を生成
        min_share = float(self.business_model_vars["attributes"]["revenue_share_min"].get())
        max_share = float(self.business_model_vars["attributes"]["revenue_share_max"].get())
        step = float(self.business_model_vars["attributes"]["revenue_share_step"].get())
        
        print(f"Generating revenue shares from {min_share} to {max_share} with step {step}")
        revenue_shares = np.arange(min_share, max_share + step, step).round(2)
        print(f"Generated revenue shares: {revenue_shares}")
        
        # 基本設定をJSONファイルから読み込み
        try:
            with open("config/revenue_share/setting_rs_0.json", 'r', encoding='utf-8') as f:
                base_config = json.load(f)
                print(f"Loaded base config successfully from setting_rs_0.json")
        except FileNotFoundError:
            messagebox.showerror("Error", "Base configuration file not found: config/revenue_share/setting_rs_0.json")
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in base configuration file")
            return

        # configディレクトリがない場合は作成
        os.makedirs("config/revenue_share", exist_ok=True)
        
        # 既存のファイルを削除（setting_rs_0.jsonは除外）
        existing_files = glob.glob("config/revenue_share/setting_rs_[1-9]*.json")
        for file in existing_files:
            os.remove(file)
        print(f"Removed {len(existing_files)} existing files")
        
        files_created = 0
        # 各Revenue Share値についてJSONファイルを作成（1から開始）
        for i, revenue_share in enumerate(revenue_shares[1:], start=1):
            try:
                config = base_config.copy()
                config["business_model_settings"] = {
                    "business_model_type": "revenue_sharing",
                    "attributes": {
                        "revenue_share": float(revenue_share)
                    }
                }
                
                file_name = f"setting_rs_{i}.json"
                file_path = os.path.join("config/revenue_share", file_name)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=4)
                
                files_created += 1
                print(f"Created file {file_name} with revenue_share: {revenue_share}")
            
            except Exception as e:
                print(f"Error creating file for revenue_share {revenue_share}: {str(e)}")
                continue

        print(f"Total files created: {files_created}")
        messagebox.showinfo(
            "Success", 
            f"Configuration files saved successfully.\nCreated {files_created} files in config/revenue_share/"
        )
        
    def select_config(self):
        """設定ファイルのフォルダを選択"""
        folder_path = filedialog.askdirectory(
            initialdir="config",
            title="設定ファイルのフォルダを選択"
        )
        
        if folder_path:
            self.file_path_var.set(folder_path)
            self.current_config = Path(folder_path).name
            
            # フォルダ内の設定ファイル一覧を取得
            config_files = glob.glob(str(Path(folder_path) / "*.json"))
            
            if not config_files:
                messagebox.showwarning("警告", "フォルダ内にJSONファイルが見つかりません")
                return
            
            # 最初の設定ファイルの内容を表示
            try:
                with open(config_files[0], 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 整形してテキストエリアに表示
                formatted_json = json.dumps(config_data, indent=2, ensure_ascii=False)
                self.content_text.delete('1.0', tk.END)
                self.content_text.insert('1.0', formatted_json)
                
                # 設定エディタタブにも値を設定
                self.name_var.set(config_data.get('name', ''))
                self.entity_var.set(config_data.get('entity', ''))
                
            except Exception as e:
                messagebox.showerror("エラー", f"設定ファイルの読み込みに失敗しました:\n{str(e)}")
                self.current_config = None
        
    def run_simulation(self):
        """シミュレーションを実行"""
        if not self.current_config:
            messagebox.showerror("エラー", "設定フォルダが選択されていません")
            return
        
        try:
            # run.pyのメイン処理を実行
            import run_with_game
            run_with_game.main(self.current_config)
            messagebox.showinfo("完了", "シミュレーションが完了しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"シミュレーション実行中にエラーが発生しました:\n{str(e)}")

if __name__ == "__main__":
    app = SimulationGUI()
    app.master.mainloop()