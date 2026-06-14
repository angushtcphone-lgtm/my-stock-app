import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="全球決策終端", layout="wide")

# ==============================================================================
# 🎨 【核心美美學】金融終端專屬樣式表
# ==============================================================================
st.markdown(
    '<style>'
    '[data-testid="stSidebarUserContent"] { overflow-y: auto !important; max-height: 90vh !important; }'
    '.execution-card { background-color: #ffffff; border-radius: 8px; padding: 20px; '
    '                  box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 5px solid #d4d4d4; margin-bottom: 15px; }'
    '.card-us-sell { border-top-color: #ff4b4b; background-color: #fffafb; }'
    '.card-us-buy { border-top-color: #00cc66; background-color: #f7fdf9; }'
    '.card-us-info { border-top-color: #0066cc; background-color: #f7faff; }'
    '.card-tw-warn { border-top-color: #ffaa00; background-color: #fffdf5; }'
    '.card-title { font-size: 16px !important; font-weight: bold !important; color: #222222 !important; '
    '              margin-bottom: 12px !important; border-bottom: 1px solid #eeeeee; padding-bottom: 6px; }'
    '.card-body { font-size: 14px !important; line-height: 1.6 !important; color: #555555 !important; }'
    '</style>',
    unsafe_allow_html=True
)

# 全球頂級核心資產歷史本益比常數保險箱
PE_PRESETS = {
    'RKLB': {'low_pe': 25.0, 'norm_pe': 35.0, 'high_pe': 45.0},
    'NVDA': {'low_pe': 20.0, 'norm_pe': 31.4, 'high_pe': 45.0},
    'AAPL': {'low_pe': 22.0, 'norm_pe': 28.0, 'high_pe': 33.0},
    'ISRG': {'low_pe': 35.0, 'norm_pe': 48.0, 'high_pe': 55.0},
    '2330.TW': {'low_pe': 18.0, 'norm_pe': 22.0, 'high_pe': 26.0},
    '2454.TW': {'low_pe': 15.0, 'norm_pe': 18.0, 'high_pe': 22.0},
    '2317.TW': {'low_pe': 10.0, 'norm_pe': 12.0, 'high_pe': 15.0}
}

# 台股中文對應字典
TW_ZH_NAMES = {
    "2330.TW": "台積電", "2454.TW": "聯發科", "2317.TW": "鴻海",
    "2308.TW": "台達電", "2382.TW": "廣達", "2603.TW": "長榮",
    "2344.TW": "華邦電", "2383.TW": "台光電", "2408.TW": "南亞科",
    "3037.TW": "欣興", "3711.TW": "日月光"
}

# 👑 【修正點 4】：從鐵律排序中永久拔除法人持股比與空頭放空比，實現極致乾淨版面
ROW_ORDER = [
    "📈 目前現價", "💵 我的持倉成本", "💰 即時持倉損益 %", "🔮 戰略目標價",
    "🟢 河流圖：價值打折區", "🟡 河流圖：基礎合理價", "🔴 河流圖：動能天花板",
    "🛠️ 戰略部署規劃", "🔔 建議操作狀態", "💥 261.8% 終極阻力天花板",
    "💥 161.8% 終極停盈點", "💥 138.2% 獲利減倉點", "🟢 38.2% 波段初步壓力",
    "🟢 50.0% 關鍵分水嶺", "🟢 61.8% 黃金鐵板支撐", "💵 實際 PE",
    "🔮 預期 PE", "⚡ 法人資金動態趨勢", "🚦 主力點火狀態"
]

# ==============================================================================
# 🕹️ 【頂層設計】全球市場切換中樞
# ==============================================================================
st.sidebar.header("🕹️ 全球市場切換中樞")
market_choice = st.sidebar.radio("🌐 選擇看盤市場", ["🇺🇸 美股核心指揮部", "🇹🇼 台股戰略中心"])

if market_choice == "🇺🇸 美股核心指揮部":
    st.title("🎯 專屬美股戰略儀表板")
    default_tickers = "RKLB, NVDA, AAPL, ISRG"
    currency_sign = "$"
else:
    st.title("🎯 專屬台股戰略儀表板")
    default_tickers = "2330, 3037, 2454, 2317"
    currency_sign = "NT$"

# ==============================================================================
# 📋 【智慧看板】明日開盤冷酷執行中央清單
# ==============================================================================
st.markdown("---")
st.subheader("📋 明日開盤冷酷執行中央清單")

