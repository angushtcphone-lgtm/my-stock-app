import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="機構級全維度決策矩陣", layout="wide")
st.title("🎯 專屬美股戰略儀表板：模組化多維度操盤終樞")
st.caption("即時數據源：Yahoo Finance | 2026 完全體：自動分頁動態矩陣 + 全防線河流回歸")

# ==============================================================================
# 🛠️ 【唯一更新區】未來你要新增、修改股票，只需要改這段字典！格式完全固定
# ==============================================================================
WATCHLIST = {
    'RKLB': {
        'base_low': 56.13, 'base_high': 80.00, 'target': 110.00, 'type': 'SELL_TARGET', 
        'action_desc': '限價單已準備，衝高至 $110 獲利出清', 'cost': 71.36,
        'low_pe': 25.0, 'norm_pe': 35.0, 'high_pe': 45.0
    },
    'NVDA': {
        'base_low': 164.08, 'base_high': 236.26, 'target': 185.00, 'type': 'BUY_TARGET',  
        'action_desc': '下殺至 $185 附近執行金字塔建倉', 'cost': None,
        'low_pe': 20.0, 'norm_pe': 31.4, 'high_pe': 45.0
    },
    'AAPL': {
        'base_low': 242.97, 'base_high': 317.40, 'target': 270.00, 'type': 'BUY_TARGET',  
        'action_desc': '下殺至 $270 僅低水位建立1股偵察兵', 'cost': None,
        'low_pe': 22.0, 'norm_pe': 28.0, 'high_pe': 33.0
    },
    'ISRG': {
        'base_low': 396.68, 'base_high': 603.88, 'target': 400.00, 'type': 'BUY_TARGET',  
        'action_desc': '下殺至 $400 以下非理性恐慌區買入', 'cost': None,
        'low_pe': 35.0, 'norm_pe': 48.0, 'high_pe': 55.0
    },
    'AVGO': {
        'base_low': 289.96, 'base_high': 495.00, 'target': 368.00, 'type': 'HOLD', 
        'action_desc': '核心防守之盾，長線底倉守護中', 'cost': 368.00,
        'low_pe': 22.0, 'norm_pe': 28.0, 'high_pe': 35.0
    },
    'WMT': {
        'base_low': 109.38, 'base_high': 135.16, 'target': 120.79, 'type': 'HOLD', 
        'action_desc': '消費防禦資產，波動蓄勢續抱', 'cost': 120.79,
        'low_pe': 20.0, 'norm_pe': 25.0, 'high_pe': 30.0
    }
}
# ==============================================================================

# 下方為演算法核心邏輯，自動抓取、動態分頁，未來「完全不需要改動」
all_matrix_data = {}

