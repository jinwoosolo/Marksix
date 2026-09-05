from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from .features import number_features

FEATURE_COLS = ['freq_all','freq_short','freq_medium','trend_short_vs_all','trend_medium_vs_all','gap_log','in_prev_draw']


def build_training_matrix(df: pd.DataFrame, min_history: int = 80, max_targets: int = 1200):
    start = max(min_history, len(df)-max_targets)
    X, y = [], []
    for i in range(start, len(df)):
        hist = df.iloc[:i]
        feats = number_features(hist)
        actual = set(int(x) for x in df.iloc[i][[f'n{k}' for k in range(1,7)]].tolist())
        X.append(feats[FEATURE_COLS])
        y.extend([1 if int(n) in actual else 0 for n in feats['number']])
    if not X:
        raise ValueError('Not enough history for ML training')
    return pd.concat(X, ignore_index=True), np.asarray(y, dtype=int)


def ml_ranking(df: pd.DataFrame, max_targets: int = 1200) -> pd.DataFrame:
    X, y = build_training_matrix(df, max_targets=max_targets)
    model = Pipeline([
        ('scale', StandardScaler()),
        ('clf', LogisticRegression(max_iter=1000, class_weight='balanced', C=0.5))
    ])
    model.fit(X, y)
    cur = number_features(df)
    cur['score'] = model.predict_proba(cur[FEATURE_COLS])[:,1]
    cur = cur.sort_values(['score','number'], ascending=[False,True]).reset_index(drop=True)
    cur['rank'] = np.arange(1,50)
    cur['tier'] = np.where(cur['rank']<=12,'Core',np.where(cur['rank']<=44,'Secondary','Lowest'))
    return cur