if market_choice == "🇺🇸 美股核心指揮部":
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="execution-card card-us-sell"><div class="card-title">🚀 RKLB ── 獲利套現</div>'
                    '<div class="card-body"><ul><li><b>動作：</b>掛好 <b>$110.00 限價賣出 20 股</b>。</li>'
                    '<li><b>核心：</b>鎖定多頭搶跑動能，完美鎖定 <b>$2,200 現金彈藥</b>！</li></ul></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="execution-card card-us-buy"><div class="card-title">🔥 NVDA ── 世紀抄底</div>'
                    '<div class="card-body"><ul><li><b>動作：</b>跌至 <b>$185.00</b> 觸發警報即開槍。</li>'
                    '<li><b>核心：</b>已實質跌穿河流打折區 ($254.54)，金字塔重倉準備！</li></ul></div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="execution-card card-us-info"><div class="card-title">🍏 AAPL ── 防禦分批</div>'
                    '<div class="card-body"><ul><li><b>動作：</b>跌至 <b>$270.00</b> 時僅建立 <b>1 股偵察兵</b>。</li>'
                    '<li><b>核心：</b>守住合理中樞，大部隊留給價值打折區 ($211.09)！</li></ul></div></div>', unsafe_allow_html=True)
else:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="execution-card card-tw-warn"><div class="card-title">🇹🇼 2330 (台積電) ── 目標見頂</div>'
                    '<div class="card-body"><ul><li><b>動作：</b>明早開盤緊盯 <b>NT$1200.00 (Sell)</b> 停盈線。</li>'
                    '<li><b>核心：</b>波段利潤已達 <b>+143.2% 🟢</b>，隨時啟動移動止損！</li></ul></div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="execution-card card-tw-warn"><div class="card-title">💡 台股半導體 ── 靜態伏擊</div>'
                    '<div class="card-body"><ul><li><b>動作：</b>聯發科 (2454)、鴻海 (2317) 保持靜態觀望。</li>'
                    '<li><b>核心：</b>嚴格靜待拉回到河流打折區或 61.8% 黃金鐵板再開槍。</li></ul></div></div>', unsafe_allow_html=True)

# ==============================================================================
# 🎛️ 【控制艙】無代碼控制面板
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ 戰略中央控制艙")

ticker_input = st.sidebar.text_input("📊 輸入股票代碼 (用逗號隔開)", default_tickers, key=f"tk_in_{market_choice}")
raw_tickers = list(dict.fromkeys([t.strip().upper() for t in ticker_input.split(",") if t.strip()]))

active_tickers = []
for t in raw_tickers:
    if market_choice == "🇹🇼 台股戰略中心":
        if t.isdigit(): active_tickers.append(f"{t}.TW")
        elif t.endswith(".TW"): active_tickers.append(t)
    else:
        if not t.isdigit() and not t.endswith(".TW"): active_tickers.append(t)

user_configs = {}
st.sidebar.markdown("---")
st.sidebar.subheader("📝 每檔標的持倉設定")

for ticker in active_tickers:
    clean_label = ticker.replace(".TW", "")
    with st.sidebar.expander(f"⚙️ {clean_label} 戰略配置規劃", expanded=False):
        has_pos = st.checkbox("我已持有此部位", value=(ticker in ['RKLB', '2330.TW']), key=f"p_{market_choice}_{ticker}")
        
        if has_pos:
            def_cost = 71.36 if 'RKLB' in ticker else (950.0 if '2330' in ticker else 0.0)
            cost = st.number_input(f"持倉成本", value=def_cost, step=0.1, key=f"c_{market_choice}_{ticker}")
        else:
            cost = None
            
        action_type = st.selectbox(f"目標類型", ["BUY_TARGET", "SELL_TARGET", "HOLD"], index=(1 if ticker in ['RKLB', '2330.TW'] else 0), key=f"ty_{market_choice}_{ticker}")
        def_target = 110.0 if 'RKLB' in ticker else (1200.0 if '2330' in ticker else 0.0)
        target = st.number_input(f"戰略目標價", value=def_target, step=1.0, key=f"tg_{market_choice}_{ticker}")
        
        def_desc = "限價單已準備，衝高獲利出清" if action_type == "SELL_TARGET" else "下殺至目標價附近執行金金字塔建倉"
        action_desc = st.text_input(f"部署規劃", value=def_desc, key=f"ds_{market_choice}_{ticker}")
        
        user_configs[ticker] = {'cost': cost, 'target': target, 'type': action_type, 'action_desc': action_desc}

# ==============================================================================
# 🧠 【後台演算法核心】清洗與推導
# ==============================================================================
holding_matrix, watching_matrix, ticker_tv_info = {}, {}, {}

