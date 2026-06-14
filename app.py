import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="機構級雙向戰略矩陣", layout="wide")
st.title("🎯 專屬美股戰略儀表板：歷史定錨、基本面與籌碼多維矩陣")
st.caption("數據源：Yahoo Finance | 策略核心：發動前歷史箱體拓展位 + 機構籌碼濾網")

# 1. 核心自選股設定：直接鎖定發動攻擊前的【歷史固定波谷與波高】
# 以你買在 $71.36 的 RKLB 為例，鎖定發動前歷史箱體：低點 56.13，高點 80.00
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
        df = stock.history(period="3mo")
        current_price = df['Close'].iloc[-1]
        
        # 2. 基本面與美股籌碼數據引擎 (yfinance info)
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        inst_held = info.get('institutionalPercentHeld', 0) * 100
        short_float = info.get('shortPercentOfFloat', 0) * 100
        
        # 3. 依據【固定歷史箱體】無情計算天花板與壓力，數據再也不會天天漂移！
        diff = cfg['base_high'] - cfg['base_low']
        ext_1382 = cfg['base_low'] + 1.382 * diff
        ext_1618 = cfg['base_low'] + 1.618 * diff
        ext_2618 = cfg['base_low'] + 2.618 * diff
        
        # 4. 建立人性化顯示標籤
        pe_display = f"{pe_ratio:.1f}x" if pe_ratio else "虧損/無"
        f_pe_display = f"{forward_pe:.1f}x" if forward_pe else "無"
        
        matrix_data.append({
            "📊 股碼": ticker,
            "📈 目前現價": f"${current_price:.2f}",
            "我的戰略目標": f"${cfg['target']:.2f} ({cfg['mode']})",
            "💥 138.2% 減倉點": f"${ext_1382:.2f}",
            "💥 161.8% 停盈點": f"${ext_1618:.2f}",
            "💥 261.8% 終極阻力": f"${ext_2618:.2f}",
            "💵 本益比 (PE)": pe_display,
            "🔮 預期 PE (Forward)": f_pe_display,
            "🛡️ 機構持股比 %": f"{inst_held:.1f}%",
            "🩳 空頭放空比 %": f"{short_float:.1f}%"
        })
    except Exception as e:
        st.error(f"無法載入 {ticker}: {e}")

if matrix_data:
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)
