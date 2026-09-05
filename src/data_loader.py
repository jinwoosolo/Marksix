from __future__ import annotations
from pathlib import Path
import io
import pandas as pd
import requests

NUM_COLS = [f'n{i}' for i in range(1,7)]
ALL_NUM_COLS = NUM_COLS + ['extra']
DEFAULT_REMOTE_CSV = 'https://raw.githubusercontent.com/jinwoosolo/Marksix-analyzer/main/marksix.csv'


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=['date', *ALL_NUM_COLS])
    out = df.copy()
    out.columns = [str(c).replace('\ufeff','').strip() for c in out.columns]
    required = ['date', *ALL_NUM_COLS]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    for c in ALL_NUM_COLS:
        out[c] = pd.to_numeric(out[c], errors='coerce')
    out['date_parsed'] = pd.to_datetime(out['date'], errors='coerce')
    out = out.dropna(subset=['date_parsed', *ALL_NUM_COLS])
    valid = out[ALL_NUM_COLS].apply(lambda s: s.between(1,49)).all(axis=1)
    out = out[valid].copy()
    out[ALL_NUM_COLS] = out[ALL_NUM_COLS].astype(int)
    # Each draw should contain 6 distinct main numbers; extra must not duplicate a main number.
    out = out[out[NUM_COLS].nunique(axis=1).eq(6)]
    out = out[~out.apply(lambda r: int(r['extra']) in {int(r[c]) for c in NUM_COLS}, axis=1)]
    out = out.sort_values('date_parsed').drop_duplicates(subset=['date_parsed'], keep='last').reset_index(drop=True)
    return out


def download_legacy_csv(url: str = DEFAULT_REMOTE_CSV, timeout: int = 20) -> pd.DataFrame:
    r = requests.get(url, timeout=timeout, headers={'User-Agent':'Marksix-AI-Lab/2.1'})
    r.raise_for_status()
    return _clean(pd.read_csv(io.BytesIO(r.content)))


def load_data(path: str | Path = 'data/marksix.csv', bootstrap_remote: bool = True) -> pd.DataFrame:
    path = Path(path)
    if path.exists() and path.stat().st_size > 20:
        try:
            return _clean(pd.read_csv(path))
        except Exception:
            pass
    if bootstrap_remote:
        df = download_legacy_csv()
        path.parent.mkdir(parents=True, exist_ok=True)
        df.drop(columns=['date_parsed'], errors='ignore').to_csv(path, index=False, encoding='utf-8-sig')
        return df
    raise FileNotFoundError(f'No valid data found at {path}')
