import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="機構級全球決策終端", layout="wide")

# ==============================================================================
# 🎨 【終極美學】注入頂級金融終端專專屬 CSS 樣式表，鎖定字體、排版與滾動條
# ==============================================================================
st.markdown(
    """
    <style>
    /* 修正側邊欄滾動條 Bug */
    [data-testid="stSidebarUserContent"] {
        overflow-y: auto !important;
        max-height: 90vh !important;
    }
    
    /* 自訂機構級極簡戰略卡片樣式：徹底根除字體不一、超版面溢出與打架問題 */
    .execution-container {
        display: flex;
        gap: 20px;
        margin-bottom: 25px;
        width: 100%;
    }
    .execution-card {
        flex: 1;
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-top: 5px solid #d4d4d4;
        min-width: 250px;
    }
    .card-us-sell { border-top-color: #ff4b4b; background-color: #fffafb; }
    .card-us-buy { border-top-color: #00cc66; background-color: #f7fdf9; }
    .card-us-info { border-top-color: #0066cc; background-color: #f7faff; }
    .card-tw-warn { border-top-color: #ffaa00; background-color: #fffdf5; }
    
    .card-title {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #222222 !important;
        margin-bottom: 12px !important;
        border-bottom: 1px solid #eeeeee;
        padding-bottom: 6px;
    }
    .card-body {
        font-size: 14px !important;
        line-height: 1.6 !important;
        color: #555555 !important;
    }
    .card-body ul {
        margin: 0 !important;
        padding-left: 20px !important;
    }
    .card-body li {
        margin-bottom: 8px !important;
    }
    </style>
    """,
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
    st.title("🎯 專屬台股戰略儀表板：護國神山與半導體核心矩陣")
    default_tickers = "2330, 2454, 2317"
    currency_sign = "NT$"

# ==============================================================================
# 📋 【強勢重塑】：明日開盤冷酷執行中央清單 (純 HTML 自訂卡片，100% 根除過期殘留)
# ==============================================================================
st.markdown("---")
st.subheader("📋 明日開盤冷酷執行中央清單")

if market_choice == "🇺🇸 美股核心指揮部":
    st.markdown("""
    <div class="execution-container">
        <div class="execution-card card-us-sell">
            <div class="card-title">🚀 RKLB (火箭實驗室) ── 獲利套現</div>
            <div class="card-body">
                <ul>
                    <li><b>計畫動作：</b> 開盤前直接
