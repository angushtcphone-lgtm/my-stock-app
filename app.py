import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 網頁基礎設定 (強置寬螢幕佈局)
st.set_page_config(page_title="AI 投顧核心戰略儀表板", layout="wide")
st.title("🚀 專屬美股戰略儀表板與即時提醒系統 (矩陣表格版)")
st.caption("即時數據源：Yahoo Finance | 核心戰略：120日費波南希結構與滾動式流水席")

# 2. 核心獵殺清單與戰略設定
watchlist = {
    'RKLB': {'target_buy': 75.0, 'target_sell': 110.0, 'type': 'SELL_TARGET'},
    'NVDA': {'target_buy': 185.0, 'target_sell': 999.0, 'type': 'BUY_TARGET'},
    'AAPL': {'target_buy': 270.0, 'target_sell': 999.0, 'type': 'BUY_TARGET'},
    'ISRG': {'target_buy': 400.0, 'target_sell': 999.0, 'type': 'BUY_TARGET'},
    'AVGO': {'target_buy': 368.0, 'target_sell': 999.0, 'type': 'HOLD'},
    'WMT':  {'target_buy': 120.79, 'target_sell': 999.0, 'type': 'HOLD'}
}

# 3. 抓取數據與計算費波南希函數
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="6mo")
    if len(df) > 120:
        df = df.iloc[-120:]
    
    current_price = df['Close'].iloc[-1]
    high_0 = df['High'].max()
    low_100 = df['Low'].min()
    
    diff = high_0 - low_100
    fib_382 = high_0 - 0.382 * diff
    fib_500 = high_0 - 0.5 * diff
    fib_618 = high_0 - 0.618 * diff
    
    return current_price, high_0, low_100, fib_382, fib_500, fib_618

# 4. 收集所有數據並轉換為橫向矩陣
matrix_data = []

for ticker, info in watchlist.items():
    try:
        price, h0, l100, f382, f500, f618 = get_stock_data(ticker)
        
        # 判斷即時狀態並亮起對應表情符號
        if info['type'] == 'BUY_TARGET' and price <= info['target_buy']:
            status_signal = "🚨 進入甜蜜買入區！"
        elif info['type'] == 'SELL_TARGET' and price >= info['target_sell']:
            status_signal = "💰 達到保守出清點！"
        elif info['type'] == 'HOLD':
            status_signal = "🛡️ 核心持股續抱"
        else:
            status_signal = "⏳ 靜態觀察中"
            
        # 決定目標價欄位要顯示買入還是賣出
        target_display = f"下殺至 ${info['target_buy']:.2f} 買" if info['type'] == 'BUY_TARGET' else f"衝高至 ${info['target_sell']:.2f} 賣"
        if info['type'] == 'HOLD':
            target_display = f"歷史成本 ${info['target_buy']:.2f}"

        # 組裝成橫向的一列數據
        matrix_data.append({
            "📊 公司股碼": ticker,
            "📈 目前現價": f"${price:.2f}",
            "我的戰略目標": target_display,
            "🎯 即時行動訊號": status_signal,
            "0% 波段高點": f"${h0:.2f}",
            "38.2% 初步支撐": f"${f382:.2f}",
            "50% 分水嶺": f"${f500:.2f}",
            "61.8% 鐵板區": f"${f618:.2f}",
            "100% 起漲點": f"${l100:.2f}"
        })
    except Exception as e:
        st.error(f"無法載入 {ticker} 的數據: {e}")

# 5. 將矩陣轉為 DataFrame 並精美呈現
if matrix_data:
    df_matrix = pd.DataFrame(matrix_data)
    
    # 使用 Streamlit 最新的美化表格，並取消 index 欄位讓畫面更乾淨
    st.dataframe(
        df_matrix, 
        use_container_width=True, 
        hide_index=True
    )
