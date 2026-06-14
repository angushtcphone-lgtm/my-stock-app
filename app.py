import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="機構級全球決策終端", layout="wide")

# ==============================================================================
# 🎨 【終極美學】注入頂級金融終端專屬 CSS 樣式表
# ==============================================================================
st.markdown(
    '<style>'
    '/* 修正側邊欄滾動條 Bug */'
    '[data-testid="stSidebarUserContent"] {'
    '    overflow-y: auto !important;'
    '    max-height: 90vh !important;'
    '}'
    '/* 自訂機構級極簡戰略卡片樣式 */'
    '.execution-card {'
    '    background-color: #ffffff;'
    '    border-radius: 8px;'
    '    padding: 20px;'
    '    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);'
    '    border-top: 5px solid #d4d4d4;'
    '    margin-bottom: 15px;'
    '    width: 100%;'
    '}'
    '.card-us-sell { border-top-color: #ff4b4b; background-color: #fffafb; }'
    '.card-us-buy { border-top-color: #00cc66; background-color: #f7fdf9; }'
    '.card-us-info { border-top-color: #0066cc; background-color: #f7faff; }'
    '.card-tw-warn { border-top-color: #ffaa00; background-color: #fffdf5; }'
    '.card-title {'
    '    font-size: 16px !important;'
    '    font-weight: bold !important;'
    '    color: #222222 !important;'
    '    margin-bottom: 12px !important;'
    '    border-bottom: 1px solid #eeeeee;'
    '    padding-bottom: 6px;'
    '}'
    '.card-body {'
    '    font-size: 14px !important;'
    '    line-height: 1.6 !important;'
    '    color: #555555 !important;'
    '}'
    '.card-body ul {'
    '    margin: 0 !important;'
    '    padding-left: 20px !important;'
    '}'
    '.card-body li {'
    '    margin-bottom: 8px !important;'
    '}'
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

# 台股中文自訂對應字典
TW_ZH_NAMES = {
    "2330.TW": "台積電",
    "2454.TW": "聯發科",
    "2317.TW": "鴻海",
    "2308.TW": "台達電",
    "2382.TW": "廣達",
    "2603.TW": "長榮"
}

# 絕對鐵律縱向排版順序
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
    st.title("🎯 專屬台股戰略儀慢板：護國神山與半導體核心矩陣")
    default_tickers = "2330, 2454, 2317"
    currency_sign = "NT$"

# ==============================================================================
# 📋 【強勢重塑】：明日開盤冷酷執行中央清單 (全面採用單引號字串拼接，100% 免疫語法錯誤)
# ==============================================================================
st.markdown("---")
st.subheader("📋 明日開盤冷酷執行中央清單")

if market_choice == "🇺🇸 美股核心指揮部":
    col_exe1, col_exe2, col_exe3 = st.columns(3)
    with col_exe1:
        card_rklb = (
            '<div class="execution-card card-us-sell">'
            '<div class="card-title">🚀 RKLB (火箭實驗室) ── 獲利套現</div>'
            '<div class="card-body"><ul>'
            '<li><b>計畫動作：</b> 開盤前直接掛好 <b>$110.00 限價賣出 20 股</b>。</li>'
            '<li><b>戰略核心：</b> 鎖定 Nasdaq-100 指數基金搶跑吸籌的瘋狂動能，在半山腰優雅停盈，死死鎖定利潤並換回 <b>$2,200 現金彈藥</b>！</li>'
            '</ul></div></div>'
        )
        st.markdown(card_rklb, unsafe_allow_html=True)
    with col_exe2:
        card_nvda = (
            '<div class="execution-card card-us-buy">'
            '<div class="card-title">🔥 NVDA (輝達) ── 世紀抄底</div>'
            '<div class="card-body"><ul>'
            '<li><b>計畫動作：</b> 設定 TradingView 價格警報，跌至 <b>$185.00</b> 無情開槍。</li>'
            '<li><b>戰略核心：</b> 目前現價已實質跌穿河流圖打折區 ($254.54)，屬於非理性超跌。若觸及 $185 鐵板區，執行金字塔重倉建倉！</li>'
            '</ul></div></div>'
        )
        st.markdown(card_nvda, unsafe_allow_html=True)
    with col_exe3:
        card_aapl = (
            '<div class="execution-card card-us-info">'
            '<div class="card-title">🍏 AAPL (蘋果) ── 防禦分批</div>'
            '<div class="card-body"><ul>'
            '<li><b>計畫動作：</b> 跌至 <b>$270.00</b> 觸發時，僅投入低水位建立 <b>1 股偵察兵底倉</b>。</li>'
            '<li><b>戰略核心：</b> $270 剛好卡在合理中樞與技術鐵板的雙重共振點。合理不等於便宜，控制低水位，大部隊留給真正的價值打折區 ($211.09)！</li>'
            '</ul></div></div>'
        )
        st.markdown(card_aapl, unsafe_allow_html=True)
else:
    col_exe1, col_exe2 = st.columns(2)
    with col_exe1:
        card_tsmc = (
            '<div class="execution-card card-tw-warn">'
            '<div class="card-title">🇹🇼 2330 (台積電) ── 終極目標見頂</div>'
            '<div class="card-body"><ul>'
            '<li><b>計畫動作：</b> 現價已飆至高點，實質觸發戰略合理價。明早開盤緊盯 <b>NT$1200.00 (Sell)</b> 保守停盈防守線。</li>'
            '<li><b>戰略核心：</b> 持倉損益已高達 <b>+143.2% 🟢</b>！隨時做好跟蹤止損準備，絕不讓利潤坐過山車。</li>'
            '</ul></div></div>'
        )
        st.markdown(card_tsmc, unsafe_allow_html=True)
    with col_exe2:
        card_tw_semi = (
            '<div class="execution-card card-tw-warn">'
            '<div class="card-title">💡 台股半導體觀測 ── 靜態伏擊</div>'
            '<div class="card-body"><ul>'
            '<li><b>計畫動作：</b> 聯發科 (2454)、鴻海 (2317) 目前處於 <b>⏳ 靜態伏擊觀察中</b>。</li>'
            '<li><b>戰略核心：</b> 嚴格靜待它們拉回到河流圖價值打折區或 61.8% 黃金鐵板支撐區時，再行啟動無情開槍計劃。</li>'
            '</ul></div></div>'
        )
        st.markdown(card_tw_semi, unsafe_allow_html=True)

# ==============================================================================
# 🎛️ 【互動式左側控制艙】無代碼圖形化操作
# ==============================================================================
st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ 戰略中央控制艙")

ticker_input = st.sidebar.text_input("📊 輸入股票代碼 (用逗號隔開)", default_tickers, key=f"ticker_in_{market_choice}")
raw_tickers = list(dict.fromkeys([t.strip().upper() for t in ticker_input.split(",") if t.strip()]))

# 冷酷市場隔離盾：嚴格篩選市場代碼，不符合條件直接丟棄
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
            
        # 河流圖精準估值
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        
        preset = PE_PRESETS.get(ticker, None)
        if preset:
            low_pe
