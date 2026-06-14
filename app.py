import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

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

# 全球頂級核心資產「歷史本益比常數保險箱」，確保河流圖估值絕對精準不漂移
PE_PRESETS = {
    'RKLB': {'low_pe': 25.0, 'norm_pe': 35.0, 'high_pe': 45.0},
    'NVDA': {'low_pe': 20.0, 'norm_pe': 31.4, 'high_pe': 45.0},
    'AAPL': {'low_pe': 22.0, 'norm_pe': 28.0, 'high_pe': 33.0},
    'ISRG': {'low_pe': 35.0, 'norm_pe': 48.0, 'high_pe': 55.0},
    '2330.TW': {'low_pe': 18.0, 'norm_pe': 22.0, 'high_pe': 26.0},
    '2454.TW': {'low_pe': 15.0, 'norm_pe': 18.0, 'high_pe': 22.0},
    '2317.TW': {'low_pe': 10.0, 'norm_pe': 12.0, 'high_pe': 15.0}
}

# 台股中文自訂對應字典
TW_ZH_NAMES = {
    "2330.TW": "台積電",
    "2454.TW": "聯發科",
    "2317.TW": "鴻海",
    "2308.TW": "台達電",
    "2382.TW": "廣達",
    "2603.TW": "長榮"
}

# 絕對鐵律縱向排版順序，強制所有市場與分頁列順序完美統一
ROW_ORDER = [
    "📈 目前現價",
    "💵 我的持倉成本",
    "💰 即時持倉損益 %",
    "🔮 戰略目標價",
    "🟢 河流圖：價值打折區",
    "🟡 河流圖：基礎合理價",
    "🔴 河流圖：動能天花板",
    "🛠️ 戰略部署規劃",
    "🔔 建議操作狀態",
    "💥 261.8% 終極阻力天花板",
    "💥 161.8% 終極停盈點",
    "💥 138.2% 獲利減倉點",
    "🟢 38.2% 波段初步壓力",
    "🟢 50.0% 關鍵分水嶺",
    "🟢 61.8% 黃金鐵板支撐",
    "💵 實際 PE",
    "🔮 預期 PE",
    "🛡️ 法人持股比例",
    "🩳 空頭放空比",
    "⚡ 法人資金動態趨勢",
    "🚦 主力點火狀態"
]

# ==============================================================================
# 🕹️ 【頂層設計】全球市場切換中樞
# ==============================================================================
st.sidebar.header("🕹️ 全球市場切換中樞")
market_choice = st.sidebar.radio("🌐 選擇看盤市場", ["🇺🇸 美股核心指揮部", "🇹🇼 台股戰略中心"])

if market_choice == "🇺🇸 美股核心指揮部":
    st.title("🎯 專屬美股戰略儀表板：多維動態籌碼與估值中樞")
    default_tickers = "RKLB, NVDA, AAPL, ISRG"
    currency_sign = "$"
else:
    st.title("🎯 專屬台股戰略儀表板：護國神山與半導體核心矩陣")
    default_tickers = "2330, 2454, 2317"
    currency_sign = "NT$"

# ==============================================================================
# 📋 【強勢回歸】：明日開盤冷酷執行中央清單 (依據不同市場動態呈現核心執行重點)
# ==============================================================================
st.markdown("---")
st.subheader("📋 明日開盤冷酷執行中央清單")

if market_choice == "🇺🇸 美股核心指揮部":
    col_exe1, col_exe2, col_exe3 = st.columns(3)
    with col_exe1:
        st.error("""
        **🚀 RKLB (火箭實驗室) ── 獲利套現**
        * **計畫動作：** 開盤前直接掛好 **$110.00 限價賣出 20 股**。
        * **戰略核心：** 鎖定 Nasdaq-100 指數基金搶跑吸籌的瘋狂動能，在半山腰優雅停盈，死死鎖定利潤並換回 **$2,200 現金彈藥**！
        """)
    with col_exe2:
        st.success("""
        **🔥 NVDA (輝達) ── 世紀抄底**
        * **計畫動作：** 設定 TradingView 價格警報，跌至 **$185.00** 無情開槍。
        * **戰略核心：** 目前現價 ($205.19) 已實質跌穿河流圖打折區 ($254.54)，屬於非理性超跌。若觸及 $185 鐵板區，執行金字塔重倉建倉！
        """)
    with col_exe3:
        st.info("""
        **🍏 AAPL (蘋果) ── 防禦分批**
        * **計畫動作：** 跌至 **$270.00** 觸發時，僅投入低水位建立 **1 股偵察兵底倉**。
        * **戰略核心：** $270 剛好卡在合理價 ($268.66) 與技術面鐵板 ($271.40) 的雙重共振點。合理不等於便宜，控制低水位，大部隊留給真正的價值打折區 ($211.09)！
        """)
