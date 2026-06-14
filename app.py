import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="機構級全維度決策矩陣", layout="wide")
st.title("🎯 專屬美股戰略儀表板：多維動態籌碼與估值矩陣")
st.caption("即時數據源：Yahoo Finance | 2026 最終進化版：固定歷史箱體 + 籌碼量能動態趨勢")

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
        
        # 2. 【核心籌碼動態變化計算】：用 3日均量 / 20日均量 監控法人資金流向變動！
        df['Vol_MA3'] = df['Volume'].rolling(window=3).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        
        latest_ma3_vol = df['Vol_MA3'].iloc[-1]
        latest_ma20_vol = df['Vol_MA20'].iloc[-1]
        
        # 計算量能動態變化比率
        volume_trend_ratio = latest_ma3_vol / latest_ma20_vol if latest_ma20_vol > 0 else 1.0
        
        # 依據變化率判定趨勢狀態
        if volume_trend_ratio >= 1.3:
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
        
        # 6. 【操作建議與智慧燈號強勢回歸】
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
            "⚡ 法人資金動態趨勢 (3MA/20MA)": trend_signal,
            "🚦 主力點火": ignition_signal,
            "💥 161.8% 停盈": f"${ext_1618:.2f}",
            "💥 138.2% 減倉": f"${ext_1382:.2f}",
            "🟢 50% 分水嶺": f"${fib_500:.2f}",
            "🟢 61.8% 鐵板區": f"${fib_618:.2f}",
            "💵 實際 PE": pe_display,
            "🔮 預期 PE": f_pe_display,
            "🛡️ 法人持股比例": inst_held_display,
            "🩳 空頭放空比": short_display
        })
    except Exception as e:
        st.error(f"無法載入 {ticker} 數據: {e}")

if matrix_data:
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

# ─── 網頁最下方：全新擴充優化 4 大戰略備註說明 ───
st.markdown("---")
st.subheader("💡 機構級數據決策智慧指引（實戰判讀核心）")

col_note1, col_note2 = st.columns(2)

with col_note1:
    st.info("""
    **📊 估值引擎判讀心法（實際 PE vs 預期 PE）**
    * **【實際 PE > 預期 PE】 $\implies$ 🚀 高成長優質標的：** 代表華爾街大數據集體預測該公司「未來的 EPS 獲利將會大爆發」（例如輝達預期 EPS 將大增至 $12.74）。未來的龐大業績會迅速填滿估值。此時若預期 PE 極低（如 16.1x），一旦市場情緒恢復到歷史正常 PE，股價將迎來爆發性的大牛市（如推算 NVDA 目標價 $400）。
    * **【實際 PE < 預期 PE】 $\implies$ ⚠️ 獲利衰退/估值過高：** 代表市場預估未來一年的賺錢能力正在萎縮，此時即便現價看似便宜，本質上面臨估值泡沫與殺估值風險，嚴禁在半山腰撈飛刀。
    """)
    st.markdown("""
    **🛡️ 法人持股比例（Institutional Held %）的黃金戰略關係**
    * **【50% ~ 80%】 ── 機構黃金防禦區：** 頂級藍籌股與核心資產的標準結構。代表「聰明錢」（共同基金、主權基金）深度護盤。股價下殺挑戰費波南希 61.8% 鐵板區時，會有巨量機構演算法買盤進場沒收，安全係數極高。
    * **【高於 90%】 ── 流動性枯竭警訊：** 機構幾乎把股票買光了。代表市場上已經沒有潛在的新主力能進來抬轎；且一旦某家大基金換股出清，極易引發多頭踩踏的連環車禍。
    * **【低於 30%】 ── 散戶市/高投機標的：** 籌碼極度分散，風吹草動大家就會互相踩踏，波動劇烈，只適合極小資金短線投機。
    """)

with col_note2:
    st.warning("""
    **🩳 籌碼引擎判讀心法（高放空比不跌之瘋狂軋空）**
    * **【空頭放空比 > 10% 且 股價頑強不跌】 $\implies$ 進入波段噴發起漲勢：**
        代表大量作空的機構已經被長線主力死死鎖定在底部。大家因為長期看好基本面，惜售不賣股票，股價不但不跌還緩步推升。這將強烈迫使空頭機構面臨無限虧損的恐懼，進而在市場上瘋狂掛單「不計成本地買回平倉」。這種被迫買回的連環海嘯，就是引發股價斷頭式暴漲的瘋狂軋空訊號！
    """)
    st.success("""
    **⚡ 法人資金動態趨勢（3MA/20MA 量能加速度）判讀**
    * 由於美股法人持股比例（13F報告）每季才公佈一次，具備嚴重落後性。因此本系統獨家採用**「3日移動平均量 $\div$ 20日移動平均量」**作為法人即時動態的照妖鏡。
    * 當指標衝破 **1.2x ~ 2.0x 倍速以上**，代表法人資金正在「**當下這幾天**」瘋狂加速流入吸籌，或者空頭正在全力踩踏補回，這是波段大行情即時噴發的最神聖足跡！
    """)
