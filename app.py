import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 網頁基礎設定 (強制寬螢幕佈局)
st.set_page_config(page_title="AI 投顧雙向戰略儀表板", layout="wide")
st.title("🚀 專屬美股戰略儀表板與雙向波段提醒系統")
st.caption("即時數據源：Yahoo Finance | 核心戰略：費波南希 120日回調與多頭拓展位")

# 2. 核心獵殺與出清清單設定
watchlist = {
    'RKLB': {'target_buy': 75.0, 'target_sell': 110.0, 'type': 'SELL_TARGET'},
    'NVDA': {'target_buy': 185.0, 'target_sell': 999.0, 'type': 'BUY_TARGET'},
    'AAPL': {'target_buy': 270.0, 'target_sell': 999.0, 'type': 'BUY_TARGET'},
    'ISRG': {'target_buy': 400.0, 'target_sell': 999.0, 'type': 'BUY_TARGET'},
    'AVGO': {'target_buy': 368.0, 'target_sell': 999.0, 'type': 'HOLD'},
    'WMT':  {'target_buy': 120.79, 'target_sell': 999.0, 'type': 'HOLD'}
}

# 3. 抓取數據並同時計算「下墜支撐位」與「噴發拓展賣點」
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="6mo")
    if len(df) > 120:
        df = df.iloc[-120:]
    
    current_price = df['Close'].iloc[-1]
    high_0 = df['High'].max()
    low_100 = df['Low'].min()
    
    diff = high_0 - low_100
    
    # 往下看支撐 (Fibonacci Retracement)
    fib_382 = high_0 - 0.382 * diff
    fib_500 = high_0 - 0.5 * diff
    fib_618 = high_0 - 0.618 * diff
    
    # 往上看賣點 (Fibonacci Extension) - 基於此波段波谷向上拓展
    ext_1382 = low_100 + 1.382 * diff
    ext_1618 = low_100 + 1.618 * diff
    
    return current_price, high_0, low_100, fib_382, fib_500, fib_618, ext_1382, ext_1618

# 4. 收集所有數據並轉換為橫向矩陣
matrix_data = []

for ticker, info in watchlist.items():
    try:
        price, h0, l100, f382, f500, f618, ext_1382, ext_1618 = get_stock_data(ticker)
        
        # 雙向智能訊號判斷
        if info['type'] == 'BUY_TARGET' and price <= info['target_buy']:
            status_signal = "🚨 進入甜蜜買入區！"
        elif info['type'] == 'SELL_TARGET' and price >= info['target_sell']:
            status_signal = "💰 達到計畫出清點！"
        elif price >= ext_1618:
            status_signal = "⚠️ 💥 瘋狂超噴發！演算法極限，無情全開分批停盈！"
        elif price >= ext_1382:
            status_signal = "💥 動能觸頂！138.2% 拓展位，強烈建議落袋減倉！"
        elif info['type'] == 'HOLD':
            status_signal = "🛡️ 核心持股守護中"
        else:
            status_signal = "⏳ 靜態埋伏觀察中"
            
        # 目標欄位人性化呈現
        if info['type'] == 'BUY_TARGET':
            target_display = f"下殺至 ${info['target_buy']:.2f} 買"
        elif info['type'] == 'SELL_TARGET':
            target_display = f"衝高至 ${info['target_sell']:.2f} 賣"
        else:
            target_display = f"底倉成本 ${info['target_buy']:.2f}"

        # 組裝矩陣欄位 (新增兩大賣點預測欄位)
        matrix_data.append({
            "📊 公司股碼": ticker,
            "📈 目前現價": f"${price:.2f}",
            "我的戰略目標": target_display,
            "🎯 雙向行動訊號": status_signal,
            "💥 161.8% 終極停盈點": f"${ext_1618:.2f}",
            "💥 138.2% 獲利減倉點": f"${ext_1382:.2f}",
            "0% 波段高點": f"${h0:.2f}",
            "50% 分水嶺": f"${f500:.2f}",
            "61.8% 鐵板區": f"${f618:.2f}",
            "100% 起漲點": f"${l100:.2f}"
        })
    except Exception as e:
        st.error(f"無法載入 {ticker} 的數據: {e}")

# 5. 渲染大矩陣表格
if matrix_data:
    df_matrix = pd.DataFrame(matrix_data)
    st.dataframe(df_matrix, use_container_width=True, hide_index=True)