for ticker in active_tickers:
    if ticker not in user_configs: continue
    cfg = user_configs[ticker]
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        if df.empty: continue
            
        current_price = df['Close'].iloc[-1]
        info = stock.info
        
        if market_choice == "🇹🇼 台股戰略中心":
            company_name = TW_ZH_NAMES.get(ticker, info.get('shortName', ticker))
            clean_code = ticker.replace(".TW", "")
            display_key = f"{clean_code}\n({company_name})"
            # 👑 【修正點 2 & 3】：全面移除三大法人與資券按鈕，只保留最純淨的TradingView K線直達連結
            ticker_tv_info[display_key] = {"label": f"📈 {company_name}", "url": f"https://www.tradingview.com/chart/?symbol=TWSE:{clean_code}"}
        else:
            company_name = info.get('shortName', info.get('longName', ticker))
            display_key = f"{ticker}\n({company_name})"
            ticker_tv_info[display_key] = {"label": f"📈 {ticker}", "url": f"https://www.tradingview.com/chart/?symbol={ticker}"}
        
        df['Vol_MA3'] = df['Volume'].rolling(window=3).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        v_ratio = df['Vol_MA3'].iloc[-1] / df['Vol_MA20'].iloc[-1] if df['Vol_MA20'].iloc[-1] > 0 else 1.0
        trend_signal = f"🔥 資金狂飆 ({v_ratio:.2f}倍速)" if v_ratio >= 1.2 else (f"📈 動態增溫 ({v_ratio:.2f}倍速)" if v_ratio >= 1.0 else f"⏳ 量能退潮 ({v_ratio:.2f}倍速)")
            
        latest_vol = df['Volume'].iloc[-1]
        prev_vol_ma20 = df['Vol_MA20'].iloc[-2] if len(df) > 21 else 1
        latest_return = (df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1]
        ignition_signal = "🔥 主力爆量點火" if (latest_vol > (2.0 * prev_vol_ma20) and latest_return > 0.01) else "⏳ 結構盤整"
        
        pe_ratio, forward_pe = info.get('trailingPE', None), info.get('forwardPE', None)
        preset = PE_PRESETS.get(ticker, None)
        
        if preset:
            low_pe, norm_pe, high_pe = preset['low_pe'], preset['norm_pe'], preset['high_pe']
            f_pe = forward_pe if (forward_pe and forward_pe > 0) else (pe_ratio if pe_ratio else norm_pe)
            f_eps = current_price / f_pe if f_pe > 0 else (current_price / norm_pe)
            river_discount = f_eps * low_pe
            river_fair = f_eps * norm_pe
            river_max = f_eps * high_pe
            dynamic_low = df['Low'].iloc[-1] if ignition_signal == "🔥 主力爆量點火" else df['Low'].tail(120).min()
        else:
            # 👑 【修正點 1】：欣興估值防爆手術！引入分位數去噪模型，徹底沒收單日髒數據引發的千元天價
            auto_low = df['Close'].quantile(0.05)
            auto_high = df['Close'].quantile(0.95)
            river_discount = auto_low * 0.90
            river_fair = (auto_low + auto_high) / 2
            river_max = auto_high * 1.10
            dynamic_low = df['Low'].iloc[-1] if ignition_signal == "🔥 主力爆量點火" else auto_low

        display_discount = f"{currency_sign}{river_discount:.2f}"
        display_fair = f"{currency_sign}{river_fair:.2f}"
        display_max = f"{currency_sign}{river_max:.2f}"

        suffix_table = " (Sell)" if cfg['type'] == "SELL_TARGET" else (" (Buy)" if cfg['type'] == "BUY_TARGET" else " (Hold)")
        display_pred_target = f"{currency_sign}{cfg['target']:.2f}{suffix_table}" if cfg['target'] > 0 else "未設定"

        # 費波南希運算 (以去噪後的動態低點重新定錨)
        auto_high_fib = df['High'].tail(120).max() if not preset else df['High'].tail(120).max()
        diff = auto_high_fib - dynamic_low
        ext_2618, ext_1618, ext_1382 = dynamic_low + 2.618 * diff, dynamic_low + 1.1618 * diff, dynamic_low + 1.382 * diff
        fib_382, fib_500, fib_618  = auto_high_fib - 0.382 * diff, auto_high_fib - 0.5 * diff, auto_high_fib - 0.618 * diff
        
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
            "📈 目前現價": f"{currency_sign}{current_price:.2f}", "💵 我的持倉成本": cost_display, "💰 即時持倉損益 %": pl_display,
            "🔮 戰略目標價": display_pred_target, "🟢 河流圖：價值打折區": display_discount, "🟡 河流圖：基礎合理價": display_fair,
            "🔴 河流圖：動能天花板": display_max, "🛠️ 戰略部署規劃": cfg['action_desc'], "🔔 建議操作狀態": action_signal,
            "💥 261.8% 終極阻力天花板": f"{currency_sign}{ext_2618:.2f}", "💥 161.8% 終極停盈點": f"{currency_sign}{ext_1618:.2f}",
            "💥 138.2% 獲利減倉點": f"{currency_sign}{ext_1382:.2f}", "🟢 38.2% 波段初步壓力": f"{currency_sign}{fib_382:.2f}",
            "🟢 50.0% 關鍵分水嶺": f"{currency_sign}{fib_500:.2f}", "🟢 61.8% 黃金鐵板支撐": f"{currency_sign}{fib_618:.2f}",
            "💵 實際 PE": f"{pe_ratio:.1f}x" if pe_ratio else "成長中", "🔮 預期 PE": f"{forward_pe:.1f}x" if forward_pe else "無",
            "⚡ 法人資金動態趨勢": trend_signal, "🚦 主力點火狀態": ignition_signal
        }
    except Exception as e:
        st.error(f"無法自動載入 {ticker} 數據: {e}")