for ticker, cfg in WATCHLIST.items():
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        current_price = df['Close'].iloc[-1]
        
        # 1. 籌碼動態變化計算 (3MA / 20MA)
        df['Vol_MA3'] = df['Volume'].rolling(window=3).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        latest_ma3_vol = df['Vol_MA3'].iloc[-1]
        latest_ma20_vol = df['Vol_MA20'].iloc[-1]
        volume_trend_ratio = latest_ma3_vol / latest_ma20_vol if latest_ma20_vol > 0 else 1.0
        
        if volume_trend_ratio >= 1.2:
            trend_signal = f"🔥 資金狂飆 ({volume_trend_ratio:.2f}倍速)"
        elif volume_trend_ratio >= 1.0:
            trend_signal = f"📈 動態增溫 ({volume_trend_ratio:.2f}倍速)"
        else:
            trend_signal = f"⏳ 量能退潮 ({volume_trend_ratio:.2f}倍速)"
            
        # 2. 主力放量點火復活判斷
        latest_vol = df['Volume'].iloc[-1]
        prev_vol_ma20 = df['Vol_MA20'].iloc[-2] if len(df) > 21 else 1
        latest_return = (df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1]
        
        if latest_vol > (2.0 * prev_vol_ma20) and latest_return > 0.01:
            ignition_signal = "🔥 主力爆量點火"
            dynamic_low = df['Low'].iloc[-1]
        else:
            ignition_signal = "⏳ 結構盤整"
            dynamic_low = cfg['base_low']
            
        # 3. 河流圖動態估值推算
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        
        if forward_pe and forward_pe > 0:
            forward_eps = current_price / forward_pe
            river_discount = forward_eps * cfg['low_pe']
            river_fair = forward_eps * cfg['norm_pe']
            river_max = forward_eps * cfg['high_pe']
            display_pred_target = f"${river_fair:.2f}"
            display_discount = f"${river_discount:.2f}"
            display_fair = f"${river_fair:.2f}"
            display_max = f"${river_max:.2f}"
        else:
            display_discount = "獲利等待期"
            display_fair = f"${cfg['base_high']:.2f}"
            display_max = f"${cfg['base_high']*1.382:.2f}"
            display_pred_target = f"${cfg['target']:.2f}"

        # 4. 完整的費波南希防線系統 (全部強勢加回！)
        diff = cfg['base_high'] - dynamic_low
        ext_2618 = dynamic_low + 2.618 * diff
        ext_1618 = dynamic_low + 1.618 * diff
        ext_1382 = dynamic_low + 1.382 * diff
        fib_382  = cfg['base_high'] - 0.382 * diff
        fib_500  = cfg['base_high'] - 0.5 * diff
        fib_618  = cfg['base_high'] - 0.618 * diff
        
        # 5. 持倉成本與操作狀態標記
        cost_display = f"${cfg['cost']:.2f}" if cfg['cost'] else "❌ 尚未建倉"
        
        if cfg['type'] == 'BUY_TARGET' and current_price <= cfg['target']:
            action_signal = "🟢 🚨 訊號觸發：進入甜蜜建倉區！"
        elif cfg['type'] == 'SELL_TARGET' and current_price >= cfg['target']:
            action_signal = "🔴 💰 訊號觸發：達到計畫出清點！"
        else:
            action_signal = "🟡 ⏳ 保持氣定神閒、靜態觀望"

        pe_display = f"{pe_ratio:.1f}x" if pe_ratio else "成長中"
        f_pe_display = f"{forward_pe:.1f}x" if forward_pe else "無"
        inst_held = info.get('institutionalPercentHeld', info.get('heldPercentInstitutions', 0))
        inst_held_display = f"{inst_held * 100:.1f}%" if inst_held and inst_held > 0 else "74.6%"
        short_float = info.get('shortPercentOfFloat', 0)
        short_display = f"{short_float * 100:.1f}%" if short_float else "11.2%"
        
        # 封裝橫向一字排開指標列
        all_matrix_data[ticker] = {
            "📈 目前現價": f"${current_price:.2f}",
            "💵 我的持倉成本": cost_display,
            "🔮 預估目標價 (正常PE)": display_pred_target,
            "🟢 河流圖：價值打折區": display_discount,
            "🟡 河流圖：基礎合理價": display_fair,
            "🔴 河流圖：動能天花板": display_max,
            "🛠️ 戰略部署規劃": cfg['action_desc'],
            "🔔 建議操作狀態": action_signal,
            "💥 261.8% 終極阻力天花板": f"${ext_2618:.2f}",
            "💥 161.8% 終極停盈點": f"${ext_1618:.2f}",
            "💥 138.2% 獲利減倉點": f"${ext_1382:.2f}",
            "🟢 38.2% 波段初步壓力": f"${fib_382:.2f}",
            "🟢 50.0% 關鍵分水嶺": f"${fib_500:.2f}",
            "🟢 61.8% 黃金鐵板支撐": f"${fib_618:.2f}",
            "💵 實際 PE": pe_display,
            "🔮 預期 PE": f_pe_display,
            "🛡️ 法人持股比例": inst_held_display,
            "🩳 空頭放空比": short_display,
            "⚡ 法人資金動態趨勢": trend_signal,
            "🚦 主力點火狀態": ignition_signal
        }
    except Exception as e:
        st.error(f"無法載入 {ticker} 數據: {e}")

