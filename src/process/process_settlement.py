import pandas as pd
import matplotlib.pyplot as plt
import os

# 設定中文字型
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang TC', 'Heiti TC', 'sans-serif'] 
plt.rcParams['axes.unicode_minus'] = False

def process_settlement():
    file_path = 'settlement_202601.csv'
    
    if not os.path.exists(file_path):
        print(f"找不到檔案: {file_path}")
        return

    print(f"正在讀取 {file_path} ...")
    
    # 讀取 CSV，header 在第 2 行 (index=1)
    df = pd.read_csv(file_path, header=1)
    
    # 處理時間欄位
    try:
        df['Datetime'] = pd.to_datetime(df['date']) + pd.to_timedelta(df['hour'], unit='h')
        df.set_index('Datetime', inplace=True)
    except Exception as e:
        print(f"時間格式轉換錯誤: {e}")
        return

    # 找出所有包含 'Price' 的欄位
    price_cols = [col for col in df.columns if 'Price' in col]
    
    if not price_cols:
        print("未找到任何包含 'Price' 的欄位。")
        return
        
    print(f"找到以下價格欄位: {price_cols}")

    # 建立輸出資料夾
    output_dir = os.path.join('plots', 'settlement_prices')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. 為每個價格欄位畫獨立的圖
    for col in price_cols:
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df[col], label=col, color='tab:blue', linewidth=1)
        
        plt.title(f'Settlement 202601 - {col}')
        plt.xlabel('時間')
        plt.ylabel('價格')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        output_img = os.path.join(output_dir, f'{col}.png')
        plt.savefig(output_img, dpi=100)
        plt.close()
        print(f"  -> 已儲存單獨圖表: {output_img}")

    # 2. 畫一張合併圖表 (比較用)
    plt.figure(figsize=(15, 8))
    for col in price_cols:
        plt.plot(df.index, df[col], label=col, linewidth=1.5, alpha=0.8)
    
    plt.title('Settlement 202601 - 所有價格比較 (All Prices)')
    plt.xlabel('時間')
    plt.ylabel('價格')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    combined_img = os.path.join(output_dir, 'ALL_Prices_Combined.png')
    plt.savefig(combined_img, dpi=150)
    plt.close()
    print(f"  -> 已儲存合併圖表: {combined_img}")

if __name__ == "__main__":
    process_settlement()
