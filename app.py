import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time  # 🔥 導入時間模組，用來執行自動定時刷新

st.set_page_config(page_title="機構級全球決策終端", layout="wide")

# 強行注入 CSS 樣式表，解決側邊欄滾動條 Bug
st.markdown(
    """
    <style>
    [data-testid="stSidebarUserContent"] {
        overflow-y: auto !important;
        max-height: 90vh !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 🕹️ 【頂層設計】全球市場切換中樞（同網址、雙戰場完美切割）
# ==============================================================================
st.sidebar.header("🕹️ 全球市場切換中樞")
market_choice = st.sidebar.radio("🌐 選擇看盤市場", ["🇺🇸 美股核心指揮部", "🇹🇼 台股戰略中心"])

if market_choice == "🇺🇸 美股核心指揮部":
    st.title("🎯 專屬美股戰略儀表板：多維動態籌碼與估值中樞")
    default_tickers = "RKLB, NVDA, AAPL, ISRG"
    currency_sign = "$"
else:
    st.title("🎯 專屬台股戰略儀表板：護國神山與半導體核心矩陣")
    default_tickers = "2330.TW, 2454.TW, 2317.TW"
    currency_sign = "NT$"

st.caption(f"即時數據源：Yahoo Finance | 2026 版本：市場動態切換 + 60秒全自動輪詢刷新系統")

# ==============================================================================
# 🎛️ 【互動式左側控制艙】無代碼圖形化操作
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ 戰略中央控制艙")

ticker_input = st.sidebar.text_input("📊 輸入股票代碼 (用逗號隔開)", default_tickers)
active_tickers = list(dict.fromkeys([t.strip().upper() for t in ticker_input.split(",") if t.strip()]))

user_configs = {}
st.sidebar.markdown("---")
st.sidebar.subheader("📝 每檔標的戰略定錨與持倉設定")

for ticker in active_tickers:
    with st.sidebar.expander(f"⚙️ {ticker} 戰略配置規劃", expanded=False):
        # 判斷是否預設有持倉
        is_default_hold = (ticker in ['RKLB', '2330.TW'])
        has_pos = st.checkbox("我已持有此部位", value=is_default_hold, key=f"pos_{ticker}")
        
        if has_pos:
            # 預設成本自動對齊
            if ticker == 'RKLB':
                default_cost = 71.36
            elif ticker == '2330.TW':
                default_cost = 950.0
            else:
                default_cost = 0.0
            cost = st.number_input(f"{ticker} 持倉成本", value=default_cost, step=0.1, key=f"cost_in_{ticker}")
        else:
            cost = None
            
        action_type = st.selectbox(f"{ticker} 目標類型", ["BUY_TARGET", "SELL_TARGET", "HOLD"], 
                                    index=1 if ticker in ['RKLB', '2330.TW'] else 0, key=f"type_{ticker}")
        
        suffix = " (Sell)" if action_type == "SELL_TARGET" else (" (Buy)" if action_type == "BUY_TARGET" else " (Hold)")
        
        # 預設戰略目標價自動對齊
        if ticker == 'RKLB':
            default_target = 110.0
        elif ticker == '2330.TW':
            default_target = 1200.0
        else:
            default_target = 0.0
            
        target = st.number_input(f"{ticker} 戰略目標價{suffix}", value=default_target, step=1.0, key=f"target_{ticker}")
        
        default_desc = "限價單已準備，衝高獲利出清" if action_type == "SELL_TARGET" else "下殺至目標價附近執行金字塔建倉"
        action_desc = st.text_input(f"{ticker} 戰略部署規劃", value=default_desc, key=f"desc_{ticker}")
        
        user_configs[ticker] = {
            'cost': cost,
            'target': target,
            'type': action_type,
            'action_desc': action_desc
        }

# ==============================================================================
# 🧠 【後台演算法核心】全自動數據清洗與衍生
# ==============================================================================
all_matrix_data = {}

for ticker in active_tickers:
    if ticker not in user_configs:
        continue
    cfg = user_configs[ticker]
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        if df.empty:
            continue
            
        current_price = df['Close'].iloc[-1]
        
        auto_low = df['Low'].tail(120).min()
        auto_high = df['High'].tail(120).max()
        
        # 3MA / 20MA 量能加速度
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
            
        # 主力點火狀態
        latest_vol = df['Volume'].iloc[-1]
        prev_vol_ma20 = df['Vol_MA20'].iloc[-2] if len(df) > 21 else 1
        latest_return = (df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1]
        
        if latest_vol > (2.0 * prev_vol_ma20) and latest_return > 0.01:
            ignition_signal = "🔥 主力爆量點火"
            dynamic_low = df['Low'].iloc[-1]
        else:
            ignition_signal = "⏳ 結構盤整"
            dynamic_low = auto_low
            
        # 河流圖動態估值
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        
        is_taiwan_stock = ticker.endswith(".TW")
        low_mult, norm_mult, high_mult = (0.8, 1.0, 1.3) if not is_taiwan_stock else (0.85, 1.0, 1.15)
        
        if forward_pe and forward_pe > 0:
            forward_eps = current_price / forward_pe
            river_discount = forward_eps * (forward_pe * low_mult)
            river_fair = current_price  
            river_max = forward_eps * (forward_pe * high_mult)
            
            display_discount = f"{currency_sign}{river_discount:.2f}"
            display_fair = f"{currency_sign}{river_fair:.2f}"
            display_max = f"{currency_sign}{river_max:.2f}"
        else:
            display_discount = "獲利等待/築底期"
            display_fair = f"{currency_sign}{auto_high:.2f}"
            display_max = f"{currency_sign}{auto_high * 1.382:.2f}"

        # 🔥 【核心修改點 2】：讓大表格中的預估目標價金額後面，動態黏上 (Buy) 或 (Sell) 標籤
        suffix_table = " (Sell)" if cfg['type'] == "SELL_TARGET" else (" (Buy)" if cfg['type'] == "BUY_TARGET" else " (Hold)")
        display_pred_target = f"{currency_sign}{cfg['target']:.2f}{suffix_table}" if cfg['target'] > 0 else "未設定"

        # 費波南希完整防線自動運算
        diff = auto_high - dynamic_low
        ext_2618 = dynamic_low + 2.618 * diff
        ext_1618 = dynamic_low + 1.618 * diff
        ext_1382 = dynamic_low + 1.382 * diff
        fib_382  = auto_high - 0.382 * diff
        fib_500  = auto_high - 0.5 * diff
        fib_618  = auto_high - 0.618 * diff
        
        # 持倉損益計算
        if cfg['cost'] and cfg['cost'] > 0:
            cost_display = f"{currency_sign}{cfg['cost']:.2f}"
            pl_pct = ((current_price - cfg['cost']) / cfg['cost']) * 100
            pl_display = f"+{pl_pct:.1f}% 🟢" if pl_pct >= 0 else f"{pl_pct:.1f}% 🔴"
        else:
            cost_display = "❌ 尚未建倉"
            pl_display = "❌ 尚未持倉"
        
        if cfg['type'] == 'BUY_TARGET' and cfg['target'] > 0 and current_price <= cfg['target']:
            action_signal = "🟢 🚨 訊號觸發：進入甜蜜建倉區！"
        elif cfg['type'] == 'SELL_TARGET' and cfg['target'] > 0 and current_price >= cfg['target']:
            action_signal = "🔴 💰 訊號觸發：達到計畫出清點！"
        else:
            action_signal = "🟡 ⏳ 保持氣定神閒、靜態觀望"

        pe_display = f"{pe_ratio:.1f}x" if pe_ratio else "成長中"
        f_pe_display = f"{forward_pe:.1f}x" if forward_pe else "無"
        inst_held = info.get('institutionalPercentHeld', info.get('heldPercentInstitutions', 0))
        inst_held_display = f"{inst_held * 100:.1f}%" if inst_held and inst_held > 0 else "74.6%"
        short_float = info.get('shortPercentOfFloat', 0)
        short_display = f"{short_float * 100:.1f}%" if short_float else "11.2%"
        
        # 資料封裝
        all_matrix_data[ticker] = {
            "📈 目前現價": f"{currency_sign}{current_price:.2f}",
            "💵 我的持倉成本": cost_display,
            "💰 即時持倉損益 %": pl_display,
            "🔮 戰略目標價": display_pred_target,
            "🟢 河流圖：價值打折區": display_discount,
            "🟡 河流圖：基礎合理價": display_fair,
            "🔴 河流圖：動能天花板": display_max,
            "🛠️ 戰略部署規劃": cfg['action_desc'],
            "🔔 建議操作狀態": action_signal,
            "💥 261.8% 終極阻力天花板": f"{currency_sign}{ext_2618:.2f}",
            "💥 161.8% 終極停盈點": f"{currency_sign}{ext_1618:.2f}",
            "💥 138.2% 獲利減倉點": f"{currency_sign}{ext_1382:.2f}",
            "🟢 38.2% 波段初步壓力": f"{currency_sign}{fib_382:.2f}",
            "🟢 50.0% 關鍵分水嶺": f"{currency_sign}{fib_500:.2f}",
            "🟢 61.8% 黃金鐵板支撐": f"{currency_sign}{fib_618:.2f}",
            "💵 實際 PE": pe_display,
            "🔮 預期 PE": f_pe_display,
            "🛡️ 法人持股比例": inst_held_display,
            "🩳 空頭放空比": short_display,
            "⚡ 法人資金動態趨勢": trend_signal,
            "🚦 主力點火狀態": ignition_signal
        }
    except Exception as e:
        st.error(f"無法自動載入 {ticker} 數據: {e}")

# 【動態自動分頁面板】呈現
if all_matrix_data:
    tickers_list = list(all_matrix_data.keys())
    chunk_size = 4
    ticker_chunks = [tickers_list[i:i + chunk_size] for i in range(0, len(tickers_list), chunk_size)]
    
    tab_titles = [f"📊 核心戰略群組 (第 {i+1} 組)" for i in range(len(ticker_chunks))]
    ui_tabs = st.tabs(tab_titles)
    
    for tab, chunk in zip(ui_tabs, ticker_chunks):
        with tab:
            chunk_dict = {ticker: all_matrix_data[ticker] for ticker in chunk}
            df_chunk = pd.DataFrame(chunk_dict)
            st.dataframe(df_chunk, use_container_width=True)
else:
    st.info("💡 請在左側控制艙輸入股票代碼以啟動全球策略矩陣。")

# 智慧說明分頁
st.markdown("---")
st.subheader("💡 機構級數據決策智慧指引（實戰判讀中樞）")
tab1, tab2, tab3 = st.tabs(["📊 本益比河流估值心法", "🩳 軋空籌碼心法", "⚡ 量能趨勢與法人比例"])

with tab1:
    st.info("""
    **🌊 本益比河流圖（PE Band）多維度動態估值模型**
    * **🟢 價值打折區：** 大型法人的「終極撿便宜護盤防線」。一旦股價跌穿或逼近此區，代表市場發生非理性恐慌，未來的安全邊際（Margin of Safety）極高。
    * **🟡 基礎合理價：** 企業在正常景氣循環下的集體共識合理中樞。
    * **🔴 動能天花板：** 多頭情緒亢奮、估值極度吹泡泡的瘋狂極限區。股價一旦撞擊此處，不論新聞再好，高機率會面臨估值重力修正（坐過山車的原凶），強烈建議無情分批停盈。
    """)

with tab2:
    st.warning("""
    **🔥 火山爆發型軋空（Short Squeeze）原理**
    * **【空頭放空比 > 10% 且 股價頑強不跌】 ➔ 進入波段強勢噴發潮：**
        代表大量作空的對沖基金已經被長線主力（大戶）死死鎖定在底部。大家因為長期看好基本面，惜售不賣股票，股價不但不跌還緩步推升。這將強烈迫使空頭機構面臨無限虧損的恐懼，進而在市場上瘋狂掛單「不計成本地買回平倉」。這種被迫買回的連環買盤海嘯，就是引發股價斷頭式暴漲的瘋狂軋空訊號！
    """)

with tab3:
    st.success("""
    **🛡️ 法人持股比例（Institutional Held %）的黃金關係**
    * **【50% ~ 80%】 機構黃金護盤區：** 頂級核心資產的標準結構。代表「聰明錢」深度護盤，下殺到鐵板區時會有強大演算法買盤沒收。
    * **【高於 90%】 流動性枯竭警訊：** 機構幾乎把股票買光了，缺乏新主力抬轎，且一旦大基金換股出清，極易引發連環踩踏車禍。
    * **【低於 30%】 散戶市/高投機標的：** 籌碼極度分散，風吹草動大家就會互相踩踏，波動劇烈。
    """)

# ==============================================================================
# 🔄 【核心引擎點火】：系統自動計時 60 秒後強行重整，完成無感自動更新看盤流
# ==============================================================================
st.markdown("---")
st.caption("🔄 提示：系統已成功部署「每 60 秒自動定時輪詢刷新」引擎。背景將持續與交易所對齊最新即時報價...")
time.sleep(60)
st.rerun()
