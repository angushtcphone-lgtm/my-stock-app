import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="華爾街隱形力量 - 核心指標監控儀表板", layout="wide")
st.title("📊 核心指標與風險評估自動指引儀表板 (v1.7)")
st.caption("即時時空背景：2026 年 6 月 FOMC 會議與美伊協議關鍵週")

# 2. 利用 Streamlit 的 session_state 來保持監控清單的狀態
if 'tickers' not in st.session_state:
    # 預設初始化您最關心的兩檔指標股
    st.session_state.tickers = ["2330.TW", "MU"]

# 3. 側邊欄：動態 Ticker 管理系統
st.sidebar.header("🛠️ 監控清單管理")
new_ticker = st.sidebar.text_input("輸入股票代碼 (例如: NVDA, AAPL, 2454.TW):").upper().strip()

if st.sidebar.button("➕ 加入監控清單"):
    if new_ticker and new_ticker not in st.session_state.tickers:
        st.session_state.tickers.append(new_ticker)
        st.rerun()
    elif new_ticker in st.session_state.tickers:
        st.sidebar.warning("該股票已在監控清單中！")

st.sidebar.write("---")
st.sidebar.subheader("📌 當前監控中股票")
for t in st.session_state.tickers:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(f"**{t}**")
    if col2.button("🗑️", key=f"del_{t}"):
        st.session_state.tickers.remove(t)
        st.rerun()

# 4. 核心量化計算邏輯
def calculate_indicators(df):
    # 計算 EMA 20
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # 計算 RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 計算 20日平均成交量 (用來判定分佈日)
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    
    # 判定分佈日 (今日收盤價低於昨日，且成交量大於20日均量)
    df['Is_Distribution'] = (df['Close'] < df['Close'].shift(1)) & (df['Volume'] > df['Vol_MA20'])
    
    return df

# 5. 主畫面：巡航監控各檔股票
if not st.session_state.tickers:
    st.info("目前監控清單為空，請在左側側邊欄加入股票代碼。")
else:
    for ticker_symbol in st.session_state.tickers:
        st.subheader(f"🔍 標的分析：{ticker_symbol}")
        
        try:
            # 抓取最近 3 個月的歷史數據以確保均線精確度
            stock = yf.Ticker(ticker_symbol)
            data = stock.history(period="3m")
            
            if data.empty:
                st.error(f"無法取得 {ticker_symbol} 的數據，請檢查代碼是否正確（台股後綴需加 .TW）。")
                continue
                
            # 執行指標計算
            df = calculate_indicators(data)
            current_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            
            # 提取關鍵數據點
            curr_price = current_row['Close']
            curr_ema20 = current_row['EMA_20']
            curr_rsi = current_row['RSI']
            curr_vol = current_row['Volume']
            ma20_vol = current_row['Vol_MA20']
            
            # 計算距離 EMA 20 的百分比乖離
            dist_to_ema20 = ((curr_price - curr_ema20) / curr_ema20) * 100
            
            # 顯示看板核心數據
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("最新收盤價", f"{curr_price:.2f}")
            m2.metric("最新 EMA 20 防線", f"{curr_ema20:.2f}")
            m3.metric("RSI (14D)", f"{curr_rsi:.1f}", delta=f"{curr_rsi - prev_row['RSI']:.1f} (與昨日比)")
            m4.metric("距離 EMA 20 乖離率", f"{dist_to_ema20:.2f}%")
            
            # 6. 自動化硬性規則判定與實戰指引系統
            st.markdown("##### 🚦 系統硬性規則動態指引")
            
            # 判定分佈日狀態
            if current_row['Is_Distribution']:
                st.error(f"🚨 警告：今日符合【分佈日】特徵！股價下跌且成交量大於20日均量（今日量: {curr_vol:,.0f} / 均量: {ma20_vol:,.0f}）。華爾街主力有高檔倒貨嫌疑。")
            else:
                st.success("💡 籌碼流向：今日未出現主力異常放量倒貨特徵。")
                
            # 判定 EMA 20 買賣防線與 RSI 過熱度
            if curr_rsi > 75:
                st.warning("❌ 【系統指引：極度超買區】RSI 已突破 75 極端熱絡值，市場高槓桿散戶瘋狂追價。依據帳本鐵律，此時嚴禁追高建倉，請保留現金等待修正。")
                
            elif dist_to_ema20 < 1.0 and dist_to_ema20 > -1.0:
                # 股價極度接近 EMA 20
                if curr_vol < ma20_vol * 0.85:
                    st.success("🔥 【系統指引：符合安全建倉條件】股價首次拉回且極度貼近 EMA 20，同時成交量出現【量極縮】（低於均量 15% 以上）。此為回測成功訊號，主力並未倒貨，允許分批建立多頭倉位。")
                else:
                    st.warning("⚠️ 【系統指引：觀望不接刀】股價雖然貼近 EMA 20，但成交量並未萎縮，代表多空博弈劇烈。需等待收盤前確認是否留下長下影線，切勿盲目左側抄底。")
                    
            elif curr_price < curr_ema20 and current_row['Volume'] > ma20_vol:
                st.error("🚨 【系統指引：趨勢破壞！絕對禁買/多單停損】股價已放量跌破 EMA 20 防線。這代表主力的核心成本底牌已被無情擊穿，多頭趨勢可能轉空。嚴禁接刀，原有長線多單應嚴格執行停損或轉為全面觀望。")
                
            else:
                st.info("🔵 【系統指引：常態趨勢區】目前股價處於常態波動區間，未觸及極端過熱或核心防線買點。請遵循交易 SOP 流程，耐心等待回測 EMA 20 的時機。")
                
            st.markdown("---")
            
        except Exception as e:
            st.error(f"處理解析 {ticker_symbol} 時發生錯誤: {e}")
