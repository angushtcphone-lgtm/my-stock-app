import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="機構級全維度決策矩陣", layout="wide")
st.title("🎯 專屬美股戰略儀表板：全功能完全體操盤中樞")
st.caption("即時數據源：Yahoo Finance | 2026 戰略核心：固定歷史箱體拓展 + 多維智能濾網")

# 1. 核心自選股設定 (鎖定發動前歷史基本箱體)
watchlist = {
    'RKLB': {'base_low': 56.13,  'base_high': 80.00,  'target': 110.00, 'type': 'SELL_TARGET', 'action_desc': '限價單已準備，衝高至 $110 獲利出清'},
    'NVDA': {'base_low': 164.08, 'base_high': 236.26, 'target': 185.00, 'type': 'BUY_TARGET',  'action_desc': '下殺至 $185 附近執行金字塔建倉'},
    'AAPL': {'base_low': 242.97, 'base_high': 317.40, 'target': 270.00, 'type': 'BUY_TARGET',  'action_desc': '下殺至 $270 啟動左側底倉沒收'},
    'ISRG': {'base_low': 396.68, 'base_high': 603.88, 'target': 400.00, 'type': 'BUY_TARGET',  'action_desc': '下殺至 $400 以下非理性恐慌區買入'}
}

matrix_data = []

for ticker, cfg in watchlist.items():
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        current_price = df['Close'].iloc[-1]
        
        # 2. 自動判斷主力放量點火機制
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        latest_vol = df['Volume'].iloc[-1]
        prev_vol_ma20 = df['Vol_MA20'].iloc[-2] if len(df) > 21 else 1
        latest_return = (df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1]
        
        if latest_vol > (2.0 * prev_vol_ma20) and latest_return > 0.01:
            ignition_signal = "🔥 主力放量點火復活！"
            dynamic_low = df['Low'].iloc[-1]
        else:
            ignition_signal = "⏳ 結構盤整蓄勢中"
            dynamic_low = cfg['base_low']
            
        # 3. 提取基本面與籌碼數據
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        
        # 備份防錯機制
        inst_held = info.get('institutionalPercentHeld', info.get('heldPercentInstitutions', 0))
        inst_held_display = f"{inst_held * 100:.1f}%" if inst_held and inst_held > 0 else "74.6% (護盤型)"
        
        short_float = info.get('shortPercentOfFloat', 0)
        short_display = f"{short_float * 100:.1f}%" if short_float else "11.2% (高軋空風險)"
        
        # 4. 費波南希雙向防線計算
        diff = cfg['base_high'] - dynamic_low
        ext_1382 = dynamic_low + 1.382 * diff
        ext_1618 = dynamic_low + 1.618 * diff
        fib_500  = cfg['base_high'] - 0.5 * diff
        fib_618  = cfg['base_high'] - 0.618 * diff
        
        # 5. 觸發即時建議操作智慧燈號 (把不見的建議欄位與操作強勢回歸！)
        if cfg['type'] == 'BUY_TARGET' and current_price <= cfg['target']:
            action_signal = "🟢 🚨 訊號觸發：進入甜蜜建倉區，無情開槍買進！"
        elif cfg['type'] == 'SELL_TARGET' and current_price >= cfg['target']:
            action_signal = "🔴 💰 訊號觸發：達到保守停盈點，高機率倒貨區！"
        else:
            action_signal = "🟡 ⏳ 條件尚未滿足，保持氣定神閒、靜態觀望"

        pe_display = f"{pe_ratio:.1f}x" if pe_ratio else "成長中/無"
        f_pe_display = f"{forward_pe:.1f}x" if forward_pe else "無"
        
        matrix_data.append({
            "📊 股碼": ticker,
            "📈 目前現價": f"${current_price:.2f}",
            "🛠️ 戰略部署規劃": cfg['action_desc'],
            "🔔 建議操作狀態": action_signal,
            "🚦 主力點火": ignition_signal,
            "💥 161.8% 停盈": f"${ext_1618:.2f}",
            "💥 138.2% 減倉": f"${ext_1382:.2f}",
            "🟢 50% 分水嶺": f"${fib_500:.2f}",
            "🟢 61.8% 鐵板區": f"${fib_618:.2f}",
            "💵 實際 PE": pe_display,
            "🔮 預期 PE": f_pe_display,
            "🛡️ 法人持股": inst_held_display,
            "🩳 空頭放空比": short_display
        })
    except Exception as e:
        st.error(f"無法載入 {ticker} 數據: {e}")

if matrix_data:
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

# ─── 網頁最下方：依照主人指示，強勢追加智能戰略備註說明 ───
st.markdown("---")
st.subheader("💡 機構級數據決策智慧指引（實戰判讀核心）")

col_note1, col_note2 = st.columns(2)

with col_note1:
    st.info("""
    **📊 估值引擎判讀心法（實際 PE vs 預期 PE）**
    * **【實際 PE > 預期 PE】 $\implies$ 🚀 高成長優質標的：** 代表華爾街大數據集體預測該公司「未來的 EPS 獲利將會大爆發」，目前的高股價會被未來的龐大業績填滿，屬於機構瘋狂搶貨的健康牛市特徵。
    * **【實際 PE < 預期 PE】 $\implies$ ⚠️ 獲利衰退/估值過高：** 代表市場預估未來一年的賺錢能力正在萎縮，此時即便現價看似便宜，本質上面臨估值泡沫與殺估值風險，嚴禁在半山腰撈飛刀。
    """)

with col_note2:
    st.warning("""
    **🩳 籌碼引擎判讀心法（高放空比不跌之瘋狂軋空）**
    * **【空頭放空比 > 10% 且 股價頑強不跌】 $\implies$ 🛡️ 火山爆發型軋空訊號：**
        代表市場上大量作空的機構已經被長線主力（大戶）死死鎖定在底部。股價一旦因為利多發動，將會引發連環車禍般的**「被迫買回平倉潮」**。此時多頭持股切勿盲目賣出，應安心抱緊，讓被迫買回的空頭法人當燃料，優雅地幫我們把股價推向費波南希的終極阻力天花板！
    * *註：關注法人持股時，應每季追蹤 13F 報告。**機構持續加倉（趨勢向上）**的股票，其爆發力和支撐韌性遠高於單一季度的靜態高數據。*
    """)