else:
    col_exe1, col_exe2 = st.columns(2)
    with col_exe1:
        st.error("""
        **🇹🇼 2330 (台積電) ── 終極目標見頂**
        * **計畫動作：** 現價已飆至 NT$2310.00，實質觸發戰略合理價。明早開盤緊盯 **NT$1200.00 (Sell)** 保守停盈防守線。
        * **戰略核心：** 持倉損益已高達 **+143.2% 🟢**！隨時做好跟蹤止損準備，拒絕讓驚人利潤坐過山車。
        """)
    with col_exe2:
        st.warning("""
        **💡 台股半導體觀測 ── 靜態伏擊**
        * **計畫動作：** 聯發科 (2454)、鴻海 (2317) 目前處於 **⏳ 靜態伏擊觀察中**。
        * **戰略核心：** 嚴格靜待它們拉回到河流圖價值打折區或 61.8% 黃金鐵板支撐區時，再行啟動無情開槍計劃。
        """)

# ==============================================================================
# 🎛️ 【互動式左側控制艙】無代碼圖形化操作
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ 戰略中央控制艙")

ticker_input = st.sidebar.text_input("📊 輸入股票代碼 (用逗號隔開)", default_tickers, key=f"ticker_in_{market_choice}")
raw_tickers = list(dict.fromkeys([t.strip().upper() for t in ticker_input.split(",") if t.strip()]))

# 🔥 【終極修復點 1】：冷酷市場隔離盾！徹底阻斷跨市場代碼漏網之魚（100% 蒸發台股中的美股ISRG）
active_tickers = []
for t in raw_tickers:
    if market_choice == "🇹🇼 台股戰略中心":
        if t.isdigit():
            active_tickers.append(f"{t}.TW")
        elif t.endswith(".TW"):
            active_tickers.append(t)
    else:
        if not t.isdigit() and not t.endswith(".TW"):
            active_tickers.append(t)

user_configs = {}
st.sidebar.markdown("---")
st.sidebar.subheader("📝 每檔標的戰略定錨與持倉設定")

for ticker in active_tickers:
    clean_label = ticker.replace(".TW", "")
    with st.sidebar.expander(f"⚙️ {clean_label} 戰略配置規劃", expanded=False):
        
        is_default_hold = (ticker in ['RKLB', '2330.TW'])
        has_pos = st.checkbox("我已持有此部位", value=is_default_hold, key=f"pos_{market_choice}_{ticker}")
        
        if has_pos:
            if 'RKLB' in ticker:
                default_cost = 71.36
            elif '2330' in ticker:
                default_cost = 950.0
            else:
                default_cost = 0.0
            cost = st.number_input(f"{clean_label} 持倉成本", value=default_cost, step=0.1, key=f"cost_in_{market_choice}_{ticker}")
        else:
            cost = None
            
        action_type = st.selectbox(f"{clean_label} 目標類型", ["BUY_TARGET", "SELL_TARGET", "HOLD"], 
                                    index=1 if ticker in ['RKLB', '2330.TW'] else 0, key=f"type_{market_choice}_{ticker}")
        
        suffix = " (Sell)" if action_type == "SELL_TARGET" else (" (Buy)" if action_type == "BUY_TARGET" else " (Hold)")
        
        if 'RKLB' in ticker:
            default_target = 110.0
        elif '2330' in ticker:
            default_target = 1200.0
        else:
            default_target = 0.0
            
        target = st.number_input(f"{clean_label} 戰略目標價{suffix}", value=default_target, step=1.0, key=f"target_{market_choice}_{ticker}")
        default_desc = "限價單已準備，衝高獲利出清" if action_type == "SELL_TARGET" else "下殺至目標價附近執行金字塔建倉"
        action_desc = st.text_input(f"{clean_label} 戰略部署規劃", value=default_desc, key=f"desc_{market_choice}_{ticker}")
        
        user_configs[ticker] = {
            'cost': cost,
            'target': target,
            'type': action_type,
            'action_desc': action_desc
        }

