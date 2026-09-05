import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_loader import download_legacy_csv

if __name__ == '__main__':
    out = Path('data/marksix.csv')
    out.parent.mkdir(parents=True, exist_ok=True)
    df = download_legacy_csv()
    df.drop(columns=['date_parsed'], errors='ignore').to_csv(out, index=False, encoding='utf-8-sig')
    print(f'Saved {len(df):,} validated draws to {out}')
