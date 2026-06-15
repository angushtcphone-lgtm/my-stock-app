import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import datetime
import io
import random
import time

# 1. 網頁基礎設定
st.set_page_config(page_title="華爾街隱形力量 - 核心指標監控儀表板", layout="wide")
st.title("📊 核心指標與風險評估自動指引儀表板 (v2.0 - 隱蔽解鎖版)")
st.caption("即時時空背景：2026 年 6 月 FOMC 會議與美伊協議關鍵週")

# 【高級偽裝瀏覽器 Session】
@st.cache_resource
def get_stealth_session():
    session = requests.Session()
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'
    ]
    session.headers.update({
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://finance.yahoo.com/',
        'Connection': 'keep-alive'
    })
    return session

# 2. 保持監控清單狀態
if 'tickers' not in st.session_state:
    st.session_state.tickers = ["2330.TW", "MU"]

# 3. 側邊欄：管理系統
st.sidebar.header("🛠️ 監控清單管理")
new_ticker = st.sidebar.text_input("輸入股票代碼 (例如: NVDA, AAPL):").upper().strip()

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
    # 確保 columns 沒有層級衝突
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
        
    # 確保必要欄位名稱正確 (相容兩種下載管道)
    if 'Adj Close' in df.columns and 'Close' not in df.columns:
        df['Close'] = df['Adj Close']
    elif 'Adj Close' in df.columns:
        df['Close'] = df['Adj Close'] # 優先採用還原權值價
        
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    df['Is_Distribution'] = (df['Close'] < df['Close'].shift(1)) & (df['Volume'] > df['Vol_MA20'])
    return df

# 5. 主畫面：數據巡航
if not st.session_state.tickers:
    st.info("目前監控清單為空，請在左側側邊欄加入股票代碼。")
else:
    session = get_stealth_session()
    
    for ticker_symbol in st.session_state.tickers:
        st.subheader(f"🔍 標的分析：{ticker_symbol}")
        
        data = pd.DataFrame()
        
        # --- 雙軌數據抓取防線 ---
        # 軌道一：嘗試常態 yf.download 管道
        try:
            data = yf.download(tickers=ticker_symbol, period="4m", session=session, progress=False, auto_adjust=True)
        except Exception:
            pass
            
        # 軌道二：若常態管道失敗或被限流，立刻啟動【隱蔽式直連 CSV 串流技術】
        if data.empty or len(data) < 20:
            try:
                end_dt = datetime.datetime.now()
                start_dt = end_dt - datetime.timedelta(days=120) # 抓4個月確保均線精確
                p1 = int(start_dt.timestamp())
                p2 = int(end_dt.timestamp())
                
                # 直連 Yahoo 最底層的無腳印數據交換 URL
                stealth_url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker_symbol}?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true"
                
                resp = session.get(stealth_url, timeout=10)
                if resp.status_code == 200:
                    data = pd.read_csv(io.StringIO(resp.text), parse_dates=['Date'], index_col='Date')
            except Exception as e:
                st.error(f"備援管道發生異常: {e}")

        # --- 數據渲染與規則判定中心 ---
        if data.empty or len(data) < 20:
            st.error(f"❌ {ticker_symbol} 雙軌防線皆遭封鎖。請點擊右下角『Manage app』->『Reboot App』強制更換雲端節點 IP。")
            continue
            
        try:
            df = calculate_indicators(data)
            current_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            
            curr_price = float(current_row['Close'])
            curr_ema20 = float(current_row['EMA_20'])
            curr_rsi = float(current_row['RSI'])
            curr_vol = float(current_row['Volume'])
            ma20_vol = float(current_row['Vol_MA20'])
            dist_to_ema20 = ((curr_price - curr_ema20) / curr_ema20) * 100
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("最新收盤價", f"{curr_price:.2f}")
            m2.metric("最新 EMA 20 防線", f"{curr_ema20:.2f}")
            m3.metric("RSI (14D)", f"{curr_rsi:.1f}", delta=f"{curr_rsi - float(prev_row['RSI']):.1f}")
            m4.metric("距離 EMA 20 乖離率", f"{dist_to_ema20:.2f}%")
            
            st.markdown("##### 🚦 系統硬性規則動態指引")
            
            if bool(current_row['Is_Distribution']):
                st.error(f"🚨 警告：今日符合【分佈日】特徵！大戶有高檔減碼嫌疑（今日量: {curr_vol:,.0f} / 均量: {ma20_vol:,.0f}）。")
            else:
                st.success("💡 籌碼流向：今日未出現主力異常放量倒貨特徵。")
                
            if curr_rsi > 75:
                st.warning("❌ 【系統指引：極度超買區】RSI 破 75，高槓桿散戶瘋狂追價中。依據帳本鐵律，此時嚴禁追高建倉，保留現金。")
            elif dist_to_ema20 < 1.0 and dist_to_ema20 > -1.0:
                if curr_vol < ma20_vol * 0.85:
                    st.success("🔥 【系統指引：符合安全建倉條件】股價首次拉回且極度貼近 EMA 20，同時成交量出現【量極縮】。允許分批建立多頭倉位。")
                else:
                    st.warning("⚠️ 【系統指引：觀望不接刀】股價貼近 EMA 20 但成交量未縮，代表多空震盪激烈，需等待收盤前確認是否收長下影線。")
            elif curr_price < curr_ema20 and curr_vol > ma20_vol:
                st.error("🚨 【系統指引：趨勢破壞！多單停損】股價放量跌破 EMA 20 防線。主力成本底牌遭擊穿，嚴禁接刀，多單應執行停損。")
            else:
                st.info("🔵 【系統指引：常態趨勢區】目前股價處於常態波動區間，未觸及極端買賣點。請耐心等待回測或突破訊號。")
                
            st.markdown("---")
            
        except Exception as e:
            st.error(f"處理解析 {ticker_symbol} 時發生錯誤: {e}")
