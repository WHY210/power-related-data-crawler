import os
import pandas as pd
import glob
import json
from pathlib import Path

def migrate():
    data_dir = Path("data/taipower_ancillary")
    
    # Find all monthly CSV files
    monthly_files = list(data_dir.glob("settlement_????-??.csv"))
    
    if not monthly_files:
        print("No monthly files found to migrate.")
        return

    print(f"Found {len(monthly_files)} monthly files.")
    
    # Group by year
    files_by_year = {}
    for f in monthly_files:
        # Filename format: settlement_YYYY-MM.csv
        # Extract YYYY
        filename = f.name
        year = filename.split('_')[1].split('-')[0]
        
        if year not in files_by_year:
            files_by_year[year] = []
        files_by_year[year].append(f)
    
    # Process each year
    for year, files in files_by_year.items():
        print(f"Processing year {year} with {len(files)} files...")
        
        dfs = []
        # Check if yearly file already exists and load it to append/merge
        yearly_csv = data_dir / f"settlement_{year}.csv"
        if yearly_csv.exists():
            print(f"  Loading existing yearly file: {yearly_csv}")
            try:
                dfs.append(pd.read_csv(yearly_csv, dtype={"date": str, "hour": str}))
            except Exception as e:
                print(f"  Error reading existing yearly file: {e}")

        # Load monthly files
        for f in files:
            try:
                dfs.append(pd.read_csv(f, dtype={"date": str, "hour": str}))
            except Exception as e:
                print(f"  Error reading {f}: {e}")
        
        if not dfs:
            continue
            
        # Concatenate
        full_df = pd.concat(dfs, ignore_index=True)
        
        # Deduplicate and Sort
        # Ensure date and hour columns exist
        if "date" in full_df.columns and "hour" in full_df.columns:
            full_df["date"] = full_df["date"].astype(str)
            full_df["hour"] = full_df["hour"].astype(str).str.zfill(2)
            
            # Remove duplicates, keeping the last occurrence (assuming newer files might have updates? or just consistent)
            full_df.drop_duplicates(subset=["date", "hour"], keep="last", inplace=True)
            
            full_df.sort_values(by=["date", "hour"], inplace=True)
            
            # Save
            yearly_json = data_dir / f"settlement_{year}.json"
            
            print(f"  Saving merged {year} data ({len(full_df)} rows) to:")
            print(f"    {yearly_csv}")
            print(f"    {yearly_json}")
            
            full_df.to_csv(yearly_csv, index=False, encoding="utf-8-sig")
            
            records = full_df.to_dict(orient="records")
            with open(yearly_json, "w", encoding="utf-8") as jf:
                json.dump(records, jf, ensure_ascii=False)
                
        else:
            print(f"  Skipping {year} - missing date/hour columns.")

    print("Migration complete.")

if __name__ == "__main__":
    migrate()
