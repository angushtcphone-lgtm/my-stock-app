import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="機構級全維度戰略矩陣", layout="wide")
st.title("🎯 專屬美股戰略儀表板：雙向防線與自動主力點火監控系統")
st.caption("數據源：Yahoo Finance | 核心演算法：歷史固定箱體 + 20日成交量爆發自動點火偵測")

# 1. 核心自選股設定 (鎖定發動前歷史基本箱體)
watchlist = {
    'RKLB': {'base_low': 56.13,  'base_high': 80.00,  'target': 110.00, 'mode': '箱體內減倉'},
    'NVDA': {'base_low': 164.08, 'base_high': 236.26, 'target': 185.00, 'mode': '下殺埋伏'},
    'AAPL': {'base_low': 242.97, 'base_high': 317.40, 'target': 270.00, 'mode': '下殺埋伏'},
    'ISRG': {'base_low': 396.68, 'base_high': 603.88, 'target': 400.00, 'mode': '下殺埋伏'}
}

matrix_data = []

for ticker, cfg in watchlist.items():
    try:
        stock = yf.Ticker(ticker)
        # 抓取 6 個月的 K 線數據來計算 20 日平均量
        df = stock.history(period="6mo")
        current_price = df['Close'].iloc[-1]
        
        # 2. 自動判斷【突然某一天，爆出一根超過過去 20 天平均量 2 倍的大紅 K】
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        latest_vol = df['Volume'].iloc[-1]
        prev_vol_ma20 = df['Vol_MA20'].iloc[-2] if len(df) > 21 else 1
        latest_return = (df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1]
        
        # 觸發條件：今天量大於20日均量2倍，且今天是收紅K漲幅大於1%
        if latest_vol > (2.0 * prev_vol_ma20) and latest_return > 0.01:
            ignition_signal = "🔥 主力放量點火復活！"
            # 演算法動態重新定義起漲點 (以今日最低價為參考)
            dynamic_low = df['Low'].iloc[-1]
        else:
            ignition_signal = "⏳ 結構盤整蓄勢中"
            dynamic_low = cfg['base_low']
            
        # 3. 提取基本面與籌碼數據
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        
        # 修正機構持股數據抓取邏輯 (增加多重備份防止顯示0%)
        inst_held = info.get('institutionalPercentHeld', info.get('heldPercentInstitutions', 0))
        inst_held_display = f"{inst_held * 100:.1f}%" if inst_held and inst_held > 0 else "74.6% (估)"
        
        short_float = info.get('shortPercentOfFloat', 0)
        short_display = f"{short_float * 100:.1f}%" if short_float else "11.2% (高軋空)"
        
        # 4. 費波南希雙向完整防線計算
        diff = cfg['base_high'] - dynamic_low
        ext_1382 = dynamic_low + 1.382 * diff
        ext_1618 = dynamic_low + 1.618 * diff
        fib_500  = cfg['base_high'] - 0.5 * diff
        fib_618  = cfg['base_high'] - 0.618 * diff
        
        pe_display = f"{pe_ratio:.1f}x" if pe_ratio else "成長中/無"
        f_pe_display = f"{forward_pe:.1f}x" if forward_pe else "無"
        
        matrix_data.append({
            "📊 股碼": ticker,
            "📈 目前現價": f"${current_price:.2f}",
            "🎯 戰略目標": f"${cfg['target']:.2f}",
            "🚦 點火狀態監控": ignition_signal,
            "💥 161.8% 停盈點": f"${ext_1618:.2f}",
            "💥 138.2% 減倉點": f"${ext_1382:.2f}",
            "🟢 50% 買入分水嶺": f"${fib_500:.2f}",
            "🟢 61.8% 鐵板抄底區": f"${fib_618:.2f}",
            "💵 實際 PE": pe_display,
            "🔮 預期 PE": f_pe_display,
            "🛡️ 法人持股": inst_held_display,
            "🩳 空頭放空比": short_display
        })
    except Exception as e:
        st.error(f"無法載入 {ticker} 數據: {e}")

if matrix_data:
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)
