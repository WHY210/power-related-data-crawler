import pandas as pd
import matplotlib.pyplot as plt
import os

# 設定中文字型
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang TC', 'Heiti TC', 'sans-serif'] 
plt.rcParams['axes.unicode_minus'] = False

def compare_dorm_srPrice():
    # 檔案路徑
    dorms_file = 'merged_dorms.csv'
    settlement_file = 'settlement_202601.csv'
    
    # 檢查檔案
    if not os.path.exists(dorms_file) or not os.path.exists(settlement_file):
        print("缺少必要的資料檔案 (merged_dorms.csv 或 settlement_202601.csv)")
        return

    print("正在讀取資料...")
    
    # 1. 讀取宿舍資料
    df_dorms = pd.read_csv(dorms_file)
    df_dorms['Datetime'] = pd.to_datetime(df_dorms['Datetime'])
    df_dorms.set_index('Datetime', inplace=True)
    
    # 2. 讀取 srPrice 資料
    df_settlement = pd.read_csv(settlement_file, header=1)
    try:
        df_settlement['Datetime'] = pd.to_datetime(df_settlement['date']) + pd.to_timedelta(df_settlement['hour'], unit='h')
        df_settlement.set_index('Datetime', inplace=True)
        sr_price = df_settlement[['srPrice']] # 只取 srPrice
    except Exception as e:
        print(f"結算資料時間處理錯誤: {e}")
        return

    # 3. 合併資料 (inner join，只保留兩邊都有的時間段)
    # 這樣可以確保畫出來的圖時間是對齊的
    merged = df_dorms.join(sr_price, how='inner')
    
    if merged.empty:
        print("錯誤: 兩個檔案的時間範圍沒有重疊，無法繪製對照圖。")
        print(f"宿舍資料範圍: {df_dorms.index.min()} ~ {df_dorms.index.max()}")
        print(f"結算資料範圍: {sr_price.index.min()} ~ {sr_price.index.max()}")
        return

    print(f"合併後資料範圍: {merged.index.min()} ~ {merged.index.max()}")
    
    # 建立輸出資料夾
    output_dir = 'plots/dorm_vs_srPrice'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 4. 為每個宿舍繪製雙軸圖
    # 宿舍名稱在 merged_dorms.csv 中，除了 srPrice 以外的欄位
    dorm_columns = [col for col in merged.columns if col != 'srPrice']
    
    for dorm in dorm_columns:
        fig, ax1 = plt.subplots(figsize=(15, 7))
        
        # 左軸: 宿舍用電量
        color_dorm = 'tab:blue'
        ax1.set_xlabel('時間')
        ax1.set_ylabel(f'{dorm} 用電量 (kW)', color=color_dorm)
        ax1.plot(merged.index, merged[dorm], color=color_dorm, label=f'{dorm} 用電量', alpha=0.8, linewidth=1.5)
        ax1.tick_params(axis='y', labelcolor=color_dorm)
        ax1.grid(True, alpha=0.3)
        
        # 右軸: srPrice
        ax2 = ax1.twinx()  # 共享 X 軸
        color_price = 'tab:red'
        ax2.set_ylabel('srPrice (價格)', color=color_price)
        ax2.plot(merged.index, merged['srPrice'], color=color_price, label='srPrice', alpha=0.6, linestyle='--', linewidth=1.5)
        ax2.tick_params(axis='y', labelcolor=color_price)
        
        # 標題
        plt.title(f'{dorm} 用電量 vs srPrice 對照圖')
        
        # 合併圖例 (稍微複雜一點，因為分屬兩個軸)
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
        
        plt.tight_layout()
        
        output_img = os.path.join(output_dir, f'{dorm}_vs_srPrice.png')
        plt.savefig(output_img, dpi=150)
        plt.close()
        print(f"  -> 已儲存: {output_img}")

if __name__ == "__main__":
    compare_dorm_srPrice()
