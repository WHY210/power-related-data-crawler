import os
import json
import glob
from datetime import datetime
import re

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FLOW_DIR = os.path.join(BASE_DIR, "data", "taipower_flow")
GEN_DIR = os.path.join(BASE_DIR, "data", "taipower_generators")

def parse_date(date_str):
    # Formats: "2025-06-01T00:00:00", "2025-06-01 00:00:00", "2025-06-01", "2022-01-01 00:00"
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except ValueError:
                return datetime.strptime(date_str, "%Y-%m-%d")

def format_date_short(dt):
    return dt.strftime("%Y%m%d")

def load_json(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':')) # Minified to save space

def process_directory(directory, list_key, file_prefix):
    print(f"Processing directory: {directory}")
    
    # 1. Identify and Rename Files
    json_files = glob.glob(os.path.join(directory, "*.json"))
    
    # Filter out files that look like master files (e.g., flow_2025.json)
    # Master pattern: prefix_YYYY.json
    master_pattern = re.compile(rf"{file_prefix}_(\d{{4}})\.json$")
    
    files_to_process = []
    
    for file_path in json_files:
        filename = os.path.basename(file_path)
        if master_pattern.match(filename):
            continue
            
        try:
            data = load_json(file_path)
            if "records" not in data or list_key not in data["records"]:
                print(f"Skipping {filename}: Invalid structure.")
                continue
                
            start_date_str = data["records"].get("START_DATE")
            end_date_str = data["records"].get("END_DATE")
            
            if not start_date_str or not end_date_str:
                print(f"Skipping {filename}: Missing dates.")
                continue
                
            start_dt = parse_date(start_date_str)
            end_dt = parse_date(end_date_str)
            
            new_filename = f"{file_prefix}_{format_date_short(start_dt)}-{format_date_short(end_dt)}.json"
            new_file_path = os.path.join(directory, new_filename)
            
            if file_path != new_file_path:
                print(f"Renaming {filename} -> {new_filename}")
                os.rename(file_path, new_file_path)
                files_to_process.append(new_file_path)
            else:
                files_to_process.append(file_path)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # 2. Merge into Master File(s) (Split by Record Year)
    records_by_year = {} # Year -> List of records
    metadata_by_year = {} # Year -> Metadata dict

    print(f"  Aggregating records from {len(files_to_process)} files...")
    for fp in files_to_process:
        try:
            data = load_json(fp)
            
            # Extract common metadata (first found serves as template)
            if not metadata_by_year:
                # Store generic metadata
                common_meta = {
                    "CATALOG": data["records"].get("CATALOG", ""),
                    "UNIT_OF_MEASUREMENT": data["records"].get("UNIT_OF_MEASUREMENT", ""),
                    "INTERVAL": data["records"].get("INTERVAL", "")
                }
            
            for rec in data["records"][list_key]:
                # Normalize DATE -> DATETIME (Repeated here for safety if files were re-read)
                if "DATE" in rec and "DATETIME" not in rec:
                    val = rec.pop("DATE")
                    val = val.replace(" ", "T")
                    if len(val) == 16:
                        val += ":00"
                    rec["DATETIME"] = val

                if "DATETIME" not in rec:
                     continue 

                # Determine Year
                dt = parse_date(rec["DATETIME"])
                year = dt.year
                
                if year not in records_by_year:
                    records_by_year[year] = []
                    metadata_by_year[year] = common_meta.copy() if 'common_meta' in locals() else {
                        "CATALOG": data["records"].get("CATALOG", ""),
                        "UNIT_OF_MEASUREMENT": data["records"].get("UNIT_OF_MEASUREMENT", ""),
                        "INTERVAL": data["records"].get("INTERVAL", "")
                    }

                records_by_year[year].append(rec)
        except Exception as e:
            print(f"Error reading {os.path.basename(fp)}: {e}")
            
    # 3. Write Master Files
    for year, new_records in records_by_year.items():
        master_filename = f"{file_prefix}_{year}.json"
        master_path = os.path.join(directory, master_filename)
        
        print(f"Updating master file for {year}: {master_filename}")
        
        master_data = {
            "records": {
                "CATALOG": metadata_by_year[year]["CATALOG"],
                "START_DATE": "9999-12-31T23:59:59",
                "END_DATE": "0000-01-01T00:00:00",
                "UNIT_OF_MEASUREMENT": metadata_by_year[year]["UNIT_OF_MEASUREMENT"],
                "INTERVAL": metadata_by_year[year]["INTERVAL"],
                list_key: []
            }
        }
        
        existing_records_dict = {} # Key: (DATETIME, UNIT_NAME) -> Record
        
        # Load existing master if it exists to preserve manual edits or other data
        if os.path.exists(master_path):
            print(f"  Loading existing master {master_filename}...")
            try:
                existing_master = load_json(master_path)
                for rec in existing_master["records"][list_key]:
                    key = (rec["DATETIME"], rec["UNIT_NAME"])
                    existing_records_dict[key] = rec
            except Exception as e:
                print(f"  Error loading master {master_filename}, starting fresh: {e}")
        
        # Merge new records
        for rec in new_records:
            key = (rec["DATETIME"], rec["UNIT_NAME"])
            existing_records_dict[key] = rec
            
        # Reconstruct list and sort
        print("  Reconstructing and sorting records...")
        all_records = list(existing_records_dict.values())
        all_records.sort(key=lambda x: (x["DATETIME"], x["UNIT_NAME"]))
        
        # Update Dates
        if all_records:
            master_data["records"][list_key] = all_records
            master_data["records"]["START_DATE"] = all_records[0]["DATETIME"]
            master_data["records"]["END_DATE"] = all_records[-1]["DATETIME"]
        
        # Save
        print(f"  Saving {master_filename}...")
        save_json(master_path, master_data)
        print(f"  Saved {master_filename} with {len(all_records)} records.")

    # 4. Cleanup: Move processed fragment files to raw directory
    if files_to_process:
        # Construct raw directory path: ../data/X -> ../data/X/raw
        raw_dir = os.path.join(directory, "raw")
        
        if not os.path.exists(raw_dir):
            try:
                os.makedirs(raw_dir)
            except Exception as e:
                print(f"  Warning: Could not create raw directory {raw_dir}. Files will remain in place. ({e})")
                raw_dir = None

        if raw_dir:
            print(f"  Moving {len(files_to_process)} processed files to {raw_dir}...")
            import shutil
            for fp in files_to_process:
                try:
                    fname = os.path.basename(fp)
                    dest_path = os.path.join(raw_dir, fname)
                    
                    # Handle collision if file already exists in raw (e.g. re-running)
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(fname)
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        dest_path = os.path.join(raw_dir, f"{base}_{timestamp}{ext}")
                    
                    shutil.move(fp, dest_path)
                    print(f"    Moved {fname}")
                except Exception as e:
                    print(f"    Error moving {fp}: {e}")

def main():
    # Process Flow
    process_directory(FLOW_DIR, "FLOW_P", "flow")
    
    # Process Generators
    process_directory(GEN_DIR, "NET_P", "generator")

if __name__ == "__main__":
    main()