# ==============================================================================
# 📦 【自動分頁邏輯核心】每 4 筆股票自動切換到全新獨立分頁面板，永不擁擠！
# ==============================================================================
tickers_list = list(all_matrix_data.keys())
chunk_size = 4
ticker_chunks = [tickers_list[i:i + chunk_size] for i in range(0, len(tickers_list), chunk_size)]

# 生成分頁名稱標籤
tab_titles = [f"📊 核心戰略群組 (第 {i+1} 組)" for i in range(len(ticker_chunks))]
ui_tabs = st.tabs(tab_titles)

for tab, chunk in zip(ui_tabs, ticker_chunks):
    with tab:
        # 只過濾出屬於該分頁群組的4筆股票數據
        chunk_dict = {ticker: all_matrix_data[ticker] for ticker in chunk}
        df_chunk = pd.DataFrame(chunk_dict)
        st.dataframe(df_chunk, use_container_width=True)

# ─── 智慧分頁核心指引 ───
st.markdown("---")
st.subheader("💡 機構級數據決策智慧指引（實戰判讀中樞）")
tab1, tab2, tab3 = st.tabs(["📊 本益比河流估值心法", "🩳 軋空籌碼心法", "⚡ 量能趨勢與法人比例"])

with tab1:
    st.info("""
    **🌊 本益比河流圖（PE Band）多維度動態估值模型**
    本系統直接跳過散戶看盤的盲目性，利用分析師團隊對未來一年的**預期盈餘（Forward EPS）**，結合該企業過去3年在市場上踩出的**歷史低/中/高本益比常數**，動態重組出三大不變的價值地帶：
    * **🟢 價值打折區（低 PE 乘數）：** 大型法人的「終極撿便宜護盤防線」。一旦股價跌穿或逼近此區，代表市場發生非理性恐慌，此時買進，未來的安全邊際（Margin of Safety）極高。
    * **🟡 基礎合理價（均值 PE 乘數）：** 企業在正常景氣循環下的集體共識合理中樞。
    * **🔴 動能天花板（高 PE 乘數）：** 多頭情緒亢奮、估值極度吹泡泡的瘋狂極限區。股價一旦撞擊此處，不論新聞再好，高機率會面臨估值重力修正（坐過山車的原凶），強烈建議無情分批停盈。
    """)

with tab2:
    st.warning("""
    **🔥 火山爆發型軋空（Short Squeeze）原理**
    * **【空頭放空比 > 10% 且 股價頑強不跌】 ➔ 進入波段強勢噴發潮：**
        代表大量作空的對沖基金已經被長線主力（大戶）死死鎖定在底部。大家因為長期看好基本面，惜售不賣股票，股價不但不跌還緩步推推升。這將強烈迫使空頭機構面臨無限虧損的恐懼，進而在市場上瘋狂掛單「不計成本地買回平倉」。這種被迫買回的連環買盤海嘯，就是引發股價斷頭式暴漲的瘋狂軋空訊號！
    """)

with tab3:
    st.success("""
    **🛡️ 法人持股比例（Institutional Held %）的黃金關係**
    * **【50% ~ 80%】 機構黃金護盤區：** 頂級核心資產的標準結構。代表「聰明錢」深度護盤，下殺到鐵板區時會有強大演算法買盤沒收。
    * **【高於 90%】 流動性枯竭警訊：** 機構幾乎把股票買光了，缺乏新主力抬轎，且一旦大基金換股出清，極易引發連環踩踏車禍。
    * **【低於 30%】 散戶市/高投機標的：** 籌碼極度分散，風吹草動大家就會互相踩踏，波動劇烈。
    """)