# ==============================================================================
# 🧠 【後台演算法核心】全自動數據清洗與衍生
# ==============================================================================
holding_matrix = {}
watching_matrix = {}
ticker_tv_info = {} 

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
        
        info = stock.info
        if market_choice == "🇹🇼 台股戰略中心":
            company_name = TW_ZH_NAMES.get(ticker, info.get('shortName', ticker))
            clean_code = ticker.replace(".TW", "")
            display_key = f"{clean_code}\n({company_name})"
            tv_url = f"https://www.tradingview.com/chart/?symbol=TWSE:{clean_code}"
            btn_label = f"📈 {company_name}" 
        else:
            company_name = info.get('shortName', info.get('longName', ticker))
            display_key = f"{ticker}\n({company_name})"
            tv_url = f"https://www.tradingview.com/chart/?symbol={ticker}"
            btn_label = f"📈 {ticker}" 
            
        ticker_tv_info[display_key] = {"label": btn_label, "url": tv_url}
        
        # 3MA / 20MA 量能加速度
        df['Vol_MA3'] = df['Volume'].rolling(window=3).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        volume_trend_ratio = df['Vol_MA3'].iloc[-1] / df['Vol_MA20'].iloc[-1] if df['Vol_MA20'].iloc[-1] > 0 else 1.0
        
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
            
        # 🔥 【核心優化點】：精準恢復 NVDA 400x 估值算法！鎖定歷史本益比區間
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        
        preset = PE_PRESETS.get(ticker, None)
        if preset:
            low_pe = preset['low_pe']
            norm_pe = preset['norm_pe']
            high_pe = preset['high_pe']
        else:
            base_pe = pe_ratio if (pe_ratio and pe_ratio > 0) else (forward_pe if forward_pe else 30.0)
            low_mult, norm_mult, high_mult = (0.65, 1.0, 1.4) if market_choice == "🇺🇸 美股核心指揮部" else (0.85, 1.0, 1.2)
            low_pe = base_pe * low_mult
            norm_pe = base_pe * norm_mult
            high_pe = base_pe * high_mult
            
        if forward_pe and forward_pe > 0:
            forward_eps = current_price / forward_pe
            river_discount = forward_eps * low_pe
            river_fair = forward_eps * norm_pe
            river_max = forward_eps * high_pe
            
            display_discount = f"{currency_sign}{river_discount:.2f}"
            display_fair = f"{currency_sign}{river_fair:.2f}"
            display_max = f"{currency_sign}{river_max:.2f}"
        else:
            display_discount = "獲利等待/築底期"
            display_fair = f"{currency_sign}{auto_high:.2f}"
            display_max = f"{currency_sign}{auto_high * 1.382:.2f}"

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
        
        # 持倉與觀察分群數據封裝
        cost_display = f"{currency_sign}{cfg['cost']:.2f}" if cfg['cost'] else "❌ 尚未建倉"
        if cfg['cost'] and cfg['cost'] > 0:
            pl_pct = ((current_price - cfg['cost']) / cfg['cost']) * 100
            pl_display = f"+{pl_pct:.1f}% 🟢" if pl_pct >= 0 else f"{pl_pct:.1f}% 🔴"
            action_signal = "🔴 💰 達到計畫出清點！" if cfg['type'] == 'SELL_TARGET' and current_price >= cfg['target'] else "🟡 ⏳ 核心持股續抱中"
        else:
            pl_display = "❌ 尚未持倉"
            action_signal = "🟢 🚨 進入甜蜜建倉區！" if cfg['type'] == 'BUY_TARGET' and cfg['target'] > 0 and current_price <= cfg['target'] else "🟡 ⏳ 靜態伏擊觀察中"
            
        target_map = holding_matrix if cfg['cost'] else watching_matrix
        target_map[display_key] = {
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
            "💵 實際 PE": f"{pe_ratio:.1f}x" if pe_ratio else "成長中",
            "🔮 預期 PE": f"{forward_pe:.1f}x" if forward_pe else "無",
            "🛡️ 法人持股比例": f"{info.get('institutionalPercentHeld', 0)*100:.1f}%",
            "🩳 空頭放空比": f"{info.get('shortPercentOfFloat', 0)*100:.1f}%",
            "⚡ 法人資金動態趨勢": trend_signal,
            "🚦 主力點火狀態": ignition_signal
        }
    except Exception as e:
        st.error(f"無法自動載入 {ticker} 數據: {e}")

