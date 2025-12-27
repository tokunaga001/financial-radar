# ここから下に今動いてるあなたのレーダーコードを丸ごと貼る
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr

def last_value(obj):
    if isinstance(obj, pd.DataFrame):
        obj = obj.iloc[:,0]
    obj = obj.dropna()
    return obj.iloc[-1] if len(obj) else None

us2y = pdr.DataReader("DGS2", "fred", start="2023-01-01")
us2y["chg10"] = us2y["DGS2"] - us2y["DGS2"].shift(10)
sig_us2y = last_value(us2y["chg10"]) is not None and last_value(us2y["chg10"]) <= -0.50

kre = yf.download("KRE", period="2y", auto_adjust=True, progress=False)
close_kre = kre["Close"] if "Close" in kre else kre.iloc[:,0]
kre["ma200"] = close_kre.rolling(200).mean()
kre["chg20"] = close_kre / close_kre.shift(20) - 1
sig_kre = (
    last_value(close_kre) is not None
    and last_value(kre["ma200"]) is not None
    and last_value(kre["chg20"]) is not None
    and last_value(close_kre) < last_value(kre["ma200"])
    and last_value(kre["chg20"]) <= -0.10
)

jnk = yf.download("JNK", period="2y", auto_adjust=True, progress=False)
close_jnk = jnk["Close"] if "Close" in jnk else jnk.iloc[:,0]
jnk["chg20"] = close_jnk / close_jnk.shift(20) - 1
sig_hy = last_value(jnk["chg20"]) is not None and last_value(jnk["chg20"]) <= -0.08

signals = {"米国債2年金利の急低下": sig_us2y, "米地銀株の崩れ": sig_kre, "信用不安(JNK)": sig_hy}
on = sum(signals.values())

def action_plan(level):
    if level == 0:
        return "🟢Green"
    if level == 1:
        return "🟡Yellow"
    if level == 2:
        return "🟠Orange"
    return "🔴Red"

print("=== 金融崩壊レーダー ===")
print("点灯数:", on, "/3")
for k, v in signals.items():
    print(k, ":", "⚠点灯" if v else "正常")
print("状態:", action_plan(on))