# ==============================================================================
# 📦 【雙軌流全自動分頁阻斷器】與分頁內部按鈕渲染
# ==============================================================================
holding_keys = list(holding_matrix.keys())
holding_chunks = [holding_keys[i:i + 4] for i in range(0, len(holding_keys), 4)]

watching_keys = list(watching_matrix.keys())
watching_chunks = [watching_keys[i:i + 4] for i in range(0, len(watching_keys), 4)]

tab_titles = []
for i in range(len(holding_chunks)): tab_titles.append(f"🛡️ 核心主力持倉 (組 {i+1})")
for i in range(len(watching_chunks)): tab_titles.append(f"⏳ 戰略觀察伏擊 (組 {i+1})")

if tab_titles:
    ui_tabs = st.tabs(tab_titles)
    current_tab_idx = 0
    
    for i, chunk in enumerate(holding_chunks):
        with ui_tabs[current_tab_idx]:
            # 👑 【修正點 2】：恢復為最受好評的 4 欄等寬極簡乾淨 K 線快捷按鈕配置
            st.caption("📈 K線圖 (點擊直達 TradingView)")
            cols_btn = st.columns(4)
            for idx, display_key in enumerate(chunk):
                if display_key in ticker_tv_info:
                    with cols_btn[idx]: st.link_button(ticker_tv_info[display_key]["label"], ticker_tv_info[display_key]["url"], use_container_width=True)
            st.markdown("") 
            chunk_dict = {k: holding_matrix[k] for k in chunk}
            st.dataframe(pd.DataFrame(chunk_dict).reindex(ROW_ORDER), use_container_width=True)
        current_tab_idx += 1
        
    for i, chunk in enumerate(watching_chunks):
        with ui_tabs[current_tab_idx]:
            # 👑 【修正點 2】：恢復為最受好評的 4 欄等寬極簡乾淨 K 線快捷按鈕配置
            st.caption("📈 K線圖 (點擊直達 TradingView)")
            cols_btn = st.columns(4)
            for idx, display_key in enumerate(chunk):
                if display_key in ticker_tv_info:
                    with cols_btn[idx]: st.link_button(ticker_tv_info[display_key]["label"], ticker_tv_info[display_key]["url"], use_container_width=True)
            st.markdown("") 
            chunk_dict = {k: watching_matrix[k] for k in chunk}
            st.dataframe(pd.DataFrame(chunk_dict).reindex(ROW_ORDER), use_container_width=True)
        current_tab_idx += 1
else:
    st.info("💡 請在左側控制艙輸入股票代碼以啟動全球策略矩陣。")

# 智慧指引
st.markdown("---")
st.subheader("💡 機構級數據決策智慧指引")
tab_gui1, tab_gui2, tab_gui3 = st.tabs(["📊 本益比河流估值心法", "🩳 軋空籌碼心法", "⚡ 量能趨勢與法人比例"])

with tab_gui1:
    st.info("📊 本益比河流圖模型：🟢價值打折區為長線安全邊際；🟡基礎合理價為共識中樞；🔴動能天花板強烈建議分批停盈。")
with tab_gui2:
    st.warning("🔥 火山爆發型軋空：當空頭放空比 > 10% 且股價頑強不跌，將迫使空頭不計成本買回平倉，引發暴漲！")
with tab_gui3:
    st.success("🛡️ 法人持股比例：50%~80% 屬於法人深度護盤的核心資產，流動性健全且下殺時具備上演算法接盤護體。")

# ==============================================================================
# 🔄 【前端無感刷新】利用 HTML Meta 標籤重整
# ==============================================================================
st.markdown("---")
st.components.v1.html('<meta http-equiv="refresh" content="60">', height=0)
st.caption("🔄 雷達運作中：系統已切換為「瀏覽器非阻塞型 60 秒定時刷新機制」，全功能安全對齊最新行情...")
