import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import json
from typing import Dict, Any
import os

class ConfigEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Simulation Config Editor")
        self.geometry("800x600")
        
        # メインフレーム
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ノートブック（タブ）の作成
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本設定タブ
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="Basic Settings")
        self.create_basic_settings(basic_frame)
        
        # 消費者設定タブ
        consumer_frame = ttk.Frame(self.notebook)
        self.notebook.add(consumer_frame, text="Consumer Settings")
        self.create_consumer_settings(consumer_frame)
        
        # 製品設定タブ
        product_frame = ttk.Frame(self.notebook)
        self.notebook.add(product_frame, text="Product Settings")
        self.create_product_settings(product_frame)
        
        # エコシステム設定タブ
        ecosystem_frame = ttk.Frame(self.notebook)
        self.notebook.add(ecosystem_frame, text="Ecosystem Settings")
        self.create_ecosystem_settings(ecosystem_frame)
        
        # ポリシー設定タブ
        policy_frame = ttk.Frame(self.notebook)
        self.notebook.add(policy_frame, text="Policy Settings")
        self.create_policy_settings(policy_frame)
        
        # ビジネスモデル設定タブを追加
        business_model_frame = ttk.Frame(self.notebook)
        self.notebook.add(business_model_frame, text="Business Model Settings")
        self.create_business_model_settings(business_model_frame)
        
        # 保存ボタン
        save_button = ttk.Button(main_frame, text="Save Config", command=self.save_config)
        save_button.pack(pady=10)

    def create_basic_settings(self, parent):
        """基本設定の入力フィールドを作成"""
        # 基本設定のフレーム
        settings_frame = ttk.LabelFrame(parent, text="Basic Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 設定項目
        self.name_var = tk.StringVar(value="simulation")
        self.entity_var = tk.StringVar(value="all")
        self.group_var = tk.StringVar(value="test")
        self.num_simulation_var = tk.StringVar(value="10")
        self.num_run_var = tk.StringVar(value="1")
        
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
            "plan_of_use_mean": tk.StringVar(value="2"),
            "plan_of_use_sd": tk.StringVar(value="1"),
            "num_of_players": tk.StringVar(value="3"),
            "churn_rate": tk.StringVar(value="0.0"),
            "reuse_probability": tk.StringVar(value="0.5"),
            "num_of_products_mean": tk.StringVar(value="1"),
            "num_of_products_sd": tk.StringVar(value="0")
        }

        # 選好設定
        self.pref_vars = {
            "ownership_part_worth_mean": tk.StringVar(value="3.0"),
            "ownership_part_worth_sd": tk.StringVar(value="0.5"),
            "subscription_part_worth_mean": tk.StringVar(value="3.0"),
            "subscription_part_worth_sd": tk.StringVar(value="0.5"),
            "reuse_part_worth_mean": tk.StringVar(value="3.0"),
            "reuse_part_worth_sd": tk.StringVar(value="0.5"),
            "remanufacture_part_worth_mean": tk.StringVar(value="0"),
            "remanufacture_part_worth_sd": tk.StringVar(value="0"),
            "price_part_worth_mean": tk.StringVar(value="0"),
            "price_part_worth_sd": tk.StringVar(value="0"),
            "spec_part_worth_mean": tk.StringVar(value="1"),
            "spec_part_worth_sd": tk.StringVar(value="0"),
            "size_part_worth_mean": tk.StringVar(value="0"),
            "size_part_worth_sd": tk.StringVar(value="0")
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
            "size": tk.StringVar(value="10"),
            "price": tk.StringVar(value="30"),
            "base_of_new_products": tk.StringVar(value="3"),
            "base_price": tk.StringVar(value="30"),
            "price_discout_rate_by_generation": tk.StringVar(value="0.1"),
            "lifetime": tk.StringVar(value="4"),
            "base_production_cost": tk.StringVar(value="100"),
            "production_cost_discout_rate_by_generation": tk.StringVar(value="0.1"),
            "transport_cost": tk.StringVar(value="30"),
            "refurbish_cost": tk.StringVar(value="24000"),
            "repair_cost": tk.StringVar(value="44000"),
            "disporsal_cost": tk.StringVar(value="4730"),
            "production_co2": tk.StringVar(value="408"),
            "transport_co2": tk.StringVar(value="3"),
            "use_co2": tk.StringVar(value="178"),
            "refurbish_co2": tk.StringVar(value="2"),
            "disporsal_co2": tk.StringVar(value="49"),
            "weibull_alpha": tk.StringVar(value="1.81"),
            "weibull_beta": tk.StringVar(value="25.8"),
            "repairable_year": tk.StringVar(value="2")
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
                    "production_volume": tk.StringVar(value="2"),
                    "subscription_fee": tk.StringVar(value="100"),
                    "initial_cost": tk.StringVar(value="500"),
                    "maintenance_cost": tk.StringVar(value="50"),
                    "revenue_share": tk.StringVar(value="0.7"),
                    "procurement_cost": tk.StringVar(value="100"),
                    "repair_cost": tk.StringVar(value="100")
                }
            },
            "reuse_provider": {
                "type": tk.StringVar(value="STANDARD"),
                "attributes": {
                    "reuse_cost": tk.StringVar(value="100"),
                    "repair_cost": tk.StringVar(value="200"),
                    "revenue_share": tk.StringVar(value="0.6"),
                    "quality_threshold": tk.StringVar(value="0.7")
                }
            },
            "manufacturer": {
                "type": tk.StringVar(value="STANDARD"),
                "attributes": {
                    "production_volume": tk.StringVar(value="2"),
                    "production_cost": tk.StringVar(value="1000"),
                    "warranty_period": tk.StringVar(value="2"),
                    "quality_standard": tk.StringVar(value="0.9"),
                    "repair_cost": tk.StringVar(value="100")
                }
            },
            "remanufacturer": {
                "type": tk.StringVar(value="STANDARD"),
                "attributes": {
                    "remanufacturing_cost": tk.StringVar(value="400"),
                    "quality_threshold": tk.StringVar(value="0.8"),
                    "success_rate": tk.StringVar(value="0.9")
                }
            },
            "recycler": {
                "type": tk.StringVar(value="STANDARD"),
                "attributes": {
                    "recycling_cost": tk.StringVar(value="100"),
                    "material_recovery_rate": tk.StringVar(value="0.8"),
                    "processing_capacity": tk.StringVar(value="1000")
                }
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

        # ビジネスモデルタイプの変数
        self.business_model_type_var = tk.StringVar(value="STANDARD")

        # ビジネスモデルタイプの選択
        ttk.Label(settings_frame, text="Business Model Type:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Combobox(
            settings_frame, 
            textvariable=self.business_model_type_var,
            values=["STANDARD", "SUBSCRIPTION", "REUSE"],  # 選択可能なビジネスモデルタイプ
            state="readonly"
        ).grid(row=0, column=1, padx=5, pady=5)

    def create_policy_settings(self, parent):
        """ポリシー設定の入力フィールドを作成"""
        settings_frame = ttk.LabelFrame(parent, text="Policy Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # ポリシー設定の変数を初期化
        self.policy_vars = {
            "carbon_tax_rate": tk.StringVar(value="0.1"),
            "subsidy_rate": tk.StringVar(value="0.2"),
            "deposit_amount": tk.StringVar(value="1000"),
            "epr_fee": tk.StringVar(value="500"),
            "repair_cost_reduction": tk.StringVar(value="0.3")
        }

        # ポリシー設定の入力フィールド
        row = 0
        for key, var in self.policy_vars.items():
            ttk.Label(settings_frame, text=f"{key}:").grid(row=row, column=0, sticky=tk.W)
            ttk.Entry(settings_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=2)
            row += 1

    def save_config(self):
        """設定をJSONファイルに保存"""
        # 消費者設定で整数として扱うパラメータのリスト
        consumer_int_params = ["num_of_players", "num_of_products_mean", "num_of_products_sd"]
        
        # エコシステム設定で整数として扱うパラメータのリスト
        ecosystem_int_params = ["production_volume"]
        
        config = {
            "name": self.name_var.get(),
            "entity": self.entity_var.get(),
            "group": self.group_var.get(),
            "num_of_simulation": int(self.num_simulation_var.get()),
            "num_of_run": int(self.num_run_var.get()),
            "consumer_attributes": {
                "A": {
                    **{
                        k: int(v.get()) if k in consumer_int_params else float(v.get()) 
                        for k, v in self.consumer_vars.items()
                    },
                    "pref_dict": {
                        k: float(v.get()) for k, v in self.pref_vars.items()
                    }
                }
            },
            "product_attributes": {
                "p": {
                    **{k: float(v.get()) for k, v in self.product_vars.items()},
                    "price_dict": {
                        k: float(v.get()) for k, v in self.price_dict_vars.items()
                    }
                }
            },
            "ecosystem_settings": {
                provider_name: {
                    "type": provider_data["type"].get(),
                    "attributes": {
                        k: int(v.get()) if k in ecosystem_int_params else float(v.get())
                        for k, v in provider_data["attributes"].items()
                    }
                }
                for provider_name, provider_data in self.ecosystem_vars.items()
            },
            "policy_settings": {
                k: float(v.get()) for k, v in self.policy_vars.items()
            },
            "business_model_type": self.business_model_type_var.get()
        }
        
        # configディレクトリがない場合は作成
        os.makedirs("config", exist_ok=True)
        
        # ファイル保存ダイアログを表示
        file_path = filedialog.asksaveasfilename(
            initialdir="config",
            title="Save Configuration File",
            filetypes=[("JSON files", "*.json")],
            defaultextension=".json",
            initialfile="setting.json"
        )
        
        if file_path:  # ファイルパスが選択された場合
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
                
            messagebox.showinfo("Success", f"Configuration saved successfully to {file_path}")

if __name__ == "__main__":
    app = ConfigEditor()
    app.mainloop() 