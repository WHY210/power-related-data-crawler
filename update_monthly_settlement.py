import json
import time
from pathlib import Path
from datetime import datetime, timedelta, date

import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://etp.taipower.com.tw/api/infoboard/settle_value/query"


def build_session() -> requests.Session:
    retry = Retry(
        total=8,
        connect=8,
        read=8,
        backoff_factor=1.2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    s = requests.Session()
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


def fetch_one_day(date_str: str, sleep_sec: float = 0.3, session: requests.Session | None = None):
    session = session or build_session()

    resp = session.get(
        API_URL,
        params={"startDate": date_str},
        timeout=(20, 60),  # (connect timeout, read timeout)
        headers={"User-Agent": "Mozilla/5.0 (compatible; GitHubActionsBot/1.0)"},
    )
    resp.raise_for_status()
    obj = resp.json()

    data = obj.get("data")
    if not isinstance(data, list) or len(data) != 24:
        raise ValueError(f"{date_str} unexpected data format")

    rows = []
    for i, row in enumerate(data):
        out = {"date": date_str, "hour": f"{i:02d}"}
        out.update(row)
        rows.append(out)

    time.sleep(sleep_sec)
    return rows


def month_key(d: date) -> str:
    return d.strftime("%Y-%m")


def monthly_paths(out_dir: Path, d: date):
    mk = month_key(d)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"settlement_{mk}.csv"
    json_path = out_dir / f"settlement_{mk}.json"
    return csv_path, json_path


def load_existing(csv_path: Path) -> pd.DataFrame:
    if csv_path.exists():
        return pd.read_csv(csv_path, dtype={"date": str, "hour": str})
    return pd.DataFrame()


def merge_and_save(df_old: pd.DataFrame, new_rows: list[dict], csv_path: Path, json_path: Path):
    df_new = pd.DataFrame(new_rows)

    if df_old is None or df_old.empty:
        df = df_new
    else:
        df = pd.concat([df_old, df_new], ignore_index=True)

    if "date" not in df.columns or "hour" not in df.columns:
        raise ValueError("Missing 'date' or 'hour' columns in merged dataframe")

    df["date"] = df["date"].astype(str)
    df["hour"] = df["hour"].astype(str).str.zfill(2)

    df.drop_duplicates(subset=["date", "hour"], keep="last", inplace=True)
    df.sort_values(["date", "hour"], inplace=True)

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    records = df.to_dict(orient="records")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)

    return len(df), len(df_new)


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def main(run_date: str, out_dir: str, fallback_yesterday: bool = False):
    d = parse_date(run_date)
    csv_path, json_path = monthly_paths(Path(out_dir), d)

    sess = build_session()

    try:
        print(f"[INFO] fetching {run_date}")
        rows = fetch_one_day(run_date, session=sess)
    except Exception as e:
        if not fallback_yesterday:
            raise
        yd = d - timedelta(days=1)
        yd_str = yd.strftime("%Y-%m-%d")
        print(f"[WARN] failed fetching {run_date}: {e}")
        print(f"[INFO] fallback fetching {yd_str}")
        rows = fetch_one_day(yd_str, session=sess)
        csv_path, json_path = monthly_paths(Path(out_dir), yd)

    df_old = load_existing(csv_path)
    total_rows, new_rows_cnt = merge_and_save(df_old, rows, csv_path, json_path)

    print(f"[DONE] appended {new_rows_cnt} rows; total {total_rows} rows")
    print(f"[DONE] saved CSV : {csv_path}")
    print(f"[DONE] saved JSON: {json_path}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--outdir", default="data", help="output directory")
    ap.add_argument("--fallback-yesterday", action="store_true", help="if today not ready, fetch yesterday")
    args = ap.parse_args()

    main(args.date, args.outdir, args.fallback_yesterday)
