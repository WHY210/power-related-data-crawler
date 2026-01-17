import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import matplotlib.font_manager as fm

# 設定中文字型 (嘗試尋找常見的中文字型，避免亂碼)
# MacOS 通常有 'Arial Unicode MS' 或 'PingFang TC'
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang TC', 'Heiti TC', 'sans-serif'] 
plt.rcParams['axes.unicode_minus'] = False

def process_dorms():
    # 建立輸出資料夾
    dirs = ['plots/full_series', 'plots/weekly_profile']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)

    # 取得所有 csv 檔案
    files = glob.glob(os.path.join('宿舍', '*.csv'))
    
    all_dfs = []

    print("開始處理檔案...")

    for file_path in files:
        file_name = os.path.basename(file_path)
        dorm_name = os.path.splitext(file_name)[0]
        
        print(f"處理: {dorm_name}")
        
        try:
            # 讀取 CSV
            df = pd.read_csv(file_path)
            
            # 確保有 Datetime 欄位
            if 'Datetime' not in df.columns:
                print(f"警告: {file_name} 缺少 'Datetime' 欄位，跳過。")
                continue
                
            # 轉換時間格式並設為 index
            df['Datetime'] = pd.to_datetime(df['Datetime'])
            df.set_index('Datetime', inplace=True)
            
            # 假設第一個欄位是數值
            value_col = df.columns[0]
            
            # 加入合併列表 (保留原始資料供合併用)
            all_dfs.append(df)
            
            # --- 圖表 1: 全時段趨勢圖 (Raw + Weekly MA + Monthly MA) ---
            plt.figure(figsize=(15, 8))
            
            # 1. 原始資料 (透明度調低，作為背景)
            plt.plot(df.index, df[value_col], label='原始數據 (每小時)', color='lightgray', alpha=0.6, linewidth=0.5)
            
            # 2. 週移動平均 (7天 * 24小時)
            weekly_rolling = df[value_col].rolling(window=24*7, min_periods=1).mean()
            plt.plot(df.index, weekly_rolling, label='週移動平均 (7日)', color='orange', linewidth=1.5)
            
            # 3. 月移動平均 (30天 * 24小時)
            monthly_rolling = df[value_col].rolling(window=24*30, min_periods=1).mean()
            plt.plot(df.index, monthly_rolling, label='月移動平均 (30日)', color='blue', linewidth=2)
            
            plt.title(f'{dorm_name} - 全時段用電趨勢')
            plt.xlabel('日期')
            plt.ylabel('用電量')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            output_img1 = os.path.join('plots/full_series', f'{dorm_name}_trend.png')
            plt.savefig(output_img1, dpi=150)
            plt.close()
            
            # --- 圖表 2: 平均週間作息圖 (Typical Week Profile) - 分季節 ---
            # 建立用於分組的欄位
            df_profile = df.copy()
            df_profile['weekday'] = df_profile.index.dayofweek # 0=Mon, 6=Sun
            df_profile['hour'] = df_profile.index.hour
            df_profile['month'] = df_profile.index.month
            
            # 定義季節函數
            def get_season(month):
                if month in [3, 4, 5]:
                    return 'Spring (春)'
                elif month in [6, 7, 8]:
                    return 'Summer (夏)'
                elif month in [9, 10, 11]:
                    return 'Autumn (秋)'
                else:
                    return 'Winter (冬)'
            
            df_profile['season'] = df_profile['month'].apply(get_season)
            
            # 設定繪圖
            plt.figure(figsize=(12, 6))
            
            seasons = ['Spring (春)', 'Summer (夏)', 'Autumn (秋)', 'Winter (冬)']
            colors = {'Spring (春)': 'green', 'Summer (夏)': 'red', 'Autumn (秋)': 'orange', 'Winter (冬)': 'blue'}
            
            # 確保 X 軸刻度正確
            ticks = range(0, 168, 24)
            labels = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']
            
            has_data = False
            
            for season in seasons:
                season_data = df_profile[df_profile['season'] == season]
                
                if not season_data.empty:
                    # 依照 (星期, 小時) 分組計算平均
                    weekly_profile = season_data.groupby(['weekday', 'hour'])[value_col].mean()
                    
                    # 如果某個季節資料不完整 (例如只有幾小時)，可能會導致繪圖問題，這裡簡單處理
                    if len(weekly_profile) > 0:
                        # 為了讓 plot 能夠正確疊加，我們需要統一 X 軸
                        # weekly_profile 的 index 是 MultiIndex (weekday, hour)
                        # 我們將其轉換為 0~167 的整數 index
                        
                        # 建立完整的 index (7天 * 24小時) 確保線條不中斷
                        full_idx = pd.MultiIndex.from_product([range(7), range(24)], names=['weekday', 'hour'])
                        weekly_profile = weekly_profile.reindex(full_idx)
                        
                        # 繪製
                        # reset_index 後，資料變成 dataframe，直接取 values 畫圖即可
                        # 這樣 x 軸就是 0, 1, 2... 167
                        plt.plot(weekly_profile.values, label=season, color=colors[season], linewidth=2)
                        has_data = True

            if has_data:
                plt.xticks(ticks, labels)
                plt.title(f'{dorm_name} - 分季節平均一週用電作息')
                plt.xlabel('時間 (星期)')
                plt.ylabel('平均用電量')
                plt.legend()
                plt.grid(True, which='both', linestyle='--', alpha=0.7)
                
                # 加入垂直分隔線區分每一天
                for x in range(24, 168, 24):
                    plt.axvline(x=x, color='gray', linestyle=':', alpha=0.5)
                    
                plt.tight_layout()
                
                output_img2 = os.path.join('plots/weekly_profile', f'{dorm_name}_profile_seasonal.png')
                plt.savefig(output_img2, dpi=150)
                plt.close()
                print(f"  -> 已儲存圖表: {output_img1}, {output_img2}")
            else:
                plt.close()
                print(f"  -> 已儲存圖表: {output_img1} (無季節資料可繪製)")
            
        except Exception as e:
            print(f"處理 {file_name} 時發生錯誤: {e}")

    # 合併所有資料 (保持不變)
    if all_dfs:
        print("正在合併所有資料...")
        # axis=1 表示橫向合併 (依據 index/Datetime 對齊)
        merged_df = pd.concat(all_dfs, axis=1)
        
        # 依照時間排序
        merged_df.sort_index(inplace=True)
        
        output_csv = 'merged_dorms.csv'
        merged_df.to_csv(output_csv)
        print(f"合併完成！已儲存至: {output_csv}")
    else:
        print("沒有成功讀取到任何資料。")

if __name__ == "__main__":
    process_dorms()
