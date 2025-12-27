import os
import csv
from datetime import datetime, timezone
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr

def last_value(obj):
    if isinstance(obj, pd.DataFrame):
        obj = obj.iloc[:, 0]
    obj = obj.dropna()
    return float(obj.iloc[-1]) if len(obj) else None

# ===== シグナル計算 =====
us2y = pdr.DataReader("DGS2", "fred", start="2023-01-01")
us2y["chg10"] = us2y["DGS2"] - us2y["DGS2"].shift(10)
us2y_now = last_value(us2y["DGS2"])
us2y_chg10 = last_value(us2y["chg10"])
sig_us2y = (us2y_chg10 is not None) and (us2y_chg10 <= -0.50)

kre = yf.download("KRE", period="2y", auto_adjust=True, progress=False)
close_kre = kre["Close"] if "Close" in kre else kre.iloc[:, 0]
kre_ma200 = close_kre.rolling(200).mean()
kre_chg20 = (close_kre / close_kre.shift(20) - 1).dropna()
kre_close_now = last_value(close_kre)
kre_ma200_now = last_value(kre_ma200)
kre_chg20_now = last_value(kre_chg20)
sig_kre = (
    kre_close_now is not None and kre_ma200_now is not None and kre_chg20_now is not None
    and (kre_close_now < kre_ma200_now) and (kre_chg20_now <= -0.10)
)

jnk = yf.download("JNK", period="2y", auto_adjust=True, progress=False)
close_jnk = jnk["Close"] if "Close" in jnk else jnk.iloc[:, 0]
jnk_chg20 = (close_jnk / close_jnk.shift(20) - 1).dropna()
jnk_chg20_now = last_value(jnk_chg20)
sig_hy = (jnk_chg20_now is not None) and (jnk_chg20_now <= -0.08)

signals = {
    "米国債2年金利の急低下": bool(sig_us2y),
    "米地銀株の崩れ": bool(sig_kre),
    "信用不安(JNK)": bool(sig_hy),
}
on = sum(signals.values())

def level(on_count: int) -> str:
    return ["🟢Green", "🟡Yellow", "🟠Orange", "🔴Red"][min(on_count, 3)]

status = level(on)

# ===== 出力 =====
print("=== 金融崩壊レーダー ===")
print(f"点灯数: {on}/3")
print("詳細:", signals)
print("状態:", status)

# ===== ログ保存（CSV追記）=====
os.makedirs("results", exist_ok=True)
path = "results/radar_log.csv"

# UTC時刻で保存（安定）。日本時刻にしたければ後で変換できます。
ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")

row = {
    "timestamp_utc": ts,
    "status": status,
    "signals_on": on,
    "us2y_now": us2y_now,
    "us2y_chg10": us2y_chg10,
    "kre_close": kre_close_now,
    "kre_ma200": kre_ma200_now,
    "kre_chg20": kre_chg20_now,
    "jnk_chg20": jnk_chg20_now,
    "sig_us2y": signals["米国債2年金利の急低下"],
    "sig_kre": signals["米地銀株の崩れ"],
    "sig_hy": signals["信用不安(JNK)"],
}

file_exists = os.path.exists(path)
with open(path, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(row.keys()))
    if not file_exists:
        writer.writeheader()
    writer.writerow(row)

print(f"ログに追記しました: {path}")

