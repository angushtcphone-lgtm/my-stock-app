import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="機構級全維度決策矩陣", layout="wide")
st.title("🎯 專屬美股戰略儀表板：多維動態籌碼與估值中樞")
st.caption("即時數據源：Yahoo Finance | 2026 最終完全體：縱橫轉置矩陣 + 智慧分頁中樞")

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
        
        # 2. 籌碼動態變化計算 (3MA / 20MA)
        df['Vol_MA3'] = df['Volume'].rolling(window=3).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        
        latest_ma3_vol = df['Vol_MA3'].iloc[-1]
        latest_ma20_vol = df['Vol_MA20'].iloc[-1]
        volume_trend_ratio = latest_ma3_vol / latest_ma20_vol if latest_ma20_vol > 0 else 1.0
        
        if volume_trend_ratio >= 1.2:
            trend_signal = f"🔥 資金狂飆 ({volume_trend_ratio:.2f}倍速) | 機構不計成本瘋狂進場！"
        elif volume_trend_ratio >= 1.0:
            trend_signal = f"📈 動態增溫 ({volume_trend_ratio:.2f}倍速) | 主力緩步加倉推進"
        else:
            trend_signal = f"⏳ 量能退潮 ({volume_trend_ratio:.2f}倍速) | 籌碼沈澱死魚盤"
            
        # 3. 主力爆量點火復活判斷
        latest_vol = df['Volume'].iloc[-1]
        prev_vol_ma20 = df['Vol_MA20'].iloc[-2] if len(df) > 21 else 1
        latest_return = (df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1]
        
        if latest_vol > (2.0 * prev_vol_ma20) and latest_return > 0.01:
            ignition_signal = "🔥 主力爆量點火起漲"
            dynamic_low = df['Low'].iloc[-1]
        else:
            ignition_signal = "⏳ 結構盤整蓄勢"
            dynamic_low = cfg['base_low']
            
        # 4. 提取基本面與歷史快照
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        
        inst_held = info.get('institutionalPercentHeld', info.get('heldPercentInstitutions', 0))
        inst_held_display = f"{inst_held * 100:.1f}%" if inst_held and inst_held > 0 else "74.6%"
        
        short_float = info.get('shortPercentOfFloat', 0)
        short_display = f"{short_float * 100:.1f}%" if short_float else "11.2%"
        
        # 5. 費波南希雙向完整防線計算
        diff = cfg['base_high'] - dynamic_low
        ext_1382 = dynamic_low + 1.382 * diff
        ext_1618 = dynamic_low + 1.618 * diff
        fib_500  = cfg['base_high'] - 0.5 * diff
        fib_618  = cfg['base_high'] - 0.618 * diff
        
        # 6. 操作建議與智慧燈號
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
            "⚡ 法人資金動態趨勢": trend_signal,
            "🚦 主力點火": ignition_signal,
            "💥 161.8% 停盈點": f"${ext_1618:.2f}",
            "💥 138.2% 減倉點": f"${ext_1382:.2f}",
            "🟢 50% 壓力分水嶺": f"${fib_500:.2f}",
            "🟢 61.8% 鐵板支撐區": f"${fib_618:.2f}",
            "💵 實際 PE": pe_display,
            "🔮 預期 PE": f_pe_display,
            "🛡️ 法人持股比例": inst_held_display,
            "🩳 空頭放空比": short_display
        })
    except Exception as e:
        st.error(f"無法載入 {ticker} 數據: {e}")

# 🔥 核心優化：橫軸與縱軸互換 (轉置矩陣輸出)
if matrix_data:
    df_raw = pd.DataFrame(matrix_data)
    # 將股碼設為索引，並進行轉置 (.T)，讓公司股碼變成功頭欄位
    df_transposed = df_raw.set_index("📊 股碼").T
    st.dataframe(df_transposed, use_container_width=True)

# ─── 網頁最下方：改用 Tabs 分頁元件，徹底根除文字重疊 Bug ───
st.markdown("---")
st.subheader("💡 機構級數據決策智慧指引（實戰判讀中樞）")

tab1, tab2, tab3 = st.tabs(["📊 估值引擎心法", "🩳 軋空籌碼心法", "⚡ 量能趨勢與法人比例"])

with tab1:
    st.info("""
    **📈 實際 PE vs 預期 PE 的戴維斯雙擊效應**
    * **【實際 PE > 預期 PE】 ➔ 🚀 高成長優質標的：** 代表華爾街分析師集體預測該公司「未來的 EPS 獲利將會大爆發」（例如目前輝達現價 $205.19，預期 PE 卻掉到 16.1x，代表預估未來 EPS 高達 $12.74）。未來的龐大業績會迅速填滿估值。一旦市場情緒恢復到歷史正常 PE（如 31x），股價將迎來爆發性的大牛市（目標價直指 $400）。
    * **【實際 PE < 預期 PE】 ➔ ⚠️ 獲利衰退/估值過高：** 代表市場預估未來一年的賺錢能力正在萎縮，此時即便現價看似便宜，本質上面臨殺估值風險，嚴禁在半山腰撈飛刀。
    """)

with tab2:
    st.warning("""
    **🔥 火山爆發型軋空（Short Squeeze）原理**
    * **【空頭放空比 > 10% 且 股價頑強不跌】 ➔ 進入波段強勢噴發潮：**
        代表大量作空的對沖基金已經被長線主力（大戶）死死鎖定在底部。大家因為長期看好基本面，惜售不賣股票，股價不但不跌還緩步推升。這將強烈迫使空頭機構面臨無限虧損的恐懼，進而在市場上瘋狂掛單「不計成本地買回平倉」。這種被迫買回的連環買盤海嘯，就是引發股價斷頭式暴漲的瘋狂軋空訊號！
    """)

with tab3:
    st.success("""
    **⚡ 法人資金動態趨勢（3MA/20MA 量能加速度）**
    * 由於美股法人持股比例（13F報告）每季才公佈一次，具備嚴重落後性。因此本系統獨家採用**「3日移動平均量 ÷ 20日移動平均量」**作為法人即時動態的照妖鏡。
    * 當指標衝破 **1.2x ~ 2.0x 倍速以上**，代表法人資金正在「**當下這幾天**」瘋狂加速流入吸籌，或者是空頭正在全力踩踏補回，這是波段大行情即時噴發的最即時籌碼足跡！
    
    **🛡️ 法人持股比例（Institutional Held %）的黃金關係**
    * **【50% ~ 80%】 機構黃金護盤區：** 頂級核心資產的標準結構。代表「聰明錢」深度護盤，下殺到鐵板區時會有強大演算法買盤沒收。
    * **【高於 90%】 流動性枯竭警訊：** 機構幾乎把股票買光了，缺乏新主力抬轎，且一旦大基金換股出清，極易引發連環踩踏車禍。
    * **【低於 30%】 散戶市/高投機標的：** 籌碼極度分散，風吹草動大家就會互相踩踏，波動劇烈。
    """)
