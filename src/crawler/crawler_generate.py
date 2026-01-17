import requests
import os
import sys
import shutil
from datetime import datetime

# Add src to path to import process script
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)

from process.organize_taipower_data import main as organize_data

root_dir = os.path.dirname(src_dir)

# Define directories
raw_gen_dir = os.path.join(root_dir, "data", "taipower_generators", "raw")
raw_flow_dir = os.path.join(root_dir, "data", "taipower_flow", "raw")
proc_gen_dir = os.path.join(root_dir, "data", "taipower_generators")
proc_flow_dir = os.path.join(root_dir, "data", "taipower_flow")

# Ensure raw directories exist
os.makedirs(raw_gen_dir, exist_ok=True)
os.makedirs(raw_flow_dir, exist_ok=True)

# Generate timestamped filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
raw_filename1 = os.path.join(raw_gen_dir, f"raw_generator_{timestamp}.json")
raw_filename2 = os.path.join(raw_flow_dir, f"raw_flow_{timestamp}.json")

# Temp filenames for processing
temp_filename1 = os.path.join(proc_gen_dir, "temp_download.json")
temp_filename2 = os.path.join(proc_flow_dir, "temp_download.json")

url1 = "https://service.taipower.com.tw/data/opendata/apply/file/d006010/001.json"
url2 = "https://service.taipower.com.tw/data/opendata/apply/file/d006009/001.json"

print("START")

# Download Generator Data
try:
    response = requests.get(url1, verify=False)
    if response.status_code == 200:
        # Save raw
        with open(raw_filename1, "wb") as file:
            file.write(response.content)
        print(f"Generator raw data saved to {raw_filename1}")
        
        # Copy to temp for processing
        shutil.copy(raw_filename1, temp_filename1)
        print(f"Generator data ready for processing at {temp_filename1}")
    else:
        print(f"Generator download failed: {response.status_code}")
except Exception as e:
    print(f"Generator download error: {e}")

# Download Flow Data
try:
    response = requests.get(url2, verify=False)
    if response.status_code == 200:
        # Save raw
        with open(raw_filename2, "wb") as file:
            file.write(response.content)
        print(f"Flow raw data saved to {raw_filename2}")
        
        # Copy to temp for processing
        shutil.copy(raw_filename2, temp_filename2)
        print(f"Flow data ready for processing at {temp_filename2}")
    else:
        print(f"Flow download failed: {response.status_code}")
except Exception as e:
    print(f"Flow download error: {e}")

# Run Organization
print("Running organization and merging...")
try:
    organize_data()
    print("Organization complete.")
except Exception as e:
    print(f"Organization failed: {e}")


# import json

# with open(r'data/2024/power_generation/各機組過去發電量20240501-20240731.json', 'r', encoding='utf-8-sig') as file:
#     data = json.load(file)

# # 使用字典來依照 FUEL_TYPE 分類 UNIT_NAME
# fuel_type_dict = {}

# for entry in data['records']['NET_P']:
#     if "UNIT_NAME" in entry and "FUEL_TYPE" in entry:
#         unit_name = entry["UNIT_NAME"]
#         fuel_type = entry["FUEL_TYPE"]
        
#         if fuel_type not in fuel_type_dict:
#             fuel_type_dict[fuel_type] = []
        
#         # 確保同一個機組名稱不重複
#         if unit_name not in fuel_type_dict[fuel_type]:
#             fuel_type_dict[fuel_type].append(unit_name)

# # 輸出每個燃料類型及其對應的機組名稱
# for fuel_type, units in fuel_type_dict.items():
#     print(f"Fuel Type: {fuel_type}")
#     for unit in units:
#         print(f"  {unit}")