# ==============================================================================
# 📦 【雙軌流全自動分頁阻斷器】與分頁內部按鈕
# ==============================================================================
holding_keys = list(holding_matrix.keys())
holding_chunks = [holding_keys[i:i + 4] for i in range(0, len(holding_keys), 4)]

watching_keys = list(watching_matrix.keys())
watching_chunks = [watching_keys[i:i + 4] for i in range(0, len(watching_keys), 4)]

tab_titles = []
for i in range(len(holding_chunks)):
    tab_titles.append(f"🛡️ 核心主力持倉 (組 {i+1})")
for i in range(len(watching_chunks)):
    tab_titles.append(f"⏳ 戰略觀察伏擊 (組 {i+1})")

if tab_titles:
    ui_tabs = st.tabs(tab_titles)
    current_tab_idx = 0
    
    # 渲染持倉分頁
    for i, chunk in enumerate(holding_chunks):
        with ui_tabs[current_tab_idx]:
            st.caption("📈 K線圖 (點擊直達 TradingView)")
            cols_btn = st.columns(4)
            for idx, display_key in enumerate(chunk):
                if display_key in ticker_tv_info:
                    with cols_btn[idx]:
                        st.link_button(ticker_tv_info[display_key]["label"], ticker_tv_info[display_key]["url"], use_container_width=True)
            st.markdown("") 
            
            chunk_dict = {k: holding_matrix[k] for k in chunk}
            df_final = pd.DataFrame(chunk_dict).reindex(ROW_ORDER)
            st.dataframe(df_final, use_container_width=True)
        current_tab_idx += 1
        
    # 渲染觀察分頁
    for i, chunk in enumerate(watching_chunks):
        with ui_tabs[current_tab_idx]:
            st.caption("📈 K線圖 (點擊直達 TradingView)")
            cols_btn = st.columns(4)
            for idx, display_key in enumerate(chunk):
                if display_key in ticker_tv_info:
                    with cols_btn[idx]:
                        st.link_button(ticker_tv_info[display_key]["label"], ticker_tv_info[display_key]["url"], use_container_width=True)
            st.markdown("") 
            
            chunk_dict = {k: watching_matrix[k] for k in chunk}
            df_final = pd.DataFrame(chunk_dict).reindex(ROW_ORDER)
            st.dataframe(df_final, use_container_width=True)
        current_tab_idx += 1
else:
    st.info("💡 請在左側控制艙輸入股票代碼以啟動全球策略矩陣。")

# 機構智慧指引
st.markdown("---")
st.subheader("💡 機構級數據決策智慧指引（實戰判讀中樞）")
tab1, tab2, tab3 = st.tabs(["📊 本益比河流估值心法", "🩳 軋空籌碼心法", "⚡ 量能趨勢與法人比例"])

with tab1:
    st.info("""
    **🌊 本益比河流圖（PE Band）多維度動態估值模型**
    * **🟢 價值打折區：** 大型法人的「終極撿便宜護盤防線」。一旦股價跌穿或逼近此區，代表市場發生非理性恐慌，未來的安全邊際（Margin of Safety）極高。
    * **🟡 基礎合理價：** 企業在正常景氣循環下的集體共識合理中樞。
    * **🔴 動能天花板：** 多頭情緒亢奮、估值極度吹泡泡的瘋狂極限區。股價一旦撞擊此處，不論新聞再好，高機率會面臨估值重力修正，強烈建議無情分批停盈。
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
    * **【低於 30%】 散戶市/高投機標的：** 籌碼極度分散，風吹角步大家就會互相踩踏，波動劇烈。
    """)

# 60秒自動輪詢刷新
st.markdown("---")
time.sleep(60)
st.rerun()
